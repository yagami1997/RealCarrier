"""
命令处理模块 - 实现各个功能命令的处理逻辑
"""

import os
import sys
import time
import json
import platform
import psutil
import csv
import io
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union

from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TaskProgressColumn, TimeRemainingColumn
from rich.console import Console

from lnptool.ui import UI, console
from lnptool.config import get_api_key, set_api_key, delete_api_key, is_configured, get_config, get_last_used_provider, save_last_used_provider
from lnptool.cache import Cache
from lnptool.lookup import LookupService, display_lookup_result, display_batch_summary
from lnptool.utils import (
    validate_phone_number, validate_csv_file, 
    format_timestamp, print_error, print_warning, 
    print_success, print_info, safe_input, 
    is_valid_api_key, phone_input, format_phone_number
)
from lnptool.i18n import (
    t, set_language, save_language_preference, 
    load_language_preference, get_current_language
)
from lnptool.provider_manager import (
    initialize as init_provider_manager,
    get_provider_status, get_active_provider,
    set_provider_priority, get_provider_priority,
    get_configured_provider_ids, get_provider_by_id,
    lookup_number as provider_lookup_number
)

# 初始化日志记录器
logger = logging.getLogger(__name__)

# 获取UI实例
ui = UI()
console = Console()

def configure_api_key() -> None:
    """API密钥配置命令"""
    ui.clear_screen()
    ui.show_logo()
    
    # 获取提供商状态
    providers = get_provider_status()
    
    # 显示提供商选择菜单
    console.print(f"\n[bold]{t('select_provider_to_configure')}[/bold]\n")
    
    for i, provider in enumerate(providers, 1):
        status_text = f"[green]{t('configured')}[/green]" if provider['configured'] else f"[red]{t('not_configured')}[/red]"
        console.print(f"[bold]{i}.[/bold] {provider['name']} - {status_text}")
    
    console.print(f"[bold]0.[/bold] {t('return_main')}")
    
    # 获取用户选择
    choice = Prompt.ask(
        t('select_option'),
        choices=[str(i) for i in range(len(providers) + 1)],
        default="0"
    )
    
    if choice == "0":
        return
    
    # 获取选择的提供商
    selected_provider = providers[int(choice) - 1]
    
    # 根据提供商类型执行不同的配置
    if selected_provider['id'] == 'twilio':
        _configure_twilio()
    elif selected_provider['id'] == 'telnyx':
        _configure_telnyx()

