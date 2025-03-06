"""
提供商管理模块
负责注册、初始化和管理所有提供商，支持多供应商配置和选择
"""

import logging
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple

from .provider import ProviderRegistry, LookupProvider, LookupResult, LookupError
from .telnyx_api import TelnyxAPI
from .twilio_api import TwilioAPI
from .i18n import t

# 配置日志
logger = logging.getLogger('provider_manager')

# 常量定义
PROVIDER_CONFIG_FILE = Path.home() / ".lnptool" / "provider_config.json"
DEFAULT_PROVIDER_PRIORITY = ["telnyx", "twilio"]

# 提供商选择模式
AUTO_MODE = "auto"  # 自动模式（按优先级）
MANUAL_MODE = "manual"  # 手动模式（指定提供商）

# 全局变量
_current_mode = AUTO_MODE
_current_provider_id = None
_initialized = False


def initialize() -> None:
    """初始化提供商管理模块"""
    global _initialized, _current_mode, _current_provider_id
    
    if _initialized:
        return
    
    try:
        # 确保配置目录存在
        PROVIDER_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果配置文件存在，加载配置
        if PROVIDER_CONFIG_FILE.exists():
            with open(PROVIDER_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                _current_mode = config.get('mode', AUTO_MODE)
                _current_provider_id = config.get('provider_id')
        
        # 注册所有提供商
        register_all_providers()
        
        _initialized = True
        logger.info("提供商管理模块初始化完成")
    
    except Exception as e:
        logger.error(f"提供商管理模块初始化失败: {e}")
        raise


def register_all_providers() -> None:
    """注册所有可用的提供商"""
    # 注册 Telnyx 提供商
    ProviderRegistry.register("telnyx", TelnyxAPI)
    
    # 注册 Twilio 提供商
    ProviderRegistry.register("twilio", TwilioAPI)
    
    logger.info("所有提供商已注册")


def get_provider_status() -> List[Dict[str, Any]]:
    """
    获取所有提供商的状态信息
    
    Returns:
        List[Dict[str, Any]]: 提供商状态信息列表
    """
    # 确保模块已初始化
    if not _initialized:
        initialize()
    
    status_list = []
    
    for provider_id, provider_class in ProviderRegistry.get_all_providers().items():
        provider = ProviderRegistry.get_provider(provider_id)
        
        if provider:
            status = {
                "id": provider_id,
                "name": provider.get_provider_name(),
                "configured": provider.is_configured(),
                "features": provider.get_provider_features(),
                "active": is_provider_active(provider_id)
            }
        else:
            status = {
                "id": provider_id,
                "name": provider_id.capitalize(),
                "configured": False,
                "features": {},
                "active": False
            }
        
        status_list.append(status)
    
    return status_list


def is_provider_active(provider_id: str) -> bool:
    """
    检查提供商是否为当前活跃提供商
    
    Args:
        provider_id: 提供商ID
        
    Returns:
        bool: 如果是当前活跃提供商返回True，否则返回False
    """
    global _current_mode, _current_provider_id
    
    if _current_mode == MANUAL_MODE:
        return provider_id == _current_provider_id
    else:  # AUTO_MODE
        active_provider = get_active_provider()
        if active_provider:
            return provider_id == get_provider_id(active_provider)
        return False


def get_active_provider() -> Optional[LookupProvider]:
    """
    获取当前活跃的提供商
    根据当前模式（自动或手动）返回相应的提供商
    
    Returns:
        Optional[LookupProvider]: 活跃的提供商实例，如果没有已配置的提供商则返回None
    """
    global _current_mode, _current_provider_id
    
    # 确保模块已初始化
    if not _initialized:
        initialize()
    
    if _current_mode == MANUAL_MODE and _current_provider_id:
        # 手动模式：返回指定的提供商
        provider = ProviderRegistry.get_provider(_current_provider_id)
        if provider and provider.is_configured():
            return provider
        else:
            # 如果指定的提供商不可用，回退到自动模式
            logger.warning(f"指定的提供商 {_current_provider_id} 不可用，回退到自动模式")
            _current_mode = AUTO_MODE
            _current_provider_id = None
    
    # 自动模式：按优先级返回提供商
    return ProviderRegistry.get_provider_by_priority()


def get_provider_by_id(provider_id: str) -> Optional[LookupProvider]:
    """
    通过ID获取提供商实例
    
    Args:
        provider_id: 提供商ID
        
    Returns:
        Optional[LookupProvider]: 提供商实例，如果不存在或未配置则返回None
    """
    provider = ProviderRegistry.get_provider(provider_id)
    if provider and provider.is_configured():
        return provider
    return None


def set_provider_priority(priority_list: List[str]) -> bool:
    """
    设置提供商优先级
    
    Args:
        priority_list: 按优先级排序的提供商ID列表
        
    Returns:
        bool: 如果设置成功返回True，否则返回False
    """
    try:
        ProviderRegistry.set_priority(priority_list)
        logger.info(f"已设置提供商优先级: {priority_list}")
        
        # 保存配置
        save_provider_config()
        
        return True
    except ValueError as e:
        logger.error(f"设置提供商优先级失败: {e}")
        return False


def get_configured_provider_ids() -> List[str]:
    """
    获取所有已配置的提供商ID
    
    Returns:
        List[str]: 已配置的提供商ID列表
    """
    return list(ProviderRegistry.get_configured_providers().keys())


def get_provider_priority() -> List[str]:
    """
    获取当前提供商优先级
    
    Returns:
        List[str]: 按优先级排序的提供商ID列表
    """
    return ProviderRegistry.get_priority()


def set_provider_mode(mode: str, provider_id: Optional[str] = None) -> bool:
    """
    设置提供商选择模式
    
    Args:
        mode: 模式 ("auto" 或 "manual")
        provider_id: 手动模式下指定的提供商ID
        
    Returns:
        bool: 如果设置成功返回True，否则返回False
    """
    global _current_mode, _current_provider_id
    
    if mode not in [AUTO_MODE, MANUAL_MODE]:
        logger.error(f"无效的提供商模式: {mode}")
        return False
    
    if mode == MANUAL_MODE:
        if not provider_id:
            logger.error("手动模式需要指定提供商ID")
            return False
        
        provider = get_provider_by_id(provider_id)
        if not provider:
            logger.error(f"提供商 {provider_id} 不存在或未配置")
            return False
    
    # 更新模式和提供商ID
    _current_mode = mode
    _current_provider_id = provider_id if mode == MANUAL_MODE else None
    
    logger.info(f"已设置提供商模式: {mode}" + 
               (f", 提供商: {provider_id}" if mode == MANUAL_MODE else ""))
    
    # 保存配置
    save_provider_config()
    
    return True


def get_current_provider_mode() -> Dict[str, Any]:
    """
    获取当前提供商选择模式信息
    
    Returns:
        Dict[str, Any]: 包含模式和提供商信息的字典
    """
    global _current_mode, _current_provider_id
    
    active_provider = get_active_provider()
    
    return {
        "mode": _current_mode,
        "provider_id": _current_provider_id if _current_mode == MANUAL_MODE else None,
        "active_provider": active_provider.get_provider_name() if active_provider else None,
        "active_provider_id": get_provider_id(active_provider) if active_provider else None
    }


def get_provider_id(provider: Optional[LookupProvider]) -> Optional[str]:
    """
    获取提供商的ID
    
    Args:
        provider: 提供商实例
        
    Returns:
        Optional[str]: 提供商ID，如果提供商为None则返回None
    """
    if not provider:
        return None
    
    for provider_id, instance in ProviderRegistry.get_all_provider_instances().items():
        if instance is provider:
            return provider_id
    
    return None


def save_provider_config() -> bool:
    """
    保存提供商配置到文件
    
    Returns:
        bool: 如果保存成功返回True，否则返回False
    """
    global _current_mode, _current_provider_id
    
    config = {
        "priority": ProviderRegistry.get_priority(),
        "mode": _current_mode,
        "provider_id": _current_provider_id
    }
    
    try:
        # 确保目录存在
        config_dir = PROVIDER_CONFIG_FILE.parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(PROVIDER_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"提供商配置已保存到: {PROVIDER_CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"保存提供商配置失败: {e}")
        return False


def load_provider_config() -> bool:
    """
    从文件加载提供商配置
    
    Returns:
        bool: 如果加载成功返回True，否则返回False
    """
    global _current_mode, _current_provider_id
    
    if not PROVIDER_CONFIG_FILE.exists():
        logger.info(f"提供商配置文件不存在: {PROVIDER_CONFIG_FILE}")
        return False
    
    try:
        with open(PROVIDER_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # 加载优先级
        if "priority" in config and isinstance(config["priority"], list):
            ProviderRegistry.set_priority(config["priority"])
            logger.info(f"已加载提供商优先级: {config['priority']}")
        
        # 加载模式
        if "mode" in config and config["mode"] in [AUTO_MODE, MANUAL_MODE]:
            _current_mode = config["mode"]
            logger.info(f"已加载提供商模式: {_current_mode}")
        
        # 加载提供商ID
        if "provider_id" in config:
            _current_provider_id = config["provider_id"]
            logger.info(f"已加载当前提供商ID: {_current_provider_id}")
        
        logger.info(f"提供商配置已从 {PROVIDER_CONFIG_FILE} 加载")
        return True
    except Exception as e:
        logger.error(f"加载提供商配置失败: {e}")
        return False


def lookup_number(phone_number: str, provider_id: Optional[str] = None) -> Tuple[Optional[LookupProvider], Union[LookupResult, Exception]]:
    """
    查询电话号码信息
    
    Args:
        phone_number: 要查询的电话号码
        provider_id: 指定的提供商ID，如果为None则使用当前活动提供商
        
    Returns:
        Tuple[Optional[LookupProvider], Union[LookupResult, Exception]]: 
            - 使用的提供商实例（如果失败则为None）
            - 查询结果或异常
    """
    # 如果指定了提供商ID，使用指定的提供商
    if provider_id:
        provider = get_provider_by_id(provider_id)
        if not provider:
            logger.error(f"{t('provider')} {provider_id} {t('not_exist_or_not_configured')}")
            return None, ValueError(f"{t('provider')} {provider_id} {t('not_exist_or_not_configured')}")
    else:
        # 否则使用当前活跃提供商
        provider = get_active_provider()
        if not provider:
            logger.error(t('no_available_provider'))
            return None, ValueError(t('no_available_provider'))
    
    # 执行查询
    try:
        logger.info(f"{t('using')} {provider.get_provider_name()} {t('query_number')}: {phone_number}")
        result = provider.lookup_number(phone_number)
        return provider, result
    except Exception as e:
        logger.error(f"{t('query_number_failed')}: {e}")
        # 确保返回的异常对象有有意义的字符串表示
        if not str(e):
            e = Exception(f"{t('unknown_error_when_querying')} {phone_number}")
        return provider, e 