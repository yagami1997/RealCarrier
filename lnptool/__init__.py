"""
LNP Tool - 美国电话号码携号转网查询工具
"""

import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from pathlib import Path

# 设置日志配置
def setup_logging(log_level=logging.INFO):
    """
    配置日志系统
    
    Args:
        log_level: 日志级别
    """
    # 创建日志目录
    log_dir = Path.home() / ".lnptool" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "lnptool.log"
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 内部级别为DEBUG，输出级别由handlers控制
    
    # 清除任何现有的处理程序
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 文件处理程序 - 记录所有级别的日志
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 控制台处理程序 - 只显示警告以上级别
    # 使用传入的log_level参数
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 添加处理程序到根日志记录器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 为第三方库设置更高的日志级别，减少输出
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return root_logger

# 默认设置为WARNING级别，减少控制台输出
# 所有重要信息都会通过rich表格展示
logger = setup_logging(logging.WARNING)

__version__ = "0.1.0"