def _configure_twilio() -> None:
    """配置Twilio API"""
    ui.clear_screen()
    ui.show_logo()
    
    # 获取当前Twilio凭据状态
    from lnptool.twilio_api import check_credentials_status
    creds_status = check_credentials_status()
    
    # 显示当前状态
    console.print(f"\n[bold]Twilio {t('api_config_title')}[/bold]\n")
    
    if creds_status['configured']:
        console.print(f"{t('status')}: {creds_status['message']}")
        console.print(f"Account SID: {creds_status['account_sid']}")
        console.print(f"Auth Token: {creds_status['auth_token']}\n")
        
        # 显示选项
        console.print(f"[bold]1.[/bold] {t('modify_credentials')}")
        console.print(f"[bold]2.[/bold] {t('delete_credentials')}")
    else:
        console.print(f"{t('status')}: {t('not_configured')}\n")
        console.print(f"[bold]1.[/bold] {t('set_credentials')}")
    
    console.print(f"[bold]0.[/bold] {t('return_main')}")
    
    # 获取用户选择
    choice = Prompt.ask(
        t('select_option'),
        choices=["0", "1", "2"] if creds_status['configured'] else ["0", "1"],
        default="0"
    )
    
    if choice == "1":
        # 设置/修改凭据
        console.print(f"\n[bold]{t('enter_twilio_credentials')}[/bold]")
        console.print(t('twilio_credentials_help'))
        print("")  # 空行
        
        # 获取Account SID
        account_sid = safe_input(t('enter_account_sid'))
        if not account_sid:
            return
        
        # 显示输入的Account SID并确认
        console.print(f"\n{t('confirm_account_sid')}: [cyan]{account_sid}[/cyan]")
        if not Confirm.ask(t('is_account_sid_correct')):
            return
        
        # 获取Auth Token
        print("")  # 空行
        console.print(t('auth_token_notice'))
        auth_token = safe_input(t('enter_auth_token'))
        if not auth_token:
            return
        
        # 显示输入的Auth Token并确认
        console.print(f"\n{t('confirm_auth_token')}: [cyan]{auth_token}[/cyan]")
        if not Confirm.ask(t('is_auth_token_correct')):
            return
        
        # 显示最终确认
        print("")  # 空行
        console.print(f"[bold]{t('final_confirmation')}[/bold]")
        console.print(f"Account SID: [cyan]{account_sid}[/cyan]")
        console.print(f"Auth Token: [cyan]{auth_token}[/cyan]")
        
        if Confirm.ask(t('confirm_save_credentials')):
            from lnptool.twilio_api import set_credentials, verify_credentials
            
            # 验证凭据
            print("")  # 空行
            with console.status(t('verifying_credentials')):
                verify_result = verify_credentials(account_sid, auth_token)
            
            if verify_result['valid']:
                if set_credentials(account_sid, auth_token):
                    print_success(t('credentials_saved'))
                else:
                    print_error(t('credentials_save_failed'))
            else:
                print_error(f"{t('invalid_credentials')}: {verify_result['message']}")
    
    elif choice == "2" and creds_status['configured']:
        # 删除凭据
        if Confirm.ask(t('confirm_delete_credentials')):
            from lnptool.twilio_api import delete_credentials
            if delete_credentials():
                print_success(t('credentials_deleted'))
            else:
                print_error(t('credentials_delete_failed'))
    
    # 等待用户按键返回
    input(f"\n{t('press_enter')} {t('to_return')}...")

def _configure_telnyx() -> None:
    """配置Telnyx API"""
    ui.clear_screen()
    ui.show_logo()
    
    # 获取当前API状态
    api_configured = is_configured()
    api_key = get_api_key() if api_configured else None
    
    # 显示API配置菜单
    ui.show_api_config_menu(api_configured, api_key)
    
    # 获取用户选择
    if api_configured:
        choice = Prompt.ask(
            t('select_option'),
            choices=["0", "1", "2"],
            default="0"
        )
        
        if choice == "1":
            # 修改API密钥
            new_key = safe_input(t('enter_api_key'), password=True)
            if new_key:
                if is_valid_api_key(new_key):
                    if set_api_key(new_key):
                        print_success(t('api_key_updated'))
                    else:
                        print_error(t('api_key_update_failed'))
                else:
                    print_error(t('invalid_api_key'))
        
        elif choice == "2":
            # 删除API密钥
            if Confirm.ask(t('confirm_delete_key')):
                if delete_api_key():
                    print_success(t('api_key_deleted'))
                else:
                    print_error(t('api_key_delete_failed'))
    else:
        choice = Prompt.ask(
            t('select_option'),
            choices=["0", "1"],
            default="0"
        )
        
        if choice == "1":
            # 配置API密钥
            new_key = safe_input(t('enter_api_key'), password=True)
            if new_key:
                if is_valid_api_key(new_key):
                    if set_api_key(new_key):
                        print_success(t('api_key_saved'))
                    else:
                        print_error(t('api_key_save_failed'))
                else:
                    print_error(t('invalid_api_key'))
    
    # 等待用户按键返回
    input(f"\n{t('press_enter')} {t('to_return')}...")

