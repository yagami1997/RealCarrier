"""
Telnyx API客户端模块 - 负责与Telnyx API的通信和响应处理
"""

import time
import logging
from typing import Dict, Any, Optional, TypedDict, Union

import requests
from requests.exceptions import RequestException, Timeout
from pydantic import BaseModel, Field

from lnptool.config import get_api_key

# API常量
API_BASE_URL = "https://api.telnyx.com/v2"
NUMBER_LOOKUP_ENDPOINT = "/number_lookup/{phone_number}"

# 默认请求配置
DEFAULT_TIMEOUT = 10  # 秒
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒

logger = logging.getLogger(__name__)


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


class LookupResult(BaseModel):
    """查询结果数据模型"""
    phone_number: str = Field(..., description="电话号码")
    country_code: str = Field(..., description="国家代码")
    carrier: CarrierInfo = Field(..., description="当前运营商")
    portability: Optional[PortabilityInfo] = Field(None, description="携号转网信息")
    status: str = Field(..., description="查询状态")
    lookup_time: float = Field(..., description="查询时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")


class APIError(Exception):
    """Telnyx API错误异常"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Any = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class TelnyxAPI:
    """Telnyx API客户端"""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """
        初始化Telnyx API客户端
        
        Args:
            api_key: Telnyx API密钥，如未提供则从配置中获取
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key or get_api_key()
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning("No API key provided or found in configuration")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        处理API响应
        
        Args:
            response: Requests响应对象
            
        Returns:
            Dict[str, Any]: 解析后的响应JSON
            
        Raises:
            APIError: 如果响应包含错误
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            error_msg = f"HTTP Error: {e}"
            try:
                error_data = response.json()
                if "errors" in error_data and error_data["errors"]:
                    error_msg = f"{error_msg} - {error_data['errors'][0].get('detail', '')}"
            except (ValueError, KeyError):
                pass
            
            logger.error(f"API request failed: {error_msg}")
            raise APIError(error_msg, response.status_code, response.text)
        except ValueError:
            error_msg = "Invalid JSON in response"
            logger.error(error_msg)
            raise APIError(error_msg, response.status_code, response.text)
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                     data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            method: HTTP方法 ('GET', 'POST', 等)
            endpoint: API端点
            params: URL参数
            data: 请求体数据
            
        Returns:
            Dict[str, Any]: 解析后的响应JSON
            
        Raises:
            APIError: 如果请求失败
        """
        url = f"{API_BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        if not self.api_key:
            raise APIError("API key is required. Please configure it first.")
        
        # 重试逻辑
        retries = 0
        while retries <= MAX_RETRIES:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )
                return self._handle_response(response)
            
            except (RequestException, Timeout) as e:
                retries += 1
                if retries > MAX_RETRIES:
                    logger.error(f"Request failed after {MAX_RETRIES} retries: {e}")
                    raise APIError(f"Request failed: {e}")
                
                logger.warning(f"Request attempt {retries} failed, retrying: {e}")
                time.sleep(RETRY_DELAY * retries)  # 指数退避
    
    def lookup_number(self, phone_number: str) -> LookupResult:
        """
        查询电话号码信息
        
        Args:
            phone_number: 电话号码，格式为E.164 (+1XXXXXXXXXX)
            
        Returns:
            LookupResult: 查询结果
            
        Raises:
            APIError: 如果查询失败
        """
        # 格式化电话号码
        formatted_number = self._format_phone_number(phone_number)
        
        endpoint = NUMBER_LOOKUP_ENDPOINT.format(phone_number=formatted_number)
        params = {"type": "carrier"}
        
        start_time = time.time()
        try:
            response = self._make_request("GET", endpoint, params=params)
            
            # 提取数据并创建结果对象
            data = response.get("data", {})
            
            carrier_data = data.get("carrier", {})
            if not isinstance(carrier_data, dict):
                carrier_data = {}
            
            # 确保carrier字段数据类型正确
            carrier_name = carrier_data.get("name", "Unknown")
            if not isinstance(carrier_name, str):
                carrier_name = str(carrier_name) if carrier_name is not None else "Unknown"
                
            carrier_type = carrier_data.get("type", "Unknown")
            if not isinstance(carrier_type, str):
                carrier_type = str(carrier_type) if carrier_type is not None else "Unknown"
                
            carrier_mcc = carrier_data.get("mobile_country_code")
            if carrier_mcc is not None and not isinstance(carrier_mcc, str):
                carrier_mcc = str(carrier_mcc)
                
            carrier_mnc = carrier_data.get("mobile_network_code")
            if carrier_mnc is not None and not isinstance(carrier_mnc, str):
                carrier_mnc = str(carrier_mnc)
                
            carrier = CarrierInfo(
                name=carrier_name,
                type=carrier_type,
                mobile_country_code=carrier_mcc,
                mobile_network_code=carrier_mnc
            )
            
            portability_data = data.get("portability", {})
            # 确保portability_data是字典类型
            if not isinstance(portability_data, dict):
                portability_data = {}
                
            previous_carrier_data = portability_data.get("previous_carrier", {})
            # 确保previous_carrier_data是字典类型
            if not isinstance(previous_carrier_data, dict):
                previous_carrier_data = {}
            
            previous_carrier = None
            if previous_carrier_data:
                prev_name = previous_carrier_data.get("name", "Unknown")
                if not isinstance(prev_name, str):
                    prev_name = str(prev_name) if prev_name is not None else "Unknown"
                    
                prev_type = previous_carrier_data.get("type", "Unknown")
                if not isinstance(prev_type, str):
                    prev_type = str(prev_type) if prev_type is not None else "Unknown"
                    
                prev_mcc = previous_carrier_data.get("mobile_country_code")
                if prev_mcc is not None and not isinstance(prev_mcc, str):
                    prev_mcc = str(prev_mcc)
                    
                prev_mnc = previous_carrier_data.get("mobile_network_code")
                if prev_mnc is not None and not isinstance(prev_mnc, str):
                    prev_mnc = str(prev_mnc)
                
                previous_carrier = CarrierInfo(
                    name=prev_name,
                    type=prev_type,
                    mobile_country_code=prev_mcc,
                    mobile_network_code=prev_mnc
                )
            
            # 确保便携性信息字段数据类型正确
            portable_value = portability_data.get("portable", False)
            ported_value = portability_data.get("ported", False)
            
            # 确保布尔值
            if not isinstance(portable_value, bool):
                portable_value = bool(portable_value)
            if not isinstance(ported_value, bool):
                ported_value = bool(ported_value)
                
            spid = portability_data.get("spid")
            if spid is not None and not isinstance(spid, str):
                spid = str(spid)
                
            ocn = portability_data.get("ocn")
            if ocn is not None and not isinstance(ocn, str):
                ocn = str(ocn)
                
            portability = PortabilityInfo(
                portable=portable_value,
                ported=ported_value,
                spid=spid,
                ocn=ocn,
                previous_carrier=previous_carrier
            )
            
            # 确保其他字段数据类型正确
            phone_number_value = data.get("phone_number", formatted_number)
            if not isinstance(phone_number_value, str):
                phone_number_value = str(phone_number_value) if phone_number_value is not None else formatted_number
                
            country_code_value = data.get("country_code", "US")
            if not isinstance(country_code_value, str):
                country_code_value = str(country_code_value) if country_code_value is not None else "US"
                
            request_id = response.get("meta", {}).get("request_id")
            if request_id is not None and not isinstance(request_id, str):
                request_id = str(request_id)
            
            return LookupResult(
                phone_number=phone_number_value,
                country_code=country_code_value,
                carrier=carrier,
                portability=portability,
                status="success",
                lookup_time=time.time(),
                request_id=request_id
            )
            
        except APIError as e:
            # 创建错误结果
            return LookupResult(
                phone_number=formatted_number,
                country_code="US",
                carrier=CarrierInfo(name="Error", type="unknown"),
                status=f"error: {str(e)}",
                lookup_time=time.time(),
                request_id=None
            )
    
    @staticmethod
    def _format_phone_number(phone_number: str) -> str:
        """
        格式化电话号码为E.164格式
        
        Args:
            phone_number: 输入的电话号码
            
        Returns:
            str: 格式化后的电话号码
        """
        # 移除所有非数字字符
        digits_only = ''.join(c for c in phone_number if c.isdigit())
        
        # 处理美国/加拿大号码
        if phone_number.startswith('+1') or (not phone_number.startswith('+') and len(digits_only) == 10):
            # 确保有国家代码
            if len(digits_only) == 10:
                return f"+1{digits_only}"
            elif len(digits_only) == 11 and digits_only.startswith('1'):
                return f"+{digits_only}"
            else:
                return f"+{digits_only}"  # 可能是不正确的格式，但尝试处理
        
        # 其他国际号码
        if not phone_number.startswith('+') and len(digits_only) > 10:
            return f"+{digits_only}"
        
        # 如果已经是E.164格式，或无法处理，则原样返回
        return phone_number
