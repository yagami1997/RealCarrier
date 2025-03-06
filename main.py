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
import csv
import os
import importlib.util

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.style import Style

from lnptool.phone_utils import format_phone_number

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

def batch_query():
    """批量查询电话号码"""
    console = Console()
    
    # 清屏并显示标题
    ui.clear_screen()
    ui.show_logo()
    console.print("\n[bold]📊 批量查询[/bold]\n")
    
    # 预先安装所有必要的依赖
    try:
        # 使用importlib.util.find_spec检查模块是否已安装
        import importlib.util
        
        # 检查是否需要安装pandas和Excel引擎
        missing_deps = []
        if importlib.util.find_spec("pandas") is None:
            missing_deps.append("pandas")
        
        if importlib.util.find_spec("openpyxl") is None:
            missing_deps.append("openpyxl")
        
        if importlib.util.find_spec("xlrd") is None:
            missing_deps.append("xlrd")
        
        # 如果有缺失的依赖，提示用户安装
        if missing_deps:
            console.print(f"[yellow]{t('missing_dependencies')}: {', '.join(missing_deps)}[/yellow]")
            if Confirm.ask(t('install_dependencies')):
                console.print(f"[yellow]{t('installing_dependencies')}...[/yellow]")
                import subprocess
                try:
                    for dep in missing_deps:
                        console.print(f"[yellow]{t('installing')}: {dep}...[/yellow]")
                        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                    console.print(f"[green]{t('dependencies_installed')}[/green]")
                except Exception as e:
                    console.print(f"[red]{t('error_installing_dependencies')}: {str(e)}[/red]")
                    # 继续执行，可能部分功能受限
            else:
                console.print(f"[yellow]{t('continue_without_dependencies')}[/yellow]")
                # 继续执行，可能部分功能受限
    except Exception as e:
        console.print(f"[red]{t('error_checking_dependencies')}: {str(e)}[/red]")
        # 继续执行，可能部分功能受限
    
    # 使用水印暗纹提示文件拖拽（不使用边框）
    console.print("\n\n", style="")  # 添加空行
    console.print(f"🖱️  {t('drag_csv_hint')}", style="dim italic")
    console.print("\n", style="")  # 添加空行
    
    # 获取CSV文件路径
    while True:
        try:
            csv_path = input(f"\n{t('input_csv_path')}: ").strip()
            # 处理拖拽文件时可能带有的引号和空格
            csv_path = csv_path.strip('"').strip("'").strip()
            
            if not csv_path:
                console.print("[yellow]" + t('please_enter_file_path') + "[/yellow]")
                continue
                
            if not Path(csv_path).exists():
                console.print(f"[red]{t('error_file_not_found')}: {csv_path}[/red]")
                if not Confirm.ask(t('retry_input')):
                    return
                continue
            break
        except KeyboardInterrupt:
            return
        except Exception as e:
            console.print(f"[red]{t('error')}: {str(e)}[/red]")
            if not Confirm.ask(t('retry_input')):
                return
    
    # 自动设置默认输出路径
    default_output_path = f"{os.path.splitext(csv_path)[0]}_results.csv"
    output_path = default_output_path
    
    # 确保输出目录存在
    output_dir = Path(output_path).parent
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            console.print(f"[red]{t('error_creating_output_dir')}: {str(e)}[/red]")
            return
    
    phone_numbers = []
    
    # 读取文件（支持CSV和Excel）
    file_ext = os.path.splitext(csv_path)[1].lower()
    
    try:
        if file_ext in ['.xlsx', '.xls']:
            # 处理Excel文件
            console.print(f"[yellow]{t('reading_excel')}...[/yellow]")
            
            try:
                # 直接尝试读取Excel文件，不再检查依赖
                import pandas as pd
                
                # 根据文件扩展名选择引擎
                engine = 'openpyxl' if file_ext == '.xlsx' else 'xlrd'
                
                # 读取Excel文件
                df = pd.read_excel(csv_path, engine=engine)
                console.print(f"[green]{t('excel_read_success')}: {len(df)} {t('rows_found')}[/green]")
                
                # 遍历所有单元格寻找电话号码
                for _, row in df.iterrows():
                    for cell in row:
                        if pd.notna(cell):  # 跳过NaN值
                            cell_str = str(cell).strip()
                            if cell_str:  # 跳过空字符串
                                try:
                                    # 尝试格式化电话号码
                                    formatted_number = format_phone_number(cell_str)
                                    phone_numbers.append(formatted_number)
                                except:
                                    # 静默跳过无效号码
                                    pass
            except ImportError as e:
                # 如果依赖缺失，提示用户并继续使用CSV
                console.print(f"[red]{t('error_excel_support')}: {str(e)}[/red]")
                console.print(f"[yellow]{t('try_csv_instead')}[/yellow]")
            except Exception as e:
                # 其他错误
                console.print(f"[red]{t('error_reading_excel')}: {str(e)}[/red]")
                console.print(f"[yellow]{t('try_csv_instead')}[/yellow]")
        else:
            # 处理CSV文件
            with open(csv_path, 'r') as f:
                # 尝试检测分隔符
                sample = f.read(1024)
                f.seek(0)
                
                # 检测可能的分隔符
                if ',' in sample:
                    delimiter = ','
                elif ';' in sample:
                    delimiter = ';'
                elif '\t' in sample:
                    delimiter = '\t'
                else:
                    delimiter = ','  # 默认使用逗号
                
                reader = csv.reader(f, delimiter=delimiter)
                
                # 遍历所有行和列寻找电话号码
                for row in reader:
                    for cell in row:
                        cell = cell.strip()
                        if cell:  # 跳过空单元格
                            try:
                                # 尝试格式化电话号码
                                formatted_number = format_phone_number(cell)
                                phone_numbers.append(formatted_number)
                            except:
                                # 静默跳过无效号码
                                pass
    except Exception as e:
        console.print(f"[red]{t('error_reading_file')}: {str(e)}[/red]")
        return
    
    # 去除重复号码
    phone_numbers = list(dict.fromkeys(phone_numbers))
    
    if not phone_numbers:
        console.print(f"[yellow]{t('warning_no_valid_numbers')}[/yellow]")
        return
    
    # 获取当前API提供商
    provider_id = get_last_used_provider()
    if not provider_id:
        console.print(f"[red]{t('error_no_api_provider')}[/red]")
        return
    
    # 显示找到的号码数量并确认
    console.print(f"\n[green]{t('found_numbers').format(count=len(phone_numbers))}[/green]")
    console.print(f"[green]{t('output_will_be_saved_to')}: {output_path}[/green]")
    
    if not Confirm.ask(t('confirm_continue')):
        return
    
    # 执行批量查询
    results = []
    success_count = 0
    error_count = 0
    total = len(phone_numbers)
    
    # 重定向标准错误输出，避免显示API错误
    original_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    # 关闭日志输出到控制台
    original_log_level = logging.getLogger().level
    logging.getLogger().setLevel(logging.CRITICAL)
    
    try:
        with console.status(f"[bold green]{t('querying_progress').format(completed=0, total=total)}") as status:
            for i, phone in enumerate(phone_numbers, 1):
                try:
                    status.update(f"[bold green]{t('querying_progress').format(completed=i, total=total)}")
                    result = provider_lookup_number(phone, provider_id=provider_id)
                    
                    if isinstance(result, Exception):
                        # 记录错误但不显示
                        error_count += 1
                        error_msg = str(result)
                        detailed_error = get_error_description(error_msg, provider_id)
                        results.append({
                            "phone": phone,
                            "status": "error",
                            "carrier": "-",
                            "line_type": "-",
                            "portable": "-",
                            "error": detailed_error
                        })
                    elif isinstance(result, tuple):
                        # 处理返回元组的情况
                        # 尝试从元组中提取有用信息
                        if len(result) >= 2:
                            # 通常元组的第一个元素是提供商ID，第二个元素是结果或错误
                            second_element = result[1]
                            
                            if isinstance(second_element, Exception):
                                # 如果第二个元素是异常，提取错误信息
                                error_count += 1
                                error_msg = str(second_element)
                                detailed_error = get_error_description(error_msg, provider_id)
                                results.append({
                                    "phone": phone,
                                    "status": "error",
                                    "carrier": "-",
                                    "line_type": "-",
                                    "portable": "-",
                                    "error": detailed_error
                                })
                            elif hasattr(second_element, 'to_dict'):
                                # 如果第二个元素有to_dict方法，说明是结果对象
                                success_count += 1
                                result_dict = second_element.to_dict()
                                results.append({
                                    "phone": phone,
                                    "status": "success",
                                    "carrier": result_dict.get("carrier", "-"),
                                    "line_type": result_dict.get("line_type", "-"),
                                    "portable": result_dict.get("portable", "-"),
                                    "error": ""
                                })
                            elif isinstance(second_element, dict):
                                # 如果第二个元素是字典，直接使用
                                success_count += 1
                                results.append({
                                    "phone": phone,
                                    "status": "success",
                                    "carrier": second_element.get("carrier", "-"),
                                    "line_type": second_element.get("line_type", "-"),
                                    "portable": second_element.get("portable", "-"),
                                    "error": ""
                                })
                            else:
                                # 其他情况，记录为错误
                                error_count += 1
                                results.append({
                                    "phone": phone,
                                    "status": "error",
                                    "carrier": "-",
                                    "line_type": "-",
                                    "portable": "-",
                                    "error": f"{t('error_tuple_unknown')}: {str(second_element)}"
                                })
                        else:
                            # 元组格式不符合预期
                            error_count += 1
                            results.append({
                                "phone": phone,
                                "status": "error",
                                "carrier": "-",
                                "line_type": "-",
                                "portable": "-",
                                "error": t('error_tuple_format')
                            })
                    else:
                        # 成功查询
                        success_count += 1
                        result_dict = result.to_dict()
                        results.append({
                            "phone": phone,
                            "status": "success",
                            "carrier": result_dict.get("carrier", "-"),
                            "line_type": result_dict.get("line_type", "-"),
                            "portable": result_dict.get("portable", "-"),
                            "error": ""
                        })
                        
                except Exception as e:
                    # 记录错误但不显示
                    error_count += 1
                    error_msg = str(e)
                    detailed_error = get_error_description(error_msg, provider_id)
                    results.append({
                        "phone": phone,
                        "status": "error",
                        "carrier": "-",
                        "line_type": "-",
                        "portable": "-",
                        "error": detailed_error
                    })
    finally:
        # 恢复标准错误输出
        sys.stderr = original_stderr
        
        # 恢复日志级别
        logging.getLogger().setLevel(original_log_level)
    
    # 显示查询结果摘要
    console.print("\n")
    console.print(f"[bold green]{t('query_summary')}:[/bold green]")
    console.print(f"[green]- {t('total_numbers')}: {total}[/green]")
    console.print(f"[green]- {t('successful_queries')}: {success_count}[/green]")
    console.print(f"[yellow]- {t('failed_queries')}: {error_count}[/yellow]")
    
    # 使用表格显示结果
    from rich.table import Table
    
    table = Table(title=t('query_results'))
    table.add_column(t('phone_number'), style="cyan")
    table.add_column(t('carrier'), style="green")
    table.add_column(t('line_type'), style="blue")
    table.add_column(t('portable'), style="magenta")
    table.add_column(t('status'), style="yellow")
    
    # 只显示前10个结果
    display_count = min(10, len(results))
    for i in range(display_count):
        result = results[i]
        status_str = "[green]✓[/green]" if result["status"] == "success" else "[red]✗[/red]"
        table.add_row(
            result["phone"],
            result["carrier"],
            result["line_type"],
            result["portable"],
            status_str
        )
    
    console.print(table)
    
    if len(results) > 10:
        console.print(f"[dim]{t('more_results_in_file').format(count=len(results)-10)}[/dim]")
    
    # 保存结果到CSV文件
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['phone_number', 'carrier', 'line_type', 'portable', 'status', 'error']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'phone_number': result["phone"],
                    'carrier': result["carrier"],
                    'line_type': result["line_type"],
                    'portable': result["portable"],
                    'status': result["status"],
                    'error': result["error"]
                })
        console.print(f"\n[green]{t('query_complete')}: {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]{t('error_saving_results')}: {str(e)}[/red]")
        return
    
    # 询问是否查看详细错误信息
    if error_count > 0 and Confirm.ask(t('view_detailed_errors')):
        error_table = Table(title=t('detailed_errors'))
        error_table.add_column(t('phone_number'), style="cyan")
        error_table.add_column(t('error_message'), style="red", no_wrap=False)
        
        for result in results:
            if result["status"] == "error" and result["error"]:
                error_table.add_row(result["phone"], result["error"])
        
        console.print(error_table)
    
    # 等待用户确认
    input(f"\n{t('press_enter_return')}")