def lookup_number() -> None:
    """单个电话号码查询命令"""
    ui.clear_screen()
    ui.show_logo()
    
    console.print(f"[bold]{t('single_lookup_title')}[/bold]\n")
    
    # 检查API配置
    if not is_configured():
        print_error(t('api_not_configured'))
        input(f"\n{t('press_enter')} {t('to_return')}...")
        return
    
    # 获取活跃的提供商
    provider = get_active_provider()
    if not provider:
        print_error(t('no_active_provider'))
        input(f"\n{t('press_enter')} {t('to_return')}...")
        return
    
    # 获取电话号码输入
    phone_number = phone_input(t('enter_phone'))
    if not phone_number:
        return
    
    # 显示查询中提示
    with console.status(f"[bold green]{t('querying')}[/bold green]"):
        # 创建查询服务
        lookup_service = LookupService()
        
        try:
            # 执行查询
            result = lookup_service.lookup_number(phone_number)
            
            # 显示结果
            if result:
                # 转换为字典以便显示
                result_dict = {
                    "phone_number": result.phone_number,
                    "carrier": result.carrier,
                    "line_type": result.line_type,
                    "portable": result.portable,
                    "city": result.city,
                    "state": result.state,
                    "rate_center": result.rate_center,
                    "provider": result.provider
                }
                ui.show_lookup_result(result_dict)
            else:
                print_warning(t('no_result'))
        
        except Exception as e:
            error_msg = str(e)
            # 检查是否是Telnyx 403错误
            if "403账户权限错误" in error_msg:
                error_msg = t("error_telnyx_403")
            # 检查是否是Twilio 10002错误
            elif "Twilio API 运营商错误: 10002" in error_msg:
                error_msg = t("error_twilio_10002")
            
            print_error(f"{t('query_failed')}: {error_msg}")
    
    # 等待用户按键返回
    input(f"\n{t('press_enter')} {t('to_return')}...")

