"""
提供商接口模块
定义了号码查询提供商的抽象接口和注册机制
"""

import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Type, Union, Set, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('provider')

# 电话号码验证正则表达式
PHONE_NUMBER_REGEX = re.compile(r'^(?:\+?1)?(\d{10})$')


class LookupResult:
    """号码查询结果类"""
    
    def __init__(self, 
                 phone_number: str,
                 carrier: Optional[str] = None,
                 carrier_type: Optional[str] = None,
                 portable: Optional[bool] = None,
                 city: Optional[str] = None,
                 state: Optional[str] = None,
                 rate_center: Optional[str] = None,
                 lata: Optional[str] = None,
                 line_type: Optional[str] = None,
                 provider: Optional[str] = None,
                 raw_data: Optional[Dict[str, Any]] = None):
        """
        初始化查询结果
        
        Args:
            phone_number: 查询的电话号码
            carrier: 运营商名称
            carrier_type: 运营商类型
            portable: 是否可携号转网
            city: 城市
            state: 州
            rate_center: 费率中心
            lata: 本地接入传输区
            line_type: 线路类型 (mobile, landline, voip, unknown)
            provider: 提供此结果的提供商名称
            raw_data: 原始响应数据
        """
        self.phone_number = phone_number
        self.carrier = carrier
        self.carrier_type = carrier_type
        self.portable = portable
        self.city = city
        self.state = state
        self.rate_center = rate_center
        self.lata = lata
        self.line_type = line_type
        self.provider = provider
        self.raw_data = raw_data or {}
        self.timestamp = time.time()  # 添加时间戳，用于缓存过期判断
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "phone_number": self.phone_number,
            "carrier": self.carrier,
            "carrier_type": self.carrier_type,
            "portable": self.portable,
            "city": self.city,
            "state": self.state,
            "rate_center": self.rate_center,
            "lata": self.lata,
            "line_type": self.line_type,
            "provider": self.provider,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LookupResult':
        """从字典创建结果对象"""
        result = cls(
            phone_number=data.get("phone_number", ""),
            carrier=data.get("carrier"),
            carrier_type=data.get("carrier_type"),
            portable=data.get("portable"),
            city=data.get("city"),
            state=data.get("state"),
            rate_center=data.get("rate_center"),
            lata=data.get("lata"),
            line_type=data.get("line_type"),
            provider=data.get("provider"),
            raw_data=data.get("raw_data", {})
        )
        if "timestamp" in data:
            result.timestamp = data["timestamp"]
        return result
    
    def is_expired(self, ttl_seconds: int = 86400) -> bool:
        """
        检查结果是否已过期
        
        Args:
            ttl_seconds: 生存时间（秒），默认为1天
            
        Returns:
            bool: 如果结果已过期返回True，否则返回False
        """
        return (time.time() - self.timestamp) > ttl_seconds


