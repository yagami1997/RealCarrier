"""
Twilio API客户端模块 - 负责与Twilio API的通信和响应处理
实现LookupProvider接口，提供标准化的号码查询功能
"""

import time
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
import threading
import functools

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException
import keyring

from .provider import (
    LookupProvider, LookupResult, LookupError, 
    ConfigurationError, AuthenticationError, 
    RateLimitError, NetworkError
)

# API常量
API_BASE_URL = "https://lookups.twilio.com/v1/PhoneNumbers"
DEFAULT_TIMEOUT = 10  # 秒
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒
RETRY_BACKOFF_FACTOR = 0.5
RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]

# 速率限制配置
RATE_LIMIT_REQUESTS = 10  # 每秒最大请求数
RATE_LIMIT_WINDOW = 1.0  # 窗口大小（秒）

# 配置日志
logger = logging.getLogger('twilio_api')

# 常量定义
TWILIO_KEYRING_SERVICE = "realcarrier-twilio-api"
TWILIO_ACCOUNT_SID_USERNAME = "twilio-account-sid"
TWILIO_AUTH_TOKEN_USERNAME = "twilio-auth-token"


class TwilioAPI(LookupProvider):
    """Twilio API客户端，实现 LookupProvider 接口"""
    
    # 类级别的会话对象，用于所有实例共享
    _shared_session = None
    _session_lock = threading.Lock()
    
    def __init__(self):
        """初始化 Twilio API 客户端"""
        super().__init__()  # 初始化父类
        self.account_sid, self.auth_token = self._get_credentials_from_keyring()
        self.session = self._get_or_create_session()
        self._rate_limit_lock = threading.Lock()
        self._rate_limit_tokens = RATE_LIMIT_REQUESTS
        self._rate_limit_last_check = time.time()
        # 设置缓存TTL为1天
        self.set_cache_ttl(86400)
    
    def _get_or_create_session(self) -> requests.Session:
        """
        获取或创建共享会话
        
        Returns:
            requests.Session: 配置好的会话对象
        """
        with self._session_lock:
            if TwilioAPI._shared_session is None or not self._is_session_valid(TwilioAPI._shared_session):
                TwilioAPI._shared_session = self._create_session()
                logger.debug("创建新的共享会话")
            return TwilioAPI._shared_session
    
    def _is_session_valid(self, session: requests.Session) -> bool:
        """
        检查会话是否有效
        
        Args:
            session: 要检查的会话
            
        Returns:
            bool: 如果会话有效返回True，否则返回False
        """
        # 检查会话是否已关闭（安全地检查closed属性）
        try:
            if hasattr(session, 'closed') and session.closed:
                return False
        except Exception:
            # 如果访问closed属性出错，认为会话无效
            return False
        
        # 检查认证信息是否匹配
        if hasattr(session, 'auth'):
            current_auth = session.auth
            if current_auth is None and (self.account_sid and self.auth_token):
                return False
            if current_auth is not None and (current_auth[0] != self.account_sid or current_auth[1] != self.auth_token):
                return False
        
        return True
    
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
        
        # 配置认证
        if self.account_sid and self.auth_token:
            session.auth = (self.account_sid, self.auth_token)
        
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
                logger.debug(f"速率限制达到，等待 {wait_time:.2f} 秒")
                time.sleep(wait_time)
                self._rate_limit_tokens = 1
            
            # 消耗一个令牌
            self._rate_limit_tokens -= 1
    
    @functools.lru_cache(maxsize=128)
    def _cached_lookup(self, phone_number: str) -> LookupResult:
        """
        带内存缓存的查询函数
        
        Args:
            phone_number: 要查询的电话号码
            
        Returns:
            LookupResult: 查询结果
            
        Raises:
            各种异常: 与lookup_number相同
        """
        # 这个函数的实现与lookup_number相同，但使用了functools.lru_cache装饰器
        # 实际的查询逻辑在_do_lookup中实现
        return self._do_lookup(phone_number)
    
    def _do_lookup(self, phone_number: str) -> LookupResult:
        """
        执行实际的查询操作
        
        Args:
            phone_number: 要查询的电话号码
            
        Returns:
            LookupResult: 查询结果
            
        Raises:
            各种异常: 与lookup_number相同
        """
        logger.info(f"查询号码: {phone_number}")
        
        if not self.is_configured():
            logger.error("Twilio API 凭据未配置")
            raise ConfigurationError("Twilio API 凭据未配置", self.get_provider_name(), None)
        
        # 验证并格式化电话号码
        try:
            formatted_number = self.validate_phone_number(phone_number)
            logger.debug(f"格式化号码: {formatted_number}")
        except ValueError as e:
            logger.error(f"无效的电话号码格式: {phone_number}")
            raise LookupError(f"无效的电话号码格式: {e}", self.get_provider_name(), None)
        
        # 构建请求URL和参数
        url = f"{API_BASE_URL}/{formatted_number}"
        params = {
            "Type": "carrier"
        }
        
        try:
            # 应用速率限制
            self._check_rate_limit()
            
            # 发送请求
            logger.debug(f"发送请求到: {url}")
            response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            
            # 检查认证错误
            if response.status_code == 401:
                logger.error("Twilio API 认证失败")
                raise AuthenticationError("无效的账户SID或认证令牌", self.get_provider_name(), response.json())
            
            # 检查速率限制错误
            if response.status_code == 429:
                logger.error("Twilio API 速率限制超出")
                retry_after = int(response.headers.get('Retry-After', 60))
                raise RateLimitError(f"速率限制超出，请在 {retry_after} 秒后重试", self.get_provider_name(), response.json())
            
            # 检查号码不存在错误
            if response.status_code == 404:
                logger.warning(f"号码不存在: {phone_number}")
                raise LookupError(f"号码不存在或格式无效", self.get_provider_name(), None)
            
            # 检查其他错误
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            # 从响应中提取数据
            result = self._parse_response(data, formatted_number)
            logger.info(f"成功查询号码: {phone_number}")
            
            return result
            
        except RequestException as e:
            logger.error(f"请求错误: {e}")
            raise NetworkError(f"连接到 Twilio API 失败: {e}", self.get_provider_name(), None)
        except ValueError as e:
            logger.error(f"响应解析错误: {e}")
            raise LookupError(f"解析 Twilio API 响应失败: {e}", self.get_provider_name(), None)
        except Exception as e:
            logger.error(f"意外错误: {e}")
            raise
    
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
        # 检查持久化缓存
        if use_cache:
            cached_result = self.get_from_cache(phone_number)
            if cached_result:
                logger.debug(f"持久化缓存命中: {phone_number}")
                return cached_result
        
        # 使用内存缓存或执行查询
        try:
            if use_cache:
                result = self._cached_lookup(phone_number)
            else:
                # 清除内存缓存
                self._cached_lookup.cache_clear()
                result = self._do_lookup(phone_number)
            
            # 添加到持久化缓存
            if use_cache:
                self.add_to_cache(result)
            
            return result
        except Exception as e:
            # 如果查询失败，清除内存缓存
            self._cached_lookup.cache_clear()
            raise
    
    def get_provider_name(self) -> str:
        """
        获取提供商名称
        
        Returns:
            str: 提供商名称
        """
        return "Twilio"
    
    def is_configured(self) -> bool:
        """
        检查提供商是否已配置
        
        Returns:
            bool: 如果提供商已配置返回True，否则返回False
        """
        return bool(self.account_sid and self.auth_token)
    
    def get_provider_features(self) -> Dict[str, bool]:
        """
        获取提供商支持的功能
        
        Returns:
            Dict[str, bool]: 功能名称和支持状态的字典
        """
        features = super().get_provider_features()
        # Twilio 不支持批量查询
        features["batch_lookup"] = False
        return features
    
    def _get_credentials_from_keyring(self) -> Tuple[Optional[str], Optional[str]]:
        """
        从系统密钥环获取 Twilio 凭据
        
        Returns:
            Tuple[Optional[str], Optional[str]]: 账户SID和认证令牌
        """
        try:
            account_sid = keyring.get_password(TWILIO_KEYRING_SERVICE, TWILIO_ACCOUNT_SID_USERNAME)
            auth_token = keyring.get_password(TWILIO_KEYRING_SERVICE, TWILIO_AUTH_TOKEN_USERNAME)
            return account_sid, auth_token
        except Exception as e:
            logger.error(f"从密钥环获取 Twilio 凭据失败: {e}")
            return None, None
    
    def _parse_response(self, response_data: Dict[str, Any], phone_number: str) -> LookupResult:
        """
        解析 Twilio API 响应
        
        Args:
            response_data: API 响应数据
            phone_number: 查询的电话号码
            
        Returns:
            LookupResult: 解析后的查询结果
            
        Raises:
            ValueError: 如果响应格式无效
        """
        if not response_data:
            raise ValueError("空响应")
        
        # 提取运营商信息
        carrier_data = response_data.get("carrier", {})
        
        # 检查运营商错误
        if carrier_data and "error_code" in carrier_data and carrier_data["error_code"]:
            error_msg = carrier_data.get("error_code")
            logger.error(f"Twilio API 运营商错误: {error_msg}")
            raise LookupError(f"Twilio API 运营商错误: {error_msg}", self.get_provider_name(), response_data)
        
        carrier_name = carrier_data.get("name")
        carrier_type = carrier_data.get("type")
        
        # 提取位置信息
        country_code = response_data.get("country_code")
        
        # 创建结果对象
        result = LookupResult(
            phone_number=phone_number,
            carrier=carrier_name,
            carrier_type=carrier_type,
            line_type=self._map_line_type(carrier_type),
            provider=self.get_provider_name(),
            raw_data=response_data
        )
        
        return result
    
    def _map_line_type(self, carrier_type: Optional[str]) -> Optional[str]:
        """
        将 Twilio 运营商类型映射到标准线路类型
        
        Args:
            carrier_type: Twilio 运营商类型
            
        Returns:
            str: 标准线路类型
        """
        if not carrier_type:
            return None
        
        # Twilio 使用的类型: mobile, landline, voip
        # 我们的标准类型: mobile, landline, voip, unknown
        carrier_type = carrier_type.lower()
        
        if carrier_type in ["mobile", "landline", "voip"]:
            return carrier_type
        
        return "unknown"


