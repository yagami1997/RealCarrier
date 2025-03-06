"""
配置管理模块 - 负责处理用户配置和API密钥的安全存储
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any

import keyring
from keyring.errors import KeyringError

# 配置常量
APP_NAME = "realcarrier"
CONFIG_DIR = Path.home() / ".lnptool"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_DIR = CONFIG_DIR / "cache"
LAST_PROVIDER_FILE = CONFIG_DIR / "last_provider.txt"
KEYRING_SERVICE = "realcarrier-telnyx-api"
KEYRING_USERNAME = "telnyx-api-key"

# 配置默认值
DEFAULT_CONFIG = {
    "api_cache_ttl": 86400,  # 默认缓存24小时
    "rate_limit": 2,         # 默认每秒最多2个请求
}

logger = logging.getLogger(__name__)


def ensure_config_dir() -> None:
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    logger.info(f"Created configuration directory: {CONFIG_DIR}")


def get_config() -> Dict[str, Any]:
    """
    获取用户配置。如果配置文件不存在，则创建默认配置。
    
    Returns:
        Dict[str, Any]: 配置字典
    """
    ensure_config_dir()
    
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        logger.info(f"Created default configuration file: {CONFIG_FILE}")
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 确保所有默认配置项都存在
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read configuration file: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> bool:
    """
    保存用户配置
    
    Args:
        config (Dict[str, Any]): 要保存的配置字典
        
    Returns:
        bool: 保存成功返回True，否则返回False
    """
    ensure_config_dir()
    
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved successfully")
        return True
    except IOError as e:
        logger.error(f"Failed to save configuration: {e}")
        return False


def get_api_key() -> Optional[str]:
    """
    从系统安全存储获取Telnyx API密钥
    
    Returns:
        Optional[str]: API密钥，如果未配置则返回None
    """
    try:
        api_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        return api_key
    except KeyringError as e:
        logger.error(f"Failed to retrieve API key from keyring: {e}")
        return None


def set_api_key(api_key: str) -> bool:
    """
    安全地存储Telnyx API密钥
    
    Args:
        api_key (str): 要存储的API密钥
        
    Returns:
        bool: 存储成功返回True，否则返回False
    """
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
        logger.info("API key stored successfully")
        return True
    except KeyringError as e:
        logger.error(f"Failed to store API key: {e}")
        return False


def delete_api_key() -> bool:
    """
    删除存储的API密钥
    
    Returns:
        bool: 删除成功返回True，否则返回False
    """
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
        logger.info("API key deleted successfully")
        return True
    except KeyringError as e:
        logger.error(f"Failed to delete API key: {e}")
        return False


def update_config_setting(key: str, value: Any) -> bool:
    """
    更新单个配置设置
    
    Args:
        key (str): 配置键
        value (Any): 配置值
    
    Returns:
        bool: 更新成功返回True，否则返回False
    """
    config = get_config()
    config[key] = value
    return save_config(config)


def is_configured() -> bool:
    """
    检查工具是否已配置（API密钥是否已设置）
    
    Returns:
        bool: 如果API密钥已设置，返回True，否则返回False
    """
    return get_api_key() is not None


def save_last_used_provider(provider_id):
    """保存上次使用的API提供商ID"""
    try:
        ensure_config_dir()
        with open(LAST_PROVIDER_FILE, 'w') as f:
            f.write(provider_id)
        return True
    except Exception as e:
        logger.error(f"保存上次使用的API提供商失败: {e}")
        return False


def get_last_used_provider():
    """获取上次使用的API提供商ID，如果不存在则返回默认值'telnyx'"""
    try:
        if LAST_PROVIDER_FILE.exists():
            with open(LAST_PROVIDER_FILE, 'r') as f:
                provider_id = f.read().strip()
                return provider_id if provider_id in ['telnyx', 'twilio'] else 'telnyx'
        return 'telnyx'  # 默认使用telnyx
    except Exception as e:
        logger.error(f"读取上次使用的API提供商失败: {e}")
        return 'telnyx'  # 出错时默认使用telnyx
