"""
Telnyx API客户端模块 - 负责与Telnyx API的通信和响应处理
实现LookupProvider接口，提供标准化的号码查询功能
"""

import time
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
import threading

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pydantic import BaseModel, Field
import keyring
from requests.exceptions import RequestException

from .provider import (
    LookupProvider, LookupResult, LookupError, 
    ConfigurationError, AuthenticationError, 
    RateLimitError, NetworkError
)
from lnptool.i18n import t

# API常量
API_BASE_URL = "https://api.telnyx.com/v2"
NUMBER_LOOKUP_ENDPOINT = "/number_lookup/{phone_number}"
BATCH_LOOKUP_ENDPOINT = "/number_lookup"

# 默认请求配置
DEFAULT_TIMEOUT = 10  # 秒
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒
RETRY_BACKOFF_FACTOR = 0.5
RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]

# 速率限制配置
RATE_LIMIT_REQUESTS = 10  # 每秒最大请求数
RATE_LIMIT_WINDOW = 1.0  # 窗口大小（秒）

# 配置日志
logger = logging.getLogger('telnyx_api')

# 常量定义
TELNYX_KEYRING_SERVICE = "realcarrier-telnyx-api"
TELNYX_KEYRING_USERNAME = "telnyx-api-key"


class CarrierInfo(BaseModel):
    """运营商信息数据模型"""
    name: str = Field(..., description="运营商名称")
    type: str = Field(..., description="号码类型 (mobile, landline, voip等)")
    mobile_country_code: Optional[str] = Field(None, description="移动国家代码")
    mobile_network_code: Optional[str] = Field(None, description="移动网络代码")


class PortabilityInfo(BaseModel):
    """携号转网信息数据模型"""
    portable: bool = Field(..., description="是否可携号转网")
    ported: bool = Field(False, description="是否已携号转网")
    spid: Optional[str] = Field(None, description="服务商ID")
    ocn: Optional[str] = Field(None, description="运营商代码")
    previous_carrier: Optional[CarrierInfo] = Field(None, description="前一个运营商")


class TelnyxLookupResponse(BaseModel):
    """Telnyx查询响应数据模型"""
    phone_number: str = Field(..., description="电话号码")
    country_code: str = Field(..., description="国家代码")
    carrier: CarrierInfo = Field(..., description="当前运营商")
    portability: Optional[PortabilityInfo] = Field(None, description="携号转网信息")
    status: str = Field(..., description="查询状态")
    request_id: Optional[str] = Field(None, description="请求ID")