def set_credentials(account_sid: str, auth_token: str) -> bool:
    """
    设置 Twilio API 凭据
    
    Args:
        account_sid: Twilio 账户 SID
        auth_token: Twilio 认证令牌
        
    Returns:
        bool: 如果设置成功返回True，否则返回False
    """
    try:
        # 验证凭据格式
        if not account_sid or not isinstance(account_sid, str):
            logger.error("无效的账户 SID")
            return False
        
        if not auth_token or not isinstance(auth_token, str):
            logger.error("无效的认证令牌")
            return False
        
        # 存储凭据到系统密钥环
        keyring.set_password(TWILIO_KEYRING_SERVICE, TWILIO_ACCOUNT_SID_USERNAME, account_sid)
        keyring.set_password(TWILIO_KEYRING_SERVICE, TWILIO_AUTH_TOKEN_USERNAME, auth_token)
        
        logger.info("Twilio API 凭据已保存")
        return True
    except Exception as e:
        logger.error(f"保存 Twilio API 凭据失败: {e}")
        return False


def delete_credentials() -> bool:
    """
    删除 Twilio API 凭据
    
    Returns:
        bool: 如果删除成功返回True，否则返回False
    """
    try:
        keyring.delete_password(TWILIO_KEYRING_SERVICE, TWILIO_ACCOUNT_SID_USERNAME)
        keyring.delete_password(TWILIO_KEYRING_SERVICE, TWILIO_AUTH_TOKEN_USERNAME)
        logger.info("Twilio API 凭据已删除")
        return True
    except Exception as e:
        logger.error(f"删除 Twilio API 凭据失败: {e}")
        return False


