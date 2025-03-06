"""
国际化模块，提供多语言支持功能
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 初始化日志记录器
logger = logging.getLogger(__name__)

# 全局变量
_translations: Dict[str, Dict[str, str]] = {}
_current_language = "zh_CN"  # 默认语言为中文

def set_translations(translations: Dict[str, Dict[str, str]]) -> bool:
    """
    设置翻译字典
    
    Args:
        translations: 包含所有语言翻译的字典
        
    Returns:
        bool: 是否成功设置
    """
    global _translations
    if not translations:
        return False
    
    _translations = translations
    return True

def get_current_language() -> str:
    """
    获取当前语言
    
    Returns:
        str: 当前语言代码
    """
    return _current_language

def set_language(language_code: str) -> bool:
    """
    设置当前语言
    
    Args:
        language_code: 语言代码，如'zh_CN'或'en_US'
        
    Returns:
        bool: 是否成功设置
    """
    global _current_language
    
    if language_code in _translations:
        _current_language = language_code
        return True
    else:
        logger.warning(f"未找到语言 {language_code} 的翻译，保持当前语言 {_current_language}")
        return False

def t(key: str) -> str:
    """
    获取指定键的翻译
    
    Args:
        key: 翻译键
        
    Returns:
        str: 翻译后的文本，如果未找到则返回键本身
    """
    if not _translations or _current_language not in _translations:
        return key
    
    translation = _translations[_current_language].get(key)
    if translation is None:
        # 如果当前语言没有该键的翻译，尝试使用英文翻译
        if _current_language != "en_US" and "en_US" in _translations:
            translation = _translations["en_US"].get(key)
        
        # 如果英文也没有，返回键本身
        if translation is None:
            logger.debug(f"未找到键 '{key}' 的翻译")
            return key
    
    return translation

def save_language_preference(language_code: str) -> bool:
    """
    保存语言偏好设置到配置文件
    
    Args:
        language_code: 语言代码
        
    Returns:
        bool: 是否成功保存
    """
    try:
        # 获取配置目录
        config_dir = Path.home() / ".lnptool"
        config_dir.mkdir(exist_ok=True)
        
        # 语言配置文件
        lang_file = config_dir / "language.json"
        
        # 保存语言设置
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump({"language": language_code}, f)
        
        return True
    except Exception as e:
        logger.error(f"保存语言偏好设置失败: {e}")
        return False

def load_language_preference() -> str:
    """
    从配置文件加载语言偏好设置
    
    Returns:
        str: 加载的语言代码，如果加载失败则返回默认语言 "zh_CN"
    """
    try:
        # 获取配置目录
        config_dir = Path.home() / ".lnptool"
        lang_file = config_dir / "language.json"
        
        # 如果文件存在，读取语言设置
        if lang_file.exists():
            with open(lang_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                language = data.get("language")
                
                if language and set_language(language):
                    logger.info(f"已加载语言偏好设置: {language}")
                    return language
        
        # 如果文件不存在或加载失败，返回默认语言
        logger.info("使用默认语言: zh_CN")
        return "zh_CN"
    except Exception as e:
        logger.error(f"加载语言偏好设置失败: {e}")
        # 返回默认语言
        return "zh_CN" 