class TelnyxAPI(LookupProvider):
    """Telnyx API客户端，实现 LookupProvider 接口"""
    
    def __init__(self):
        """初始化 Telnyx API 客户端"""
        super().__init__()  # 初始化父类
        self.api_key = self._get_api_key_from_keyring()
        self.session = self._create_session()
        self._rate_limit_lock = threading.Lock()
        self._rate_limit_tokens = RATE_LIMIT_REQUESTS
        self._rate_limit_last_check = time.time()
        self._batch_size = 10  # 批量查询的最大号码数
    
    def _create_session(self) -> requests.Session:
        """
        创建并配置请求会话
        
        Returns:
            requests.Session: 配置好的会话对象
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_FORCELIST,
            allowed_methods=["GET", "POST"]
        )
        
        # 配置适配器
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        # 配置请求头
        if self.api_key:
            session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
        
        return session
    
    def _check_rate_limit(self) -> None:
        """
        检查并应用速率限制
        如果超出速率限制，会阻塞直到有可用的令牌
        """
        with self._rate_limit_lock:
            current_time = time.time()
            time_passed = current_time - self._rate_limit_last_check
            
            # 添加新令牌
            self._rate_limit_tokens = min(
                RATE_LIMIT_REQUESTS,
                self._rate_limit_tokens + time_passed * (RATE_LIMIT_REQUESTS / RATE_LIMIT_WINDOW)
            )
            
            # 更新最后检查时间
            self._rate_limit_last_check = current_time
            
            # 如果没有足够的令牌，等待
            if self._rate_limit_tokens < 1:
                # 计算需要等待的时间
                wait_time = (1 - self._rate_limit_tokens) * (RATE_LIMIT_WINDOW / RATE_LIMIT_REQUESTS)
                logger.debug(f"Rate limit reached, waiting for {wait_time:.2f} seconds")
                time.sleep(wait_time)
                self._rate_limit_tokens = 1
            
            # 消耗一个令牌
            self._rate_limit_tokens -= 1
    
    def lookup_number(self, phone_number: str, use_cache: bool = True) -> LookupResult:
        """
        查询电话号码信息
        
        Args:
            phone_number: 要查询的电话号码
            use_cache: 是否使用缓存
            
        Returns:
            LookupResult: 查询结果
            
        Raises:
            ConfigurationError: 提供商未正确配置
            AuthenticationError: 认证失败
            RateLimitError: 超出API速率限制
            NetworkError: 网络连接错误
            LookupError: 其他查询错误
        """
        logger.info(f"Looking up number: {phone_number}")
        
        # 检查缓存
        if use_cache:
            cached_result = self.get_from_cache(phone_number)
            if cached_result:
                logger.debug(f"Cache hit for number: {phone_number}")
                return cached_result
        
        if not self.is_configured():
            logger.error("Telnyx API key not configured")
            raise ConfigurationError("Telnyx API key not configured", self.get_provider_name(), None)
        
        # 验证并格式化电话号码
        try:
            formatted_number = self.validate_phone_number(phone_number)
            logger.debug(f"Formatted number: {formatted_number}")
        except ValueError as e:
            logger.error(f"Invalid phone number format: {phone_number}")
            raise LookupError(f"Invalid phone number format: {e}", self.get_provider_name(), None)
        
        # 构建请求URL和参数
        url = f"{API_BASE_URL}{NUMBER_LOOKUP_ENDPOINT.format(phone_number=formatted_number)}"
        params = {
            "type": "carrier"
        }
        
        try:
            # 应用速率限制
            self._check_rate_limit()
            
            # 发送请求
            logger.debug(f"Sending request to: {url}")
            response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            
            # 检查认证错误
            if response.status_code == 401:
                logger.error("Authentication failed with Telnyx API")
                raise AuthenticationError("Invalid API key or unauthorized access", self.get_provider_name(), response)
            
            # 检查其他错误
            if response.status_code == 403:
                error_msg = t("error_telnyx_403")
                logger.error(f"Telnyx API authorization error: {response.status_code}")
                raise LookupError(error_msg, self.get_provider_name(), None)
            elif response.status_code != 200:
                logger.error(f"Telnyx API error: {response.status_code} - {response.text}")
                raise LookupError(f"Failed to connect to Telnyx API: {response.status_code} {response.reason} for url: {url}", self.get_provider_name(), None)
            
            # 解析响应
            data = response.json()
            
            # 检查响应是否包含错误
            if "errors" in data:
                error_msg = data["errors"][0].get("detail", "Unknown error")
                logger.error(f"Telnyx API returned error: {error_msg}")
                raise LookupError(f"Telnyx API error: {error_msg}", self.get_provider_name(), data)
            
            # 从响应中提取数据
            result = self._parse_response(data, formatted_number)
            logger.info(f"Successfully looked up number: {phone_number}")
            return result
            
        except RequestException as e:
            logger.error(f"Request error: {e}")
            raise LookupError(f"Failed to connect to Telnyx API: {e}", self.get_provider_name(), None)
        except ValueError as e:
            logger.error(f"Response parsing error: {e}")
            raise LookupError(f"Failed to parse Telnyx API response: {e}", self.get_provider_name(), None)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def get_provider_name(self) -> str:
        """
        获取提供商名称
        
        Returns:
            str: 提供商名称
        """
        return "Telnyx"
    
    def is_configured(self) -> bool:
        """
        检查提供商是否已配置
        
        Returns:
            bool: 如果提供商已配置返回True，否则返回False
        """
        return self.api_key is not None and len(self.api_key) > 0
    
    def get_provider_features(self) -> Dict[str, bool]:
        """
        获取提供商支持的功能
        
        Returns:
            Dict[str, bool]: 功能名称和支持状态的字典
        """
        return {
            "line_type": True,
            "portability": True,
            "carrier_details": True,
            "location": True
        }
    
    def _get_api_key_from_keyring(self) -> Optional[str]:
        """
        从系统密钥环获取 API 密钥
        
        Returns:
            Optional[str]: API 密钥，如果未配置返回 None
        """
        try:
            api_key = keyring.get_password(TELNYX_KEYRING_SERVICE, TELNYX_KEYRING_USERNAME)
            return api_key
        except Exception as e:
            logger.error(f"Failed to get API key from keyring: {e}")
            return None
    
    def _parse_response(self, response_data: Dict[str, Any], phone_number: str) -> LookupResult:
        """
        解析 Telnyx API 响应，转换为标准 LookupResult
        
        Args:
            response_data: API 响应数据
            phone_number: 查询的电话号码
            
        Returns:
            LookupResult: 解析后的查询结果
        """
        # 提取数据对象
        data = response_data.get("data", {})
        
        # 提取运营商信息
        carrier_info = data.get("carrier", {})
        
        # 提取城市和州信息
        city = carrier_info.get("city")
        state = carrier_info.get("state")
        
        # 提取线路类型
        line_type = self._map_line_type(carrier_info.get("type"))
        
        # 创建标准查询结果
        result = LookupResult(
            phone_number=phone_number,
            carrier=carrier_info.get("name"),
            carrier_type=carrier_info.get("type"),
            portable=data.get("portability", {}).get("portable"),
            city=city,
            state=state,
            rate_center=carrier_info.get("rate_center"),
            lata=carrier_info.get("lata"),
            line_type=line_type,
            provider=self.get_provider_name(),
            raw_data=response_data
        )
        
        return result
    
    def _map_line_type(self, carrier_type: Optional[str]) -> Optional[str]:
        """
        将 Telnyx 运营商类型映射到标准线路类型
        
        Args:
            carrier_type: Telnyx 运营商类型
            
        Returns:
            Optional[str]: 标准线路类型 (mobile, landline, voip, unknown)
        """
        if not carrier_type:
            return None
            
        carrier_type = carrier_type.lower()
        
        if carrier_type == "mobile":
            return "mobile"
        elif carrier_type == "landline":
            return "landline"
        elif carrier_type in ["voip", "voip_provider"]:
            return "voip"
        else:
            return "unknown"


# 辅助函数

def set_api_key(api_key: str) -> bool:
    """
    设置 Telnyx API 密钥
    
    Args:
        api_key: API 密钥
        
    Returns:
        bool: 如果设置成功返回 True，否则返回 False
    """
    try:
        keyring.set_password(TELNYX_KEYRING_SERVICE, TELNYX_KEYRING_USERNAME, api_key)
        logger.info("Telnyx API key stored successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to store Telnyx API key: {e}")
        return False


def delete_api_key() -> bool:
    """
    删除存储的 Telnyx API 密钥
    
    Returns:
        bool: 如果删除成功返回 True，否则返回 False
    """
    try:
        keyring.delete_password(TELNYX_KEYRING_SERVICE, TELNYX_KEYRING_USERNAME)
        logger.info("Telnyx API key deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to delete Telnyx API key: {e}")
        return False


def check_api_key_status() -> Dict[str, Any]:
    """
    检查 Telnyx API 密钥状态
    
    Returns:
        Dict[str, Any]: 包含 API 密钥状态信息的字典
    """
    try:
        api_key = keyring.get_password(TELNYX_KEYRING_SERVICE, TELNYX_KEYRING_USERNAME)
        
        if not api_key:
            return {
                "configured": False,
                "message": "API key not configured",
                "masked_key": None
            }
        
        # 创建掩码版本的 API 密钥
        masked_key = f"{'*' * (len(api_key) - 4)}{api_key[-4:]}" if len(api_key) > 4 else "****"
        
        return {
            "configured": True,
            "message": "API key configured",
            "masked_key": masked_key
        }
    except Exception as e:
        logger.error(f"Failed to check API key status: {e}")
        return {
            "configured": False,
            "message": f"Error checking API key: {e}",
            "masked_key": None
        }


def verify_api_key(api_key: str) -> Dict[str, Any]:
    """
    验证 Telnyx API 密钥
    
    Args:
        api_key: 要验证的 API 密钥
        
    Returns:
        Dict[str, Any]: 包含验证结果的字典
    """
    # 创建临时会话
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })
    
    # 测试号码
    test_number = "+12025550142"  # 美国华盛顿特区的测试号码
    
    try:
        # 发送测试请求
        url = f"{API_BASE_URL}{NUMBER_LOOKUP_ENDPOINT.format(phone_number=test_number)}"
        response = session.get(url, params={"type": "carrier"}, timeout=DEFAULT_TIMEOUT)
        
        # 检查响应状态
        if response.status_code == 200:
            return {
                "valid": True,
                "message": "API key verified successfully"
            }
        elif response.status_code == 401:
            return {
                "valid": False,
                "message": "Invalid API key"
            }
        else:
            return {
                "valid": False,
                "message": f"API verification failed with status code: {response.status_code}"
            }
    except Exception as e:
        logger.error(f"API key verification error: {e}")
        return {
            "valid": False,
            "message": f"API verification error: {e}"
        }