class LookupError(Exception):
    """查询错误基类"""
    
    def __init__(self, message: str, provider: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化查询错误
        
        Args:
            message: 错误消息
            provider: 提供商名称
            details: 错误详情
        """
        self.provider = provider
        self.details = details or {}
        super().__init__(f"{provider} error: {message}")


class ConfigurationError(LookupError):
    """配置错误"""
    pass


class AuthenticationError(LookupError):
    """认证错误"""
    pass


class RateLimitError(LookupError):
    """速率限制错误"""
    pass


class NetworkError(LookupError):
    """网络错误"""
    pass


class LookupProvider(ABC):
    """号码查询提供商抽象接口"""
    
    def __init__(self):
        """初始化提供商"""
        self._cache: Dict[str, LookupResult] = {}
        self._cache_ttl = 86400  # 默认缓存1天
    
    @abstractmethod
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
        pass
    
    def lookup_numbers(self, phone_numbers: List[str], use_cache: bool = True) -> Dict[str, Union[LookupResult, Exception]]:
        """
        批量查询电话号码信息
        
        Args:
            phone_numbers: 要查询的电话号码列表
            use_cache: 是否使用缓存
            
        Returns:
            Dict[str, Union[LookupResult, Exception]]: 电话号码和查询结果（或错误）的字典
        """
        results = {}
        for phone_number in phone_numbers:
            try:
                results[phone_number] = self.lookup_number(phone_number, use_cache)
            except Exception as e:
                results[phone_number] = e
        return results
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        获取提供商名称
        
        Returns:
            str: 提供商名称
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        检查提供商是否已配置
        
        Returns:
            bool: 如果提供商已配置返回True，否则返回False
        """
        pass
    
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
            "location": True,
            "batch_lookup": self.supports_batch_lookup(),
            "cache": True,
            "rate_limit": True
        }
    
    def supports_batch_lookup(self) -> bool:
        """
        检查提供商是否支持批量查询
        
        Returns:
            bool: 如果提供商支持批量查询返回True，否则返回False
        """
        return False
    
    def validate_phone_number(self, phone_number: str) -> str:
        """
        验证并格式化电话号码
        
        Args:
            phone_number: 要验证的电话号码
            
        Returns:
            str: 格式化后的电话号码
            
        Raises:
            ValueError: 如果号码格式无效
        """
        # 移除所有非数字字符
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # 如果是11位且以1开头，移除1
        if len(cleaned) == 11 and cleaned.startswith('1'):
            cleaned = cleaned[1:]
        
        # 验证是否为10位数字
        if len(cleaned) != 10:
            raise ValueError("电话号码必须是10位数字")
        
        # 返回E.164格式
        return f"+1{cleaned}"
    
    def get_from_cache(self, phone_number: str) -> Optional[LookupResult]:
        """
        从缓存获取查询结果
        
        Args:
            phone_number: 电话号码
            
        Returns:
            Optional[LookupResult]: 缓存的查询结果，如果不存在或已过期返回None
        """
        # 格式化电话号码作为缓存键
        try:
            formatted_number = self.validate_phone_number(phone_number)
        except ValueError:
            return None
        
        # 检查缓存
        result = self._cache.get(formatted_number)
        if result and not result.is_expired(self._cache_ttl):
            return result
        
        return None
    
    def add_to_cache(self, result: LookupResult) -> None:
        """
        添加查询结果到缓存
        
        Args:
            result: 查询结果
        """
        self._cache[result.phone_number] = result
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._cache.clear()
    
    def set_cache_ttl(self, ttl_seconds: int) -> None:
        """
        设置缓存生存时间
        
        Args:
            ttl_seconds: 生存时间（秒）
        """
        self._cache_ttl = ttl_seconds
    
    def get_cache_ttl(self) -> int:
        """
        获取缓存TTL
        
        Returns:
            int: 缓存生存时间（秒）
        """
        return self._cache_ttl