def get_error_description(error_msg, provider_id):
    """根据错误信息提供详细的错误描述"""
    # Telnyx错误
    if "403" in error_msg and "Telnyx" in error_msg:
        return t('error_telnyx_403')
    elif "401" in error_msg and "Telnyx" in error_msg:
        return t('error_telnyx_401')
    elif "429" in error_msg and "Telnyx" in error_msg:
        return t('error_telnyx_429')
    elif "500" in error_msg and "Telnyx" in error_msg:
        return t('error_telnyx_500')
    
    # Twilio错误
    elif "10002" in error_msg and "Twilio" in error_msg:
        return t('error_twilio_10002')
    elif "20003" in error_msg and "Twilio" in error_msg:
        return t('error_twilio_20003')
    elif "20404" in error_msg and "Twilio" in error_msg:
        return t('error_twilio_20404')
    
    # 通用错误
    elif "API返回格式错误" in error_msg:
        if provider_id == "telnyx":
            return t('error_telnyx_format')
        else:
            return t('error_twilio_format')
    elif "timeout" in error_msg.lower() or "超时" in error_msg:
        return t('error_timeout')
    elif "connection" in error_msg.lower() or "连接" in error_msg:
        return t('error_connection')
    
    # 默认错误
    return error_msg

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
                batch_query()
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