def batch_lookup() -> None:
    """批量查询电话号码"""
    ui.clear_screen()
    ui.show_logo()
    
    # 获取上次使用的API提供商
    last_provider = get_last_used_provider()
    provider_name = "Telnyx" if last_provider == "telnyx" else "Twilio"
    
    console.print(f"\n[bold cyan]{t('current_api_provider')}:[/] [yellow]{provider_name}[/]")
    console.print(f"[bold cyan]{t('switch_api_provider')}?[/]")
    console.print(f"[bold cyan]1.[/] {t('use')} [yellow]Telnyx[/] API")
    console.print(f"[bold cyan]2.[/] {t('use')} [yellow]Twilio[/] API")
    console.print(f"[bold cyan]3.[/] {t('continue_using')} [yellow]{provider_name}[/] API")
    console.print("")
    
    # 默认使用上次的API提供商
    choice = Prompt.ask(t('select_option'), choices=["1", "2", "3"], default="3")
    
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
        ui.show_lookup_error(f"{provider_id.capitalize()} API {t('not_configured_please_configure')}")
        input(f"\n{t('press_enter')} {t('to_continue')}...")
        return
    
    # 获取CSV文件路径
    ui.clear_screen()
    ui.show_logo()
    
    # 显示文件拖拽提示（使用醒目的样式）
    console.print("\n[bold cyan]" + "═" * 60 + "[/bold cyan]")
    console.print("[bold cyan]║[/bold cyan]" + " " * 58 + "[bold cyan]║[/bold cyan]")
    console.print("[bold cyan]║[/bold cyan]    🖱️  " + t('drag_csv_hint') + " " * (48 - len(t('drag_csv_hint'))) + "[bold cyan]║[/bold cyan]")
    console.print("[bold cyan]║[/bold cyan]" + " " * 58 + "[bold cyan]║[/bold cyan]")
    console.print("[bold cyan]" + "═" * 60 + "[/bold cyan]")
    
    console.print(f"\n[bold]{t('enter_csv_path_prompt')}:[/]")
    csv_path = Prompt.ask(t('enter_csv_path'))
    
    # 处理拖拽文件时可能带有的引号和空格
    csv_path = csv_path.strip('"').strip("'").strip()
    
    if not os.path.exists(csv_path):
        ui.show_lookup_error(f"{t('file_not_exist')}: {csv_path}")
        input(f"\n{t('press_enter')} {t('to_continue')}...")
        return
    
    # 获取输出文件路径
    output_path = Prompt.ask(t('enter_output_path'), default=f"{os.path.splitext(csv_path)[0]}_results.csv")
    
    # 读取CSV文件
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            
            # 尝试读取第一行作为表头
            try:
                header = next(reader)
                # 检查第一行是否可能是表头（包含非数字字符的字段）
                is_header = any(not field.strip().isdigit() for field in header if field.strip())
            except StopIteration:
                # 文件为空
                ui.show_lookup_error(t('csv_empty'))
                input(f"\n{t('press_enter')} {t('to_continue')}...")
                return
            
            # 收集电话号码
            phone_numbers = []
            
            # 如果第一行不是表头，也将其添加到电话号码列表中
            if not is_header:
                for field in header:
                    if field and field.strip():
                        try:
                            # 使用format_phone_number处理各种格式
                            raw_number = field.strip()
                            formatted_number = format_phone_number(raw_number)
                            # 添加国际区号
                            if not formatted_number.startswith("+1"):
                                formatted_number = "+1" + formatted_number
                            phone_numbers.append(formatted_number)
                        except ValueError as e:
                            # 记录无效号码但继续处理
                            logger.warning(f"跳过无效号码 {field}: {str(e)}")
            
            # 读取剩余行
            for row in reader:
                if row and row[0]:
                    try:
                        # 使用format_phone_number处理各种格式
                        raw_number = row[0].strip()
                        formatted_number = format_phone_number(raw_number)
                        # 添加国际区号
                        if not formatted_number.startswith("+1"):
                            formatted_number = "+1" + formatted_number
                        phone_numbers.append(formatted_number)
                    except ValueError as e:
                        # 记录无效号码但继续处理
                        logger.warning(f"跳过无效号码 {row[0]}: {str(e)}")
        
        if not phone_numbers:
            ui.show_lookup_error(t('no_valid_phone_numbers'))
            input(f"\n{t('press_enter')} {t('to_continue')}...")
            return
        
        console.print(f"\n[bold]{t('found_phone_numbers').format(count=len(phone_numbers))}[/]")
        if not Confirm.ask(t('confirm_continue')):
            return
        
        # 重定向标准错误输出
        original_stderr = sys.stderr
        sys.stderr = io.StringIO()
        
        # 关闭日志输出到控制台
        original_log_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            # 执行批量查询
            results = []
            errors = []
            
            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(f"[cyan]{t('querying_using_api').format(provider=provider_id.capitalize())}...", total=len(phone_numbers))
                
                for phone in phone_numbers:
                    try:
                        provider_result = provider_lookup_number(phone, provider_id=provider_id)
                        
                        # 如果返回结果是元组，则解包
                        if isinstance(provider_result, tuple):
                            provider, result = provider_result
                        else:
                            result = provider_result
                        
                        if isinstance(result, Exception):
                            error_msg = str(result)
                            # 检查是否是Twilio 10002错误
                            if "Twilio API 运营商错误: 10002" in error_msg:
                                try:
                                    from lnptool.translations import get_translations
                                    from lnptool.i18n import load_language_preference
                                    translations = get_translations()
                                    current_lang = load_language_preference()
                                    # 确保current_lang是有效的语言代码
                                    if not current_lang or current_lang not in translations:
                                        current_lang = "zh_CN"  # 默认使用中文
                                    error_msg = translations[current_lang]["error_twilio_10002"]
                                except Exception as e:
                                    # 如果获取翻译失败，使用硬编码的错误信息
                                    error_msg = t("error_twilio_10002")
                            # 检查是否是Telnyx 403错误
                            elif "403账户权限错误" in error_msg:
                                error_msg = t("error_telnyx_403")
                            
                            # 确保错误信息不为空
                            if not error_msg or error_msg == "None":
                                error_msg = t("unknown_error_check_api")
                            
                            errors.append((phone, error_msg))
                        elif isinstance(result, str):
                            # 如果结果是字符串，可能是错误消息
                            if not result or result == "None":
                                errors.append((phone, t("unknown_error_check_api")))
                            else:
                                errors.append((phone, result))
                        elif result is None:
                            errors.append((phone, t("empty_result_check_api")))
                        elif hasattr(result, 'to_dict'):
                            # 如果结果有to_dict方法，说明是正常的查询结果
                            results.append(result.to_dict())
                        else:
                            # 其他未知类型的结果
                            errors.append((phone, t("unknown_result_type").format(type=type(result))))
                    except Exception as e:
                        # 处理其他任何异常
                        error_msg = str(e)
                        if not error_msg or error_msg == "None":
                            error_msg = t("unknown_exception_check_api")
                        errors.append((phone, error_msg))
                    
                    progress.update(task, advance=1)
                    # 添加延迟以避免API限制
                    time.sleep(0.5)
            
            # 写入结果到CSV
            with open(output_path, 'w', newline='') as f:
                fieldnames = ['phone_number', 'carrier', 'line_type', 'portable']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for result in results:
                    writer.writerow({
                        'phone_number': result.get('phone_number', ''),
                        'carrier': result.get('carrier', ''),
                        'line_type': result.get('line_type', ''),
                        'portable': result.get('portable', '')
                    })
            
            # 显示结果摘要
            ui.show_batch_summary(len(phone_numbers), len(results), len(errors), output_path)
            
            # 如果有错误，询问是否显示
            if errors and Confirm.ask(f"\n{t('show_error_details')}"):
                console.print(f"\n[bold red]{t('error_details')}:[/]")
                for phone, error in errors:
                    # 格式化电话号码
                    import re
                    # 移除所有非数字字符
                    phone_digits = re.sub(r'\D', '', phone)
                    # 如果是11位且以1开头，去掉1
                    if len(phone_digits) == 11 and phone_digits.startswith('1'):
                        phone_digits = phone_digits[1:]
                    # 如果是10位，则格式化为(XXX) XXX-XXXX
                    if len(phone_digits) == 10:
                        display_phone = format_phone_number(phone_digits)
                    else:
                        display_phone = phone
                    
                    console.print(f"[red]{display_phone}:[/] {error}")
        finally:
            # 恢复标准错误输出和日志级别
            sys.stderr = original_stderr
            logging.getLogger().setLevel(original_log_level)
        
    except Exception as e:
        ui.show_lookup_error(f"{t('batch_lookup_failed')}: {str(e)}")
    
    # 等待用户按键返回
    input(f"\n{t('press_enter')} {t('to_return')}...")