class ProviderRegistry:
    """提供商注册表"""
    
    _providers: Dict[str, Type[LookupProvider]] = {}
    _instances: Dict[str, LookupProvider] = {}
    _priority: List[str] = []
    _configured_cache: Dict[str, bool] = {}
    _cache_timestamp: float = 0
    _cache_ttl: float = 60  # 缓存有效期（秒）
    
    @classmethod
    def register(cls, provider_id: str, provider_class: Type[LookupProvider]) -> None:
        """
        注册提供商类
        
        Args:
            provider_id: 提供商ID
            provider_class: 提供商类
        """
        if provider_id in cls._providers:
            logger.warning(f"Provider {provider_id} already registered, overwriting")
        
        cls._providers[provider_id] = provider_class
        # 清除缓存
        cls._configured_cache.clear()
        cls._cache_timestamp = 0
        logger.info(f"Registered provider: {provider_id}")
    
    @classmethod
    def get_provider_class(cls, provider_id: str) -> Optional[Type[LookupProvider]]:
        """
        获取提供商类
        
        Args:
            provider_id: 提供商ID
            
        Returns:
            Type[LookupProvider]: 提供商类，如果不存在返回None
        """
        return cls._providers.get(provider_id)
    
    @classmethod
    def get_provider(cls, provider_id: str) -> Optional[LookupProvider]:
        """
        获取提供商实例
        
        Args:
            provider_id: 提供商ID
            
        Returns:
            LookupProvider: 提供商实例，如果不存在或创建失败返回None
        """
        if provider_id not in cls._instances and provider_id in cls._providers:
            try:
                cls._instances[provider_id] = cls._providers[provider_id]()
                logger.info(f"Created provider instance: {provider_id}")
            except Exception as e:
                logger.error(f"Failed to create provider instance {provider_id}: {e}")
                return None
        
        return cls._instances.get(provider_id)
    
    @classmethod
    def get_all_providers(cls) -> Dict[str, Type[LookupProvider]]:
        """
        获取所有注册的提供商类
        
        Returns:
            Dict[str, Type[LookupProvider]]: 提供商ID和类的字典
        """
        return cls._providers.copy()
    
    @classmethod
    def get_all_provider_instances(cls) -> Dict[str, LookupProvider]:
        """
        获取所有提供商实例
        
        Returns:
            Dict[str, LookupProvider]: 提供商ID和实例的字典
        """
        # 只创建尚未创建的实例
        for provider_id in cls._providers:
            if provider_id not in cls._instances:
                cls.get_provider(provider_id)
        
        # 过滤掉创建失败的实例
        return {k: v for k, v in cls._instances.items() if v is not None}
    
    @classmethod
    def get_configured_providers(cls) -> Dict[str, LookupProvider]:
        """
        获取所有已配置的提供商实例
        
        Returns:
            Dict[str, LookupProvider]: 提供商ID和实例的字典
        """
        # 检查缓存是否有效
        current_time = time.time()
        if current_time - cls._cache_timestamp <= cls._cache_ttl and cls._configured_cache:
            # 使用缓存的配置状态
            configured = {}
            for provider_id, is_configured in cls._configured_cache.items():
                if is_configured:
                    provider = cls.get_provider(provider_id)
                    if provider:
                        configured[provider_id] = provider
            return configured
        
        # 缓存过期，重新检查配置状态
        configured = {}
        cls._configured_cache = {}
        
        for provider_id, provider in cls.get_all_provider_instances().items():
            try:
                if provider and provider.is_configured():
                    configured[provider_id] = provider
                    cls._configured_cache[provider_id] = True
                else:
                    cls._configured_cache[provider_id] = False
            except Exception as e:
                logger.error(f"Error checking if provider {provider_id} is configured: {e}")
                cls._configured_cache[provider_id] = False
        
        cls._cache_timestamp = current_time
        return configured
    
    @classmethod
    def set_priority(cls, priority_list: List[str]) -> None:
        """
        设置提供商优先级
        
        Args:
            priority_list: 按优先级排序的提供商ID列表
            
        Raises:
            ValueError: 如果列表中包含未注册的提供商ID
        """
        # 验证所有ID都是有效的提供商
        unknown_ids = [pid for pid in priority_list if pid not in cls._providers]
        if unknown_ids:
            raise ValueError(f"Unknown provider IDs: {', '.join(unknown_ids)}")
        
        cls._priority = priority_list.copy()
        logger.info(f"Set provider priority: {priority_list}")
    
    @classmethod
    def get_priority(cls) -> List[str]:
        """
        获取提供商优先级
        
        Returns:
            List[str]: 按优先级排序的提供商ID列表
        """
        if not cls._priority:
            # 如果未设置优先级，返回所有已注册提供商的ID
            return list(cls._providers.keys())
        
        return cls._priority.copy()
    
    @classmethod
    def get_provider_by_priority(cls) -> Optional[LookupProvider]:
        """
        按优先级获取第一个已配置的提供商实例
        
        Returns:
            LookupProvider: 提供商实例，如果没有已配置的提供商返回None
        """
        configured = cls.get_configured_providers()
        if not configured:
            logger.warning("No configured providers available")
            return None
        
        # 按优先级顺序尝试获取提供商
        for provider_id in cls.get_priority():
            if provider_id in configured:
                return configured[provider_id]
        
        # 如果没有匹配优先级的提供商，返回任意一个已配置的提供商
        logger.info("No provider matching priority order, using any configured provider")
        return next(iter(configured.values()))
    
    @classmethod
    def clear(cls) -> None:
        """清除所有注册的提供商和实例"""
        cls._providers.clear()
        cls._instances.clear()
        cls._priority.clear()
        cls._configured_cache.clear()
        cls._cache_timestamp = 0
        logger.info("Cleared provider registry")
    
    @classmethod
    def invalidate_cache(cls) -> None:
        """使缓存失效"""
        cls._configured_cache.clear()
        cls._cache_timestamp = 0
        logger.debug("Invalidated provider configuration cache") 