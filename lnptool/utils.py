"""
工具函数模块 - 提供各种辅助功能
"""

import re
import os
import logging
import sys
from pathlib import Path
from typing import List, Optional, Callable, Any
from datetime import datetime, timezone

import click
from rich.console import Console

console = Console()


def configure_logging(verbose: bool = False) -> None:
    """
    配置日志记录
    
    Args:
        verbose: 是否启用详细日志
    """
    from lnptool.config import CONFIG_DIR
    
    # 确保日志目录存在
    log_dir = CONFIG_DIR / "logs"
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建日志文件名
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = log_dir / f"lnptool-{timestamp}.log"
    
    # 配置日志级别
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # 创建日志处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    
    # 避免重复记录
    root_logger.propagate = False
    
    # 记录初始信息
    logging.info(f"Log started at {timestamp}")
    logging.info(f"Verbose logging: {verbose}")


def validate_phone_number(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """
    验证电话号码格式
    
    Args:
        ctx: Click上下文
        param: 参数对象
        value: 电话号码
        
    Returns:
        str: 有效的电话号码
        
    Raises:
        click.BadParameter: 如果电话号码格式无效
    """
    if not value:
        return value
    
    # 移除非数字字符
    digits_only = ''.join(c for c in value if c.isdigit())
    
    # 验证格式
    if len(digits_only) not in (10, 11) or (len(digits_only) == 11 and not digits_only.startswith('1')):
        raise click.BadParameter(f"请提供有效的美国电话号码。可以是10位数字或以1开头的11位数字。")
    
    # 格式化为E.164格式
    if len(digits_only) == 10:
        return f"+1{digits_only}"
    else:
        return f"+{digits_only}"


def validate_csv_file(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """
    验证CSV文件路径
    
    Args:
        ctx: Click上下文
        param: 参数对象
        value: 文件路径
        
    Returns:
        str: 有效的文件路径
        
    Raises:
        click.BadParameter: 如果文件路径无效
    """
    if not value:
        return value
    
    path = Path(value)
    
    if not path.exists():
        raise click.BadParameter(f"文件不存在: {value}")
    
    if not path.is_file():
        raise click.BadParameter(f"不是一个文件: {value}")
    
    if path.suffix.lower() != '.csv':
        raise click.BadParameter(f"不是CSV文件: {value}")
    
    return value


def format_timestamp(timestamp: float) -> str:
    """
    格式化时间戳为人类可读的日期时间
    
    Args:
        timestamp: Unix时间戳
        
    Returns:
        str: 格式化的日期时间字符串
    """
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    local_dt = dt.astimezone()  # 转换为本地时区
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")


def is_valid_api_key(api_key: str) -> bool:
    """
    检查API密钥是否有效
    
    Args:
        api_key: 要检查的API密钥
        
    Returns:
        bool: 如果API密钥格式有效，返回True
    """
    # Telnyx API密钥通常是以KEY开头的字符串，后跟一系列字母数字字符
    pattern = r'^KEY[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, api_key))


def print_error(message: str) -> None:
    """
    打印错误消息
    
    Args:
        message: 错误消息
    """
    console.print(f"[bold red]错误: {message}[/bold red]")


def print_warning(message: str) -> None:
    """
    打印警告消息
    
    Args:
        message: 警告消息
    """
    console.print(f"[bold yellow]警告: {message}[/bold yellow]")


def print_success(message: str) -> None:
    """
    打印成功消息
    
    Args:
        message: 成功消息
    """
    console.print(f"[bold green]{message}[/bold green]")


def print_info(message: str) -> None:
    """
    打印信息消息
    
    Args:
        message: 信息消息
    """
    console.print(f"[cyan]{message}[/cyan]")


def safe_input(prompt: str, password: bool = False) -> str:
    """
    安全的用户输入
    
    Args:
        prompt: 提示消息
        password: 是否为密码输入
        
    Returns:
        str: 用户输入
    """
    try:
        if password:
            return click.prompt(prompt, hide_input=True)
        else:
            return click.prompt(prompt)
    except (click.Abort, KeyboardInterrupt):
        print("\n操作已取消")
        sys.exit(1)


def retry_on_error(func: Callable, *args: Any, retries: int = 3, delay: float = 1.0, **kwargs: Any) -> Any:
    """
    在发生错误时重试函数
    
    Args:
        func: 要重试的函数
        *args: 函数参数
        retries: 最大重试次数
        delay: 重试之间的延迟（秒）
        **kwargs: 函数关键字参数
        
    Returns:
        Any: 函数返回值
        
    Raises:
        Exception: 如果所有重试都失败，则重新引发最后一个异常
    """
    import time
    last_exception = None
    
    for attempt in range(retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt < retries:
                print_warning(f"操作失败，第{attempt+1}次重试...")
                time.sleep(delay * (attempt + 1))  # 指数回退
            else:
                print_error(f"操作在重试{retries}次后仍然失败: {str(e)}")
                raise last_exception