def cache_management() -> None:
    """缓存管理命令"""
    ui.clear_screen()
    ui.show_logo()
    
    console.print(f"[bold]{t('cache_management')}[/bold]\n")
    
    # 创建缓存实例
    cache = Cache()
    
    # 获取缓存统计
    stats = cache.get_stats()
    
    # 显示缓存统计
    ui.show_cache_stats(stats)
    
    # 显示菜单选项
    console.print(f"\n[bold]1.[/bold] {t('clear_cache')}")
    console.print(f"[bold]0.[/bold] {t('return_main')}")
    
    # 获取用户选择
    choice = Prompt.ask(
        t('select_option'),
        choices=["0", "1"],
        default="0"
    )
    
    if choice == "1":
        # 清除缓存
        if Confirm.ask(t('confirm_clear_cache')):
            cache.clear()
            print_success(t('cache_cleared'))
    
    # 等待用户按键返回
    input(f"\n{t('press_enter')} {t('to_return')}...")

def system_info() -> None:
    """系统信息命令"""
    ui.clear_screen()
    ui.show_logo()
    
    console.print(f"[bold]{t('system_info')}[/bold]\n")
    
    # 收集系统信息
    api_status = t('yes') if is_configured() else t('no')
    providers_status = get_provider_status()
    provider_info = []
    for provider in providers_status:
        provider_info.append(f"{provider['name']} ({provider['id']})")
    
    # 获取更准确的操作系统信息
    os_name = platform.system()
    os_version = ""
    kernel_version = ""
    
    if os_name == "Darwin":
        # macOS
        try:
            # 获取macOS版本
            try:
                mac_ver = platform.mac_ver()[0]
                
                # 根据版本号确定macOS名称
                version_map = {
                    "10.15": "Catalina",
                    "11": "Big Sur",
                    "12": "Monterey",
                    "13": "Ventura",
                    "14": "Sonoma"
                }
                
                major_version = mac_ver.split(".")[0]
                if major_version == "10":
                    minor_version = mac_ver.split(".")[1]
                    version_key = f"10.{minor_version}"
                else:
                    version_key = major_version
                
                if version_key in version_map:
                    os_version = version_map[version_key]
                else:
                    os_version = mac_ver
                
                kernel_version = f"Darwin {platform.release()}"
            except Exception as e:
                logger.error(f"{t('failed_get_macos_version')}: {e}")
                kernel_version = f"Darwin {platform.release()}"
        except Exception as e:
            logger.error(f"{t('failed_get_macos_version')}: {e}")
            kernel_version = f"Darwin {platform.release()}"
    elif os_name == "Windows":
        # Windows
        try:
            win_ver = platform.version()
            if "10.0" in win_ver:
                # 检查是否为Windows 11
                build = int(win_ver.split('.')[-1]) if win_ver.split('.')[-1].isdigit() else 0
                if build >= 22000:
                    os_name = "Windows 11"
                else:
                    os_name = "Windows 10"
            os_version = f"Build {win_ver.split('.')[-1]}"
            kernel_version = f"Windows NT {'.'.join(win_ver.split('.')[:2])}"
        except Exception as e:
            logger.error(f"{t('failed_get_windows_version')}: {e}")
            kernel_version = f"Windows NT {platform.release()}"
    elif os_name == "Linux":
        # Linux
        try:
            # 尝试使用platform模块获取Linux发行版信息
            linux_distro = platform.platform()
            os_name = linux_distro.split('-')[0]
            # 获取Linux内核版本
            kernel_info = platform.release()
            kernel_version = f"Linux {kernel_info.split('-')[0]}"
        except Exception as e:
            logger.error(f"{t('failed_get_linux_distro')}: {e}")
            kernel_version = f"Linux {platform.release()}"
    
    # 获取更准确的CPU信息
    cpu_info = platform.processor() or "Unknown"
    
    # 根据操作系统获取CPU信息
    try:
        if os_name == "Darwin":
            # 对于macOS，尝试获取Apple Silicon或Intel处理器信息
            import subprocess
            
            # 尝试使用sysctl获取处理器信息
            try:
                # 首先尝试获取处理器品牌字符串
                cpu_brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
                if cpu_brand:
                    cpu_info = cpu_brand
                    # 如果成功获取到处理器品牌，不需要继续尝试其他方法
                else:
                    # 如果无法获取处理器品牌，尝试获取设备型号
                    model = subprocess.check_output(["sysctl", "-n", "hw.model"]).decode().strip()
                    # 根据设备型号推断芯片型号
                    if "MacBookPro18" in model:
                        cpu_info = "Apple M1 Pro/Max"
                    elif "MacBookPro17" in model:
                        cpu_info = "Apple M1 Pro/Max"
                    elif "MacBookAir10" in model:
                        cpu_info = "Apple M1"
                    elif "Mac14" in model:
                        cpu_info = "Apple M2"
                    elif "Mac13" in model:
                        cpu_info = "Apple M1"
                    else:
                        # 如果无法推断芯片型号，使用架构信息
                        arch = subprocess.check_output(["uname", "-m"]).decode().strip()
                        if arch == "arm64":
                            cpu_info = "Apple Silicon"
                        else:
                            cpu_info = f"Intel {arch}"
            except Exception as e:
                # 如果无法使用sysctl，尝试使用uname -m获取架构
                try:
                    arch = subprocess.check_output(["uname", "-m"]).decode().strip()
                    if arch == "arm64":
                        cpu_info = "Apple Silicon"
                    else:
                        cpu_info = f"Intel {arch}"
                except Exception as e:
                    logger.error(f"{t('failed_get_macos_cpu_info')}: {e}")
                    # 如果所有方法都失败，使用platform.machine()
                    machine = platform.machine()
                    if machine == "arm64":
                        cpu_info = "Apple Silicon"
                    else:
                        cpu_info = machine
        
        elif os_name.startswith("Windows"):
            # 对于Windows，从注册表获取CPU信息
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_info = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
            except Exception as e:
                logger.error(f"{t('failed_get_windows_cpu_info')}: {e}")
        
        elif os_name.startswith("Linux"):
            # 对于Linux，从/proc/cpuinfo获取CPU信息
            try:
                import re
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if line.startswith("model name"):
                            cpu_info = re.sub(".*model name.*:", "", line, 1).strip()
                            break
            except Exception as e:
                logger.error(f"{t('failed_get_linux_cpu_info')}: {e}")
    except Exception as e:
        logger.error(f"{t('failed_get_cpu_info')}: {e}")
    
    # 获取系统信息
    info = {
        'os': f"macOS {os_version}" if os_name == "Darwin" else os_name,
        'kernel': kernel_version,
        'python': platform.python_version(),
        'cpu': cpu_info,
        'memory': f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
        'app_version': 'Beta v1.0.0',
        'api_status': api_status,
        'providers': provider_info
    }
    
    # 获取提供商状态
    active_providers = [p['id'] for p in providers_status if p['active']]
    configured_providers = [p['id'] for p in providers_status if p['configured']]
    
    info['active_providers'] = ', '.join(active_providers) if active_providers else t('none')
    info['configured_providers'] = ', '.join(configured_providers) if configured_providers else t('none')
    
    # 获取缓存统计
    cache = Cache()
    cache_stats = cache.get_stats()
    
    info['cache_entries'] = cache_stats['total_entries']
    info['cache_size'] = f"{cache_stats['cache_size_bytes'] / 1024:.2f} KB"
    
    # 显示系统信息
    ui.show_system_info(info)
    
    # 等待用户按键返回
    input(f"\n{t('press_enter')} {t('to_return')}...")

