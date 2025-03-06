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
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()

try:
    from lnptool.i18n import t
except ImportError:
    # 如果i18n模块尚未创建，提供一个简单的代替函数
    def t(key):
        return key


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


def validate_phone_number(ctx: click.Context = None, param: click.Parameter = None, value: str = None) -> str:
    """
    验证电话号码格式，支持Click回调和直接调用两种方式
    
    Args:
        ctx: Click上下文（可选）
        param: 参数对象（可选）
        value: 电话号码
        
    Returns:
        str: 有效的电话号码
        
    Raises:
        click.BadParameter: 如果作为Click回调使用且电话号码格式无效
        ValueError: 如果直接调用且电话号码格式无效
    """
    if not value:
        return value
    
    # 帮助用户处理常见的美国电话号码格式
    # 比如 (626)630-8117 或 626-630-8117 等
    
    # 移除所有非数字字符
    digits_only = ''.join(c for c in value if c.isdigit())
    
    # 验证格式
    if len(digits_only) not in (10, 11) or (len(digits_only) == 11 and not digits_only.startswith('1')):
        error_msg = "请提供有效的美国电话号码，格式为10位数字或以1开头的11位数字"
        if ctx:
            # 作为Click回调使用
            raise click.BadParameter(error_msg)
        else:
            # 直接调用
            raise ValueError(error_msg)
    
    # 格式化为E.164格式
    if len(digits_only) == 10:
        formatted = f"+1{digits_only}"
        formatted_display = f"({digits_only[:3]}){digits_only[3:6]}-{digits_only[6:]}"
    else:  # 11位数字且以1开头
        # 确保使用后10位数字，避免重复国家代码
        formatted = f"+1{digits_only[1:]}"
        formatted_display = f"({digits_only[1:4]}){digits_only[4:7]}-{digits_only[7:]}"
    
    # 显示友好提示
    if ctx:
        click.echo(f"您要查询的电话号码是: {formatted_display}")
        
        # 确认是否继续
        if click.confirm("是否继续?", default=True):
            return formatted
        else:
            click.echo("操作已取消")
            sys.exit(0)
    
    return formatted


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


def format_phone_number(phone_digits: str) -> str:
    """
    将10位电话号码格式化为(XXX) XXX-XXXX格式
    
    Args:
        phone_digits: 10位电话号码数字
        
    Returns:
        str: 格式化后的电话号码
    """
    if len(phone_digits) == 10:
        return f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
    else:
        return phone_digits  # 如果不是10位，则返回原始数字


def phone_input(prompt_text: str, use_rich: bool = True) -> str:
    """
    获取用户输入的电话号码，并进行格式化
    
    Args:
        prompt_text: 提示文本
        use_rich: 是否使用Rich库进行格式化输出
        
    Returns:
        str: 格式化后的电话号码，如果用户取消则返回空字符串
    """
    from lnptool.i18n import t
    
    while True:
        # 获取用户输入
        if use_rich:
            phone = Prompt.ask(prompt_text)
        else:
            print(prompt_text)
            phone = input("> ")
        
        # 如果用户输入为空，视为取消
        if not phone:
            print_info(t("operation_cancelled"))
            return ""
        
        # 移除所有非数字字符
        phone_digits = re.sub(r'\D', '', phone)
        
        # 检查是否是美国号码
        if len(phone_digits) == 10:
            # 添加美国国家代码（用于API查询）
            formatted_phone = f"+1{phone_digits}"
            # 创建显示用的格式化电话号码
            display_phone = format_phone_number(phone_digits)
            
            if use_rich:
                console.print(f"{t('plus_1_added')}: [bold]{display_phone}[/bold]")
            else:
                print(f"{t('plus_1_added')}: {display_phone}")
            
            # 确认号码
            if use_rich:
                ui = __import__('lnptool.ui', fromlist=['UI']).UI
                ui.show_phone_confirmation(display_phone)
                if Confirm.ask(f"{t('confirm_continue')}"):
                    return formatted_phone
                else:
                    print_info(t("input_cancelled"))
            else:
                print(f"{t('phone_you_entered')}: {display_phone}")
                confirm = input(f"{t('confirm_continue')} (y/n): ").lower()
                if confirm in ['y', 'yes']:
                    return formatted_phone
                else:
                    print_info(t("input_cancelled"))
        
        # 检查是否已经包含国家代码
        elif len(phone_digits) == 11 and phone_digits.startswith('1'):
            formatted_phone = f"+{phone_digits}"
            if use_rich:
                if Confirm.ask(f"{t('phone_you_entered')}: {formatted_phone}. {t('confirm_continue')}"):
                    return formatted_phone
                else:
                    print_info(t("input_cancelled"))
            else:
                print(f"{t('phone_you_entered')}: {formatted_phone}")
                confirm = input(f"{t('confirm_continue')} (y/n): ").lower()
                if confirm in ['y', 'yes']:
                    return formatted_phone
                else:
                    print_info(t("input_cancelled"))
        
        # 检查是否已经是完整的国际格式
        elif phone.startswith('+1') and len(phone_digits) == 11:
            formatted_phone = f"+{phone_digits}"
            if use_rich:
                if Confirm.ask(f"{t('phone_you_entered')}: {formatted_phone}. {t('confirm_continue')}"):
                    return formatted_phone
                else:
                    print_info(t("input_cancelled"))
            else:
                print(f"{t('phone_you_entered')}: {formatted_phone}")
                confirm = input(f"{t('confirm_continue')} (y/n): ").lower()
                if confirm in ['y', 'yes']:
                    return formatted_phone
                else:
                    print_info(t("input_cancelled"))
        
        # 格式不正确
        else:
            print_warning(t("incorrect_number_format"))


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


def clear_screen() -> None:
    """
    清除终端屏幕
    """
    os.system('cls' if os.name == 'nt' else 'clear')
