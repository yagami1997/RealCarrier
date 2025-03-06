#!/usr/bin/env python3
"""
RealCarrier - 美国电话号码查询工具
支持多API接口 (Telnyx & Twilio)
Beta 1.0.0
"""

import sys
import logging
import traceback
from pathlib import Path
import re
import io
import time

from rich.console import Console
from rich.prompt import Prompt, Confirm

# 初始化日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入模块
from lnptool.ui import UI
from lnptool.commands import (
    configure_api_key, lookup_number, batch_lookup,
    cache_management, system_info, language_settings,
    provider_settings
)
from lnptool.i18n import t, set_translations, load_language_preference
from lnptool.translations import get_translations
from lnptool.utils import print_error, print_success, print_info, print_warning
from lnptool.provider_manager import initialize as init_provider_manager, get_provider_status, get_provider_by_id, lookup_number as provider_lookup_number
from lnptool.config import ensure_config_dir, save_last_used_provider, get_last_used_provider

# 获取UI实例
ui = UI()
console = Console()

def initialize_app():
    """初始化应用程序"""
    try:
        # 确保配置目录存在
        ensure_config_dir()
        
        # 初始化翻译库
        set_translations(get_translations())
        
        # 加载语言偏好设置
        load_language_preference()
        
        # 初始化提供商管理模块
        init_provider_manager()
        
        # 检查提供商状态
        providers = get_provider_status()
        active_providers = [p for p in providers if p['active']]
        
        if not active_providers:
            print_warning(t('no_active_provider'))
        else:
            print_info(t('active_providers') + ": " + ", ".join(p['name'] for p in active_providers))
            
    except Exception as e:
        logger.error(f"初始化失败: {e}", exc_info=True)
        print_error(f"{t('init_failed')}: {str(e)}")
        return False
    
    return True

