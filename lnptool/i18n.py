"""
国际化支持模块 - 简化版
提供多语言支持功能
"""

import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('i18n')

# 语言配置文件路径
LANGUAGE_CONFIG_FILE = Path.home() / ".realcarrier" / "language.json"

# 当前语言设置
CURRENT_LANGUAGE = "zh_CN"  # 默认为中文

# 翻译字典
TRANSLATIONS = {
    "zh_CN": {},
    "en_US": {}
}

def set_translations(translations_dict):
    """设置翻译字典"""
    global TRANSLATIONS
    TRANSLATIONS = translations_dict

def get_current_language():
    """获取当前语言设置"""
    global CURRENT_LANGUAGE
    return CURRENT_LANGUAGE

def set_language(language):
    """设置当前语言"""
    global CURRENT_LANGUAGE
    if language in ["zh_CN", "en_US"]:
        CURRENT_LANGUAGE = language
        return True
    return False

def load_language_preference():
    """从文件加载语言设置"""
    global CURRENT_LANGUAGE
    try:
        if LANGUAGE_CONFIG_FILE.exists():
            with open(LANGUAGE_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if 'language' in config and config['language'] in ['zh_CN', 'en_US']:
                    CURRENT_LANGUAGE = config['language']
                    return True
    except Exception as e:
        logger.error(f"加载语言设置出错: {e}")
    return False

def save_language_preference(language):
    """保存语言设置到文件"""
    try:
        LANGUAGE_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LANGUAGE_CONFIG_FILE, 'w') as f:
            json.dump({'language': language}, f)
        return True
    except Exception as e:
        logger.error(f"保存语言设置出错: {e}")
        return False

def t(key):
    """获取翻译文本"""
    global CURRENT_LANGUAGE, TRANSLATIONS
    try:
        if key in TRANSLATIONS.get(CURRENT_LANGUAGE, {}):
            return TRANSLATIONS[CURRENT_LANGUAGE][key]
        elif key in TRANSLATIONS.get("en_US", {}):
            return TRANSLATIONS["en_US"][key]
        else:
            return key
    except Exception:
        return key 