def verify_credentials(account_sid: str, auth_token: str) -> Dict[str, Any]:
    """
    验证 Twilio API 凭据
    
    Args:
        account_sid: Twilio 账户 SID
        auth_token: Twilio 认证令牌
        
    Returns:
        Dict[str, Any]: 包含验证结果的字典
    """
    # 创建临时会话
    session = requests.Session()
    session.auth = (account_sid, auth_token)
    
    # 构建请求URL和参数（使用基础URL验证，而不是查询具体号码）
    url = "https://lookups.twilio.com/v1/PhoneNumbers"
    
    try:
        # 发送请求
        response = session.get(url, timeout=DEFAULT_TIMEOUT)
        
        # 检查认证错误
        if response.status_code == 401:
            return {
                "valid": False,
                "message": "无效的账户SID或认证令牌"
            }
        
        # 如果能访问API（返回200或404），说明凭据有效
        if response.status_code in [200, 404]:
            return {
                "valid": True,
                "message": "Twilio API 凭据有效"
            }
        
        return {
            "valid": False,
            "message": f"API 请求失败: {response.status_code} - {response.text}"
        }
    except RequestException as e:
        return {
            "valid": False,
            "message": f"连接到 Twilio API 失败: {e}"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"验证 Twilio API 凭据失败: {e}"
        }


def check_credentials_status() -> Dict[str, Any]:
    """
    检查 Twilio API 凭据状态
    
    Returns:
        Dict[str, Any]: 包含状态信息的字典
    """
    try:
        # 从密钥环获取凭据
        account_sid = keyring.get_password(TWILIO_KEYRING_SERVICE, TWILIO_ACCOUNT_SID_USERNAME)
        auth_token = keyring.get_password(TWILIO_KEYRING_SERVICE, TWILIO_AUTH_TOKEN_USERNAME)
        
        # 检查凭据是否存在
        if not account_sid or not auth_token:
            return {
                "configured": False,
                "message": "Twilio API 凭据未配置",
                "account_sid": None,
                "auth_token": None
            }
        
        # 掩码处理凭据
        masked_account_sid = f"{account_sid[:4]}...{account_sid[-4:]}" if len(account_sid) > 8 else "****"
        masked_auth_token = f"{auth_token[:2]}...{auth_token[-2:]}" if len(auth_token) > 4 else "****"
        
        # 验证凭据有效性
        result = verify_credentials(account_sid, auth_token)
        
        if result["valid"]:
            return {
                "configured": True,
                "valid": True,
                "message": "Twilio API 凭据有效",
                "account_sid": masked_account_sid,
                "auth_token": masked_auth_token
            }
        else:
            return {
                "configured": True,
                "valid": False,
                "message": result["message"],
                "account_sid": masked_account_sid,
                "auth_token": masked_auth_token
            }
            
    except Exception as e:
        logger.error(f"检查 Twilio API 凭据状态失败: {e}")
        return {
            "configured": False,
            "message": f"检查 Twilio API 凭据状态失败: {e}",
            "account_sid": None,
            "auth_token": None
        } 