def lookup_single_number():
    """查询单个电话号码"""
    while True:
        # 清屏并显示菜单
        ui.clear_screen()
        ui.show_logo()
        
        # 获取上次使用的API提供商
        last_provider = get_last_used_provider()
        
        # 显示菜单，包含上次使用的API提供商选项
        ui.show_single_lookup_menu(last_provider)
        
        # 获取用户选择
        choices = ["0", "1", "2"]
        default_choice = "0"
        
        if last_provider:
            choices.append("3")
            # 设置默认选项为使用上次的API提供商
            default_choice = "3"
        
        choice = Prompt.ask("请选择操作", choices=choices, default=default_choice)
        
        if choice == "0":
            return
        
        # 选择查询接口
        if choice == "1":
            provider_id = "telnyx"
        elif choice == "2":
            provider_id = "twilio"
        else:  # choice == "3"
            provider_id = last_provider
        
        # 保存当前选择的API提供商
        save_last_used_provider(provider_id)
        
        # 检查选择的接口是否已配置
        provider = get_provider_by_id(provider_id)
        if not provider:
            ui.show_lookup_error(f"{provider_id.capitalize()} API 未配置，请先完成配置")
            input("\n按 Enter 键继续...")
            continue
        
        # 获取电话号码
        ui.clear_screen()
        ui.show_logo()
        ui.show_phone_input()
        
        phone = Prompt.ask("电话号码")
        
        # 格式化电话号码
        try:
            if not phone.startswith("+1"):
                phone = "+1" + phone.strip()
            
            # 验证格式
            if not re.match(r'^\+1\d{10}$', phone):
                raise ValueError("无效的电话号码格式")
            
            # 显示确认
            ui.show_phone_confirmation(phone)
            if not Confirm.ask("确认继续"):
                continue
            
            # 显示查询进度
            ui.show_lookup_progress()
            
            # 重定向标准错误输出
            original_stderr = sys.stderr
            sys.stderr = io.StringIO()
            
            # 关闭日志输出到控制台
            original_log_level = logging.getLogger().level
            logging.getLogger().setLevel(logging.CRITICAL)
            
            try:
                # 执行查询
                try:
                    provider_result = provider_lookup_number(phone, provider_id=provider_id)
                    
                    # 如果返回结果是元组，则解包
                    if isinstance(provider_result, tuple) and len(provider_result) == 2:
                        provider, result = provider_result
                    else:
                        result = provider_result
                    
                    # 处理各种可能的结果类型
                    if result is None:
                        ui.show_lookup_error("查询结果为空，请检查API配置和网络连接")
                    elif isinstance(result, Exception):
                        error_msg = str(result)
                        if not error_msg or error_msg == "None":
                            error_msg = "未知错误，请检查API配置和网络连接"
                        
                        # 检查是否是Twilio 10002错误
                        if "Twilio API 运营商错误: 10002" in error_msg:
                            try:
                                from lnptool.translations import get_translations
                                translations = get_translations()
                                current_lang = load_language_preference()
                                # 确保current_lang是有效的语言代码
                                if not current_lang or current_lang not in translations:
                                    current_lang = "zh_CN"  # 默认使用中文
                                error_msg = translations[current_lang]["error_twilio_10002"]
                            except Exception as e:
                                # 如果获取翻译失败，使用硬编码的错误信息
                                error_msg = "Twilio API 运营商错误: 10002，试用版Twilio无法跨区域发送消息，请升级账户或联系客户服务解决"
                        
                        ui.show_lookup_error(error_msg)
                    elif isinstance(result, str):
                        # 如果结果是字符串，可能是错误消息
                        if not result or result == "None":
                            ui.show_lookup_error("未知错误，请检查API配置和网络连接")
                        else:
                            ui.show_lookup_error(result)
                    elif hasattr(result, 'to_dict'):
                        # 如果结果有to_dict方法，说明是正常的查询结果
                        ui.show_lookup_result(result.to_dict())
                    else:
                        # 其他未知类型的结果
                        ui.show_lookup_error(f"未知的结果类型: {type(result)}")
                except Exception as query_error:
                    # 捕获查询过程中的任何异常
                    error_msg = str(query_error)
                    error_type = type(query_error).__name__
                    error_traceback = traceback.format_exc()
                    
                    # 记录详细的错误信息到日志文件
                    with open("error_log.txt", "a") as f:
                        f.write(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"电话号码: {phone}\n")
                        f.write(f"提供商: {provider_id}\n")
                        f.write(f"错误类型: {error_type}\n")
                        f.write(f"错误信息: {error_msg}\n")
                        f.write(f"错误堆栈: {error_traceback}\n")
                        f.write("-" * 80 + "\n")
                    
                    if not error_msg or error_msg == "None":
                        error_msg = f"查询过程中发生错误: {error_type}"
                    
                    ui.show_lookup_error(f"{error_msg}\n请查看error_log.txt获取详细信息")
            finally:
                # 恢复标准错误输出
                sys.stderr = original_stderr
                
                # 恢复日志级别
                logging.getLogger().setLevel(original_log_level)
            
        except ValueError as e:
            # 处理电话号码格式错误
            error_msg = str(e)
            if not error_msg or error_msg == "None":
                error_msg = "电话号码格式无效"
            ui.show_lookup_error(error_msg)
        except Exception as e:
            # 处理其他任何异常
            error_msg = str(e)
            if not error_msg or error_msg == "None":
                error_msg = "发生未知错误，请检查API配置和网络连接"
            ui.show_lookup_error(error_msg)
        
        # 等待用户确认返回
        ui.show_return_prompt()
        input()

def main():
    """主函数入口"""
    try:
        # 初始化应用
        if not initialize_app():
            input(f"\n{t('press_enter')} {t('to_exit')}...")
            return
        
        # 程序主循环
        while True:
            ui.clear_screen()
            ui.show_logo()
            ui.show_main_menu()
            
            choice = Prompt.ask(
                t('select_option'),
                choices=["0", "1", "2", "3", "4", "5", "6"],
                default="0"
            )
            
            # 处理用户选择
            if choice == "1":
                configure_api_key()
            elif choice == "2":
                lookup_single_number()
            elif choice == "3":
                batch_lookup()
            elif choice == "4":
                cache_management()
            elif choice == "5":
                system_info()
            elif choice == "6":
                language_settings()
            elif choice == "0":
                print_success(t('goodbye'))
                break
    
    except KeyboardInterrupt:
        ui.clear_screen()
        console.print(f"[bold green]{t('goodbye')}[/bold green]")
    
    except Exception as e:
        logger.error(f"未处理的异常: {e}", exc_info=True)
        traceback.print_exc()
        print_error(f"{t('program_error')}: {str(e)}")
        input(f"\n{t('press_any_key')}...")

if __name__ == "__main__":
    main() 