def language_settings() -> None:
    """语言设置命令"""
    ui.clear_screen()
    ui.show_logo()
    
    # 获取当前语言
    current_lang = get_current_language()
    
    # 显示语言设置菜单
    ui.show_language_settings(current_lang)
    
    # 获取用户选择
    choice = Prompt.ask(
        t('select_option'),
        choices=["0", "1", "2"],
        default="0"
    )
    
    # 处理选择
    if choice == "1":
        # 切换到中文
        if current_lang != "zh_CN":
            if set_language("zh_CN"):
                if save_language_preference("zh_CN"):
                    print_success(t("language_changed") + " " + t("language_zh"))
                else:
                    print_warning(t("unable_save") + " " + t("language_zh"))
        else:
            print_info(t("already_using") + " " + t("language_zh"))
    
    elif choice == "2":
        # 切换到英文
        if current_lang != "en_US":
            if set_language("en_US"):
                if save_language_preference("en_US"):
                    print_success(t("language_changed") + " " + t("language_en"))
                else:
                    print_warning(t("unable_save") + " " + t("language_en"))
        else:
            print_info(t("already_using") + " " + t("language_en"))
    
    # 等待用户按键返回
    input(f"\n{t('press_enter')} {t('to_return')}...")

def provider_settings() -> None:
    """提供商设置命令"""
    ui.clear_screen()
    ui.show_logo()
    
    console.print(f"[bold]{t('provider_settings')}[/bold]\n")
    
    # 获取提供商状态
    providers_status = get_provider_status()
    
    # 显示提供商状态
    for provider in providers_status:
        status_text = f"[green]{t('active')}[/green]" if provider['active'] else f"[dim]{t('inactive')}[/dim]"
        config_text = f"[green]{t('configured')}[/green]" if provider['configured'] else f"[red]{t('not_configured')}[/red]"
        
        console.print(f"[bold]{provider['name']}[/bold] ({provider['id']})")
        console.print(f"  {t('status')}: {status_text}")
        console.print(f"  {t('configuration')}: {config_text}")
        console.print("")
    
    # 显示当前优先级
    priority = get_provider_priority()
    console.print(f"{t('current_priority')}: [cyan]{', '.join(priority)}[/cyan]\n")
    
    # 显示菜单选项
    console.print(f"[bold]1.[/bold] {t('change_priority')}")
    console.print(f"[bold]2.[/bold] {t('configure_provider')}")
    console.print(f"[bold]0.[/bold] {t('return_main')}")
    
    # 获取用户选择
    choice = Prompt.ask(
        t('select_option'),
        choices=["0", "1", "2"],
        default="0"
    )
    
    if choice == "1":
        # 更改优先级
        configured_providers = get_configured_provider_ids()
        
        if not configured_providers:
            print_error(t('no_configured_providers'))
        else:
            # 显示可用提供商
            console.print(f"\n{t('available_providers')}:")
            for i, provider_id in enumerate(configured_providers):
                console.print(f"  {i+1}. {provider_id}")
            
            # 获取新的优先级
            priority_input = Prompt.ask(
                t('enter_priority'),
                default=",".join(configured_providers)
            )
            
            # 解析输入
            new_priority = [p.strip() for p in priority_input.split(",")]
            
            # 验证输入
            valid = all(p in configured_providers for p in new_priority)
            
            if valid:
                # 设置新的优先级
                if set_provider_priority(new_priority):
                    print_success(t('priority_updated'))
                else:
                    print_error(t('priority_update_failed'))
            else:
                print_error(t('invalid_priority'))
    
    elif choice == "2":
        # 配置提供商
        # 显示可用提供商
        console.print(f"\n{t('available_providers')}:")
        for i, provider in enumerate(providers_status):
            console.print(f"  {i+1}. {provider['name']} ({provider['id']})")
        
        # 获取提供商选择
        provider_idx = Prompt.ask(
            t('select_provider'),
            choices=[str(i+1) for i in range(len(providers_status))],
            default="1"
        )
        
        # 获取选择的提供商
        selected_provider = providers_status[int(provider_idx) - 1]
        
        # 根据提供商类型执行不同的配置
        if selected_provider['id'] == 'twilio':
            # 配置Twilio
            from lnptool.twilio_api import set_credentials, delete_credentials
            
            # 显示Twilio配置选项
            console.print(f"\n[bold]Twilio {t('configuration')}[/bold]\n")
            console.print(f"[bold]1.[/bold] {t('set_credentials')}")
            console.print(f"[bold]2.[/bold] {t('delete_credentials')}")
            console.print(f"[bold]0.[/bold] {t('cancel')}")
            
            # 获取用户选择
            twilio_choice = Prompt.ask(
                t('select_option'),
                choices=["0", "1", "2"],
                default="0"
            )
            
            if twilio_choice == "1":
                # 设置凭据
                account_sid = safe_input(t('enter_account_sid'))
                auth_token = safe_input(t('enter_auth_token'), password=True)
                
                if account_sid and auth_token:
                    if set_credentials(account_sid, auth_token):
                        print_success(t('credentials_saved'))
                    else:
                        print_error(t('credentials_save_failed'))
            
            elif twilio_choice == "2":
                # 删除凭据
                if Confirm.ask(t('confirm_delete_credentials')):
                    if delete_credentials():
                        print_success(t('credentials_deleted'))
                    else:
                        print_error(t('credentials_delete_failed'))
        
        elif selected_provider['id'] == 'telnyx':
            # 配置Telnyx
            # 显示Telnyx配置选项
            console.print(f"\n[bold]Telnyx {t('configuration')}[/bold]\n")
            console.print(f"[bold]1.[/bold] {t('set_api_key')}")
            console.print(f"[bold]2.[/bold] {t('delete_api_key')}")
            console.print(f"[bold]0.[/bold] {t('cancel')}")
            
            # 获取用户选择
            telnyx_choice = Prompt.ask(
                t('select_option'),
                choices=["0", "1", "2"],
                default="0"
            )
            
            if telnyx_choice == "1":
                # 设置API密钥
                api_key = safe_input(t('enter_api_key'), password=True)
                
                if api_key:
                    if is_valid_api_key(api_key):
                        if set_api_key(api_key):
                            print_success(t('api_key_saved'))
                        else:
                            print_error(t('api_key_save_failed'))
                    else:
                        print_error(t('invalid_api_key'))
            
            elif telnyx_choice == "2":
                # 删除API密钥
                if Confirm.ask(t('confirm_delete_key')):
                    if delete_api_key():
                        print_success(t('api_key_deleted'))
                    else:
                        print_error(t('api_key_delete_failed'))
    
    # 等待用户按键返回
    input(f"\n{t('press_enter')} {t('to_return')}...") 