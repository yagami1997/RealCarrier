#!/usr/bin/env python3
"""
RealCarrier - Telnyx LNP美国电话号码查询工具
Alpha 0.1.0
"""

import os
import sys
import platform
import psutil
import time
import json
import re
import csv
import uuid
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Union

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from rich.text import Text
from rich.layout import Layout
import logging

# 初始化日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from lnptool.config import get_api_key, set_api_key, is_configured, get_config
from lnptool.telnyx_api import TelnyxAPI
from lnptool.lookup import LookupService, display_lookup_result, display_batch_summary
from lnptool.utils import is_valid_api_key, print_error, print_success, print_warning, print_info, phone_input

# 从i18n模块导入国际化函数
from lnptool.i18n import t, set_translations, set_language, save_language_preference, load_language_preference, get_current_language

# 语言翻译字典
TRANSLATIONS = {
    "zh_CN": {
        # 主菜单
        "app_title": "美国电话号码查询工具",
        "menu_option_1": "🔑 API密钥配置",
        "menu_option_2": "📱 查询单个电话号码",
        "menu_option_3": "📊 批量查询CSV文件",
        "menu_option_4": "💾 缓存管理",
        "menu_option_5": "ℹ️  系统信息",
        "menu_option_6": "🌐 语言设置",
        "menu_option_7": "🚀 Telnyx指南",
        "menu_option_0": "❌ 退出程序",
        "select_option": "请选择操作",
        
        # 电话号码查询界面
        "single_lookup_title": "查询单个电话号码",
        "enter_phone": "请输入电话号码",
        "plus_1_added": "+1已添加",
        "querying": "正在查询...",
        "query_result": "查询结果",
        "query_failed": "查询失败",
        
        # API配置
        "api_config_title": "API密钥配置",
        "current_api_status": "当前API状态",
        "configured": "已配置",
        "not_configured": "未配置",
        "none": "无",
        "current_api_key": "当前API密钥",
        "api_status": "API状态",
        "api_key": "API密钥",
        "api_service_info": "Telnyx API服务信息",
        "telnyx_info": "Telnyx官网",
        "register_account": "注册账号",
        "config_api_key": "配置API密钥",
        "modify_api_key": "修改API密钥",
        "delete_api_key": "删除API密钥",
        "telnyx_guide": "Telnyx指南",
        "return_main": "返回主菜单",
        "tool_uses": "工具用途",
        
        # 通用
        "github_link": "Github链接",
        "press_enter": "按Enter键",
        "to_return": "返回",
        "to_continue": "继续",
        "yes": "是",
        "no": "否",
        
        # 语言设置
        "language_settings": "语言设置",
        "current_language": "当前语言",
        "language_zh": "中文",
        "language_en": "英文",
        "language_return": "返回主菜单",
        "select_language": "选择语言",
        "language_changed": "语言已切换为",
        "unable_save": "无法保存语言设置，但已临时切换为",
        "already_using": "当前已是",
        
        # 查询结果
        "field": "字段",
        "value": "值",
        "query_status": "查询状态",
        "failed": "失败",
        "error_reason": "错误原因",
        "phone_number": "电话号码",
        "country": "国家",
        "carrier": "运营商",
        "number_type": "号码类型",
        "portable": "可携号转网",
        "ported": "已携号转网",
        "service_provider_id": "服务商ID",
        "carrier_code": "运营商代码",
        "previous_carrier": "前运营商",
        "previous_number_type": "前号码类型",
        "unknown": "未知",
        "error_403": "403错误，请检查Telnyx API账户状态，是否完成KYC认证或者余额足够",
        
        # 批量查询
        "batch_lookup_title": "批量查询CSV文件",
        "select_csv": "选择CSV文件",
        "file_not_exist": "文件不存在",
        "csv_files": "CSV文件",
        "reading_csv": "正在读取CSV文件",
        "found_numbers": "找到电话号码",
        "sample_numbers": "样例号码",
        "confirm_lookup": "确认查询",
        "executing_batch": "正在执行批量查询",
        "batch_wait": "请耐心等待，查询进度将实时显示",
        "batch_summary": "查询摘要",
        "results_saved": "结果已保存至",
        "error_in_report": "详细错误信息请查看报告文件",
        "batch_failed": "批量查询失败",
        "csv_format": "CSV文件格式示例",
        "csv_hint": "CSV文件应包含电话号码列，可以有其他备注列",
        "step1": "步骤1",
        "select_csv_file": "选择CSV文件",
        "enter_csv_path": "请输入CSV文件路径",
        "drag_drop_hint": "可直接将文件拖放到此处",
        "file_selected": "已选择文件",
        "not_csv_warning": "选择的文件不是CSV格式，可能导致处理错误",
        "continue_prompt": "是否继续?",
        "step2": "步骤2",
        "set_output_file": "设置输出文件",
        "recommended_output": "推荐输出文件",
        "enter_output_path": "请输入输出文件路径",
        "step3": "步骤3",
        "confirm_query_settings": "确认查询设置",
        "input_file": "输入文件",
        "output_file": "输出文件",
        "detected_phone_col": "检测到电话号码列",
        "column_number": "第{number}列",
        "no_phone_col": "未检测到明确的电话号码列，将使用第一列",
        "estimated_queries": "估计将进行{count}次查询",
        "large_batch_warning": "批量较大，可能需要较长时间",
        "file_preview_error": "文件预览错误",
        "will_process_anyway": "将继续处理文件",
        "confirm_batch": "确认开始批量查询?",
        "read_numbers_from_csv": "从CSV文件读取电话号码",
        "numbers": "个号码",
        "results_saved_to": "结果已保存至",
        "batch_result_summary": "批量查询结果摘要",
        "summary_item": "摘要项",
        "count": "数量",
        "percentage": "百分比",
        "total_numbers": "总号码数",
        "successful_queries": "成功查询",
        "failed_queries": "失败查询",
        "error_type_stats": "错误类型统计",
        "error_type": "错误类型",
        "error_403_short": "403权限错误",
        "remark": "备注",
        "customer_a": "客户A",
        "customer_b": "客户B",
        "customer_c": "客户C",
        "no_api_key": "未配置API密钥，请先配置",
        "operation_cancelled": "操作已取消",
        "processing": "处理中",
        "carrier_distribution": "运营商分布",
        "ported_numbers": "携转号码数",
        "error_401_short": "401认证失败",
        "error_404_short": "404未找到",
        "error_429_short": "429请求过多",
        "error_5xx_short": "服务器错误",
        "error_timeout_short": "请求超时",
        "error_unknown_short": "未知错误",
        "error_occurred": "发生错误",
        
        # 缓存管理
        "cache_mgmt_title": "缓存管理",
        "cache_description": "缓存功能说明",
        "cache_policy": "缓存策略：成功的查询结果会缓存30天",
        "cache_stats": "缓存统计",
        "total_entries": "总缓存条目",
        "valid_entries": "有效条目",
        "expired_entries": "过期条目",
        "clear_all_cache": "清除所有缓存",
        "clear_expired": "清除过期缓存",
        "cache_cleared": "缓存已清除",
        "no_expired": "没有过期缓存需要清理",
        "entries_removed": "条目已移除",
        "show_stats": "显示缓存统计",
        "clear_all": "清除所有缓存",
        "clear_expired": "清除过期缓存",
        "show_recent": "显示最近缓存",
        "return_main": "返回主菜单",
        "option": "选项",
        "description": "描述",
        "item": "项目",
        "value": "值",
        "cache_size": "缓存大小",
        "cache_ttl": "缓存有效期",
        "hours": "小时",
        "confirm_clear_all": "确认清除所有缓存?",
        "all_cleared": "所有缓存已清除",
        "clear_failed": "清除失败",
        "possible_solution": "可能的解决方案",
        "check_disk_permission": "检查磁盘权限",
        "file_locked": "文件被锁定",
        "persistent_problem": "如果问题持续，请尝试重新启动应用",
        "cleared_expired": "已清除{count}个过期条目",
        "clear_expired_failed": "清除过期缓存失败",
        "show_recent_count": "显示最近几条记录",
        "no_recent_lookups": "没有最近的查询记录",
        "recent_lookups": "最近的查询记录",
        "phone": "电话号码",
        "time": "时间",
        "get_stats_failed": "获取统计信息失败",
        "get_recent_failed": "获取最近记录失败",
        "no_recent": "没有最近的查询记录",
        "query_time": "查询时间",
        "program_error": "程序发生错误",
        "press_any_key": "按任意键退出",
        
        # 系统信息
        "system_info_title": "ℹ️  系统信息",
        "os_info": "操作系统",
        "kernel_version": "内核版本",
        "cpu_model": "CPU型号",
        "system_memory": "系统内存",
        "api_status": "API状态",
        "api_cache_ttl": "API缓存有效期",
        "api_rate_limit": "API请求限制",
        "cache_entry_count": "缓存条目数量",
        "cache_size": "缓存大小",
        "requests_per_sec": "请求/秒",
        
        # 退出
        "goodbye": "感谢使用，再见！",
        
        # 电话号码输入
        "incorrect_number_format": "号码格式不正确，请在+1后输入10位美国电话号码",
        "phone_you_entered": "您输入的电话号码是",
        "confirm_continue": "是否继续?",
        "input_cancelled": "已取消输入，请重新输入",
        "operation_cancelled": "操作已取消",
        
        # Telnyx指南
        "quick_start_guide": "快速入门指南",
        "is_telnyx_provider": "是一家通信API提供商，用于查询电话号码状态",
        "register_telnyx_account": "注册Telnyx账号",
        "add_payment_method": "添加支付方式（信用卡等）",
        "get_api_key": "获取API密钥",
        "verify_account_kyc": "完成账户验证（KYC）",
        "enable_lnp_service": "开通LNP查询服务",
    },
    "en_US": {
        # Main Menu
        "app_title": "US Phone Number Lookup Tool",
        "menu_option_1": "🔑 API Key Configuration",
        "menu_option_2": "📱 Single Number Lookup",
        "menu_option_3": "📊 Batch CSV Lookup",
        "menu_option_4": "💾 Cache Management",
        "menu_option_5": "ℹ️  System Information",
        "menu_option_6": "🌐 Language Settings",
        "menu_option_7": "🚀 Telnyx Guide",
        "menu_option_0": "❌ Exit Program",
        "select_option": "Select an option",
        
        # Phone Lookup Interface
        "single_lookup_title": "Single Phone Number Lookup",
        "enter_phone": "Enter phone number",
        "plus_1_added": "+1 has been added",
        "querying": "Querying...",
        "query_result": "Query Result",
        "query_failed": "Query failed",
        
        # API Configuration
        "api_config_title": "API Key Configuration",
        "current_api_status": "Current API Status",
        "configured": "Configured",
        "not_configured": "Not Configured",
        "none": "None",
        "current_api_key": "Current API Key",
        "api_status": "API Status",
        "api_key": "API Key",
        "api_service_info": "Telnyx API Service Information",
        "telnyx_info": "Telnyx Website",
        "register_account": "Register Account",
        "config_api_key": "Configure API Key",
        "modify_api_key": "Modify API Key",
        "delete_api_key": "Delete API Key",
        "telnyx_guide": "Telnyx Guide",
        "return_main": "Return to Main Menu",
        "tool_uses": "Tool Uses",
        
        # General
        "github_link": "Github Link",
        "press_enter": "Press Enter",
        "to_return": "to return",
        "to_continue": "to continue",
        "yes": "Yes",
        "no": "No",
        
        # Language Settings
        "language_settings": "Language Settings",
        "current_language": "Current Language",
        "language_zh": "Chinese",
        "language_en": "English",
        "language_return": "Return to Main Menu",
        "select_language": "Select Language",
        "language_changed": "Language changed to",
        "unable_save": "Unable to save language setting, but temporarily switched to",
        "already_using": "Current language is already",
        
        # Query Results
        "field": "Field",
        "value": "Value",
        "query_status": "Query Status",
        "failed": "Failed",
        "error_reason": "Error Reason",
        "phone_number": "Phone Number",
        "country": "Country",
        "carrier": "Carrier",
        "number_type": "Number Type",
        "portable": "Portable",
        "ported": "Ported",
        "service_provider_id": "Service Provider ID",
        "carrier_code": "Carrier Code",
        "previous_carrier": "Previous Carrier",
        "previous_number_type": "Previous Number Type",
        "unknown": "Unknown",
        "error_403": "403 Error, please check Telnyx API account status, KYC verification or sufficient balance",
        
        # Batch Lookup
        "batch_lookup_title": "Batch CSV Lookup",
        "select_csv": "Select CSV file",
        "file_not_exist": "File does not exist",
        "csv_files": "CSV files",
        "reading_csv": "Reading CSV file",
        "found_numbers": "Found phone numbers",
        "sample_numbers": "Sample numbers",
        "confirm_lookup": "Confirm lookup",
        "executing_batch": "Executing batch lookup",
        "batch_wait": "Please wait patiently, progress will be displayed in real-time",
        "batch_summary": "Batch Summary",
        "results_saved": "Results saved to",
        "error_in_report": "See the report file for detailed error information",
        "batch_failed": "Batch lookup failed",
        "csv_format": "CSV File Format Example",
        "csv_hint": "CSV file should contain a phone number column, can have other remark columns",
        "step1": "Step 1",
        "select_csv_file": "Select CSV File",
        "enter_csv_path": "Enter CSV file path",
        "drag_drop_hint": "You can drag and drop file here",
        "file_selected": "File selected",
        "not_csv_warning": "Selected file is not CSV format, may cause processing errors",
        "continue_prompt": "Continue?",
        "step2": "Step 2",
        "set_output_file": "Set Output File",
        "recommended_output": "Recommended output file",
        "enter_output_path": "Enter output file path",
        "step3": "Step 3",
        "confirm_query_settings": "Confirm Query Settings",
        "input_file": "Input file",
        "output_file": "Output file",
        "detected_phone_col": "Detected phone number column",
        "column_number": "Column {number}",
        "no_phone_col": "No explicit phone number column detected, will use the first column",
        "estimated_queries": "Estimated {count} queries to perform",
        "large_batch_warning": "Large batch, may take longer time",
        "file_preview_error": "File preview error",
        "will_process_anyway": "Will continue processing the file",
        "confirm_batch": "Confirm batch lookup?",
        "read_numbers_from_csv": "Reading numbers from CSV",
        "numbers": "numbers",
        "results_saved_to": "Results saved to",
        "batch_result_summary": "Batch Result Summary",
        "summary_item": "Summary Item",
        "count": "Count",
        "percentage": "Percentage",
        "total_numbers": "Total Numbers",
        "successful_queries": "Successful Queries",
        "failed_queries": "Failed Queries",
        "error_type_stats": "Error Type Statistics",
        "error_type": "Error Type",
        "error_403_short": "403 Permission Error",
        "remark": "Remark",
        "customer_a": "Customer A",
        "customer_b": "Customer B",
        "customer_c": "Customer C",
        "no_api_key": "API key not configured, please configure first",
        "operation_cancelled": "Operation cancelled",
        "processing": "Processing",
        "carrier_distribution": "Carrier Distribution",
        "ported_numbers": "Ported Numbers",
        "error_401_short": "401 Authentication Failed",
        "error_404_short": "404 Not Found",
        "error_429_short": "429 Too Many Requests",
        "error_5xx_short": "Server Error",
        "error_timeout_short": "Request Timeout",
        "error_unknown_short": "Unknown Error",
        "error_occurred": "Error occurred",
        
        # Cache Management
        "cache_mgmt_title": "Cache Management",
        "cache_description": "Cache Functionality",
        "cache_policy": "Cache Policy: Successful query results are cached for 30 days",
        "cache_stats": "Cache Statistics",
        "total_entries": "Total Cache Entries",
        "valid_entries": "Valid Entries",
        "expired_entries": "Expired Entries",
        "clear_all_cache": "Clear All Cache",
        "clear_expired": "Clear Expired Cache",
        "cache_cleared": "Cache Cleared",
        "no_expired": "No expired cache to clear",
        "entries_removed": "entries removed",
        "show_stats": "Show Cache Statistics",
        "clear_all": "Clear All Cache",
        "clear_expired": "Clear Expired Cache",
        "show_recent": "Show Recent Cache",
        "return_main": "Return to Main Menu",
        "option": "Option",
        "description": "Description",
        "item": "Item",
        "value": "Value",
        "cache_size": "Cache Size",
        "cache_ttl": "Cache TTL",
        "hours": "hours",
        "confirm_clear_all": "Confirm clear all cache?",
        "all_cleared": "All cache cleared",
        "clear_failed": "Clear failed",
        "possible_solution": "Possible solutions",
        "check_disk_permission": "Check disk permissions",
        "file_locked": "File may be locked",
        "persistent_problem": "If problem persists, try restarting the application",
        "cleared_expired": "Cleared {count} expired entries",
        "clear_expired_failed": "Failed to clear expired cache",
        "show_recent_count": "Show how many recent records",
        "no_recent_lookups": "No recent lookups found",
        "recent_lookups": "Recent Lookups",
        "phone": "Phone",
        "time": "Time",
        "get_stats_failed": "Failed to get statistics",
        "get_recent_failed": "Failed to get recent records",
        "no_recent": "No recent lookups",
        "query_time": "Query Time",
        "program_error": "Program error",
        "press_any_key": "Press any key to exit",
        
        # System Info
        "system_info_title": "ℹ️  System Information",
        "os_info": "Operating System",
        "kernel_version": "Kernel Version",
        "cpu_model": "CPU Model",
        "system_memory": "System Memory",
        "api_cache_ttl": "API Cache TTL",
        "api_rate_limit": "API Rate Limit",
        "cache_entry_count": "Cache Entry Count",
        "cache_size": "Cache Size",
        "requests_per_sec": "requests/sec",
        
        # Exit
        "goodbye": "Thank you for using, goodbye!",
        
        # Phone Number Input
        "incorrect_number_format": "Incorrect format, please enter 10-digit US phone number after +1",
        "phone_you_entered": "Phone number you entered",
        "confirm_continue": "Continue?",
        "input_cancelled": "Input cancelled, please enter again",
        "operation_cancelled": "Operation cancelled",
        
        # Telnyx Guide
        "quick_start_guide": "Quick Start Guide",
        "is_telnyx_provider": "is a communications API provider used for phone number status lookup",
        "register_telnyx_account": "Register Telnyx Account", 
        "add_payment_method": "Add Payment Method (Credit Card, etc.)",
        "get_api_key": "Get API Key",
        "verify_account_kyc": "Complete Account Verification (KYC)",
        "enable_lnp_service": "Enable LNP Lookup Service",
    }
}

# 初始化Rich控制台
console = Console()

def clear_screen():
    """清除屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_logo():
    """显示程序标志"""
    # 创建主标题面板
    title_text = "RealCarrier - "
    if get_current_language() == "zh_CN":
        title_text += "美国电话号码状态查询器"
    else:
        title_text += "US Phone Number Status Lookup Tool"
        
    console.print(Panel.fit(
        f"[bold blue]RealCarrier[/bold blue] - [cyan]{title_text}[/cyan]",
        border_style="green",
        padding=(1, 2),
        title="v0.1.0",
        subtitle="by Yagami1997"
    ))
    console.print()

def show_main_menu():
    """显示主菜单"""
    console.print(f"\n[bold cyan]RealCarrier Alpha[/bold cyan] - {t('app_title')}\n")
    
    # 创建带有表情符号的菜单表格
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column(t("option"), style="cyan")
    table.add_column(t("description"), style="white")
    
    table.add_row("[1]", t("menu_option_1"))
    table.add_row("[2]", t("menu_option_2"))
    table.add_row("[3]", t("menu_option_3"))
    table.add_row("[4]", t("menu_option_4"))
    table.add_row("[5]", t("menu_option_5"))
    table.add_row("[6]", t("menu_option_6"))
    table.add_row("[0]", t("menu_option_0"))
    
    console.print(table)
    console.print(f"{t('select_option')} [0-6]: ", end="")

def check_api_key_status():
    """检查API密钥状态"""
    api_key = get_api_key()
    if api_key:
        status = f"[bold green]{t('configured')}[/bold green]"
        # 显示密钥前4位和后4位，中间用星号
        masked_key = f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}" if len(api_key) > 8 else "******"
        return status, masked_key
    else:
        return f"[bold red]{t('not_configured')}[/bold red]", t("none")

def configure_api_key():
    """配置API密钥"""
    while True:
        clear_screen()
        show_logo()
        console.print(f"[bold]{t('api_config_title')}[/bold]\n")
        
        # 显示当前状态
        status, masked_key = check_api_key_status()
        console.print(f"{t('current_api_status')}: {status}")
        if t("configured") in status:
            console.print(f"{t('current_api_key')}: {masked_key}")
        
        # 显示Telnyx信息
        console.print(f"\n[cyan]{t('api_service_info')}[/cyan]")
        console.print()
        
        # 显示API密钥配置菜单
        table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
        table.add_column(t("option"), style="cyan", justify="center")
        table.add_column(t("description"), style="white")
        
        if t("configured") in status:
            table.add_row("[1]", t("modify_api_key"))
            table.add_row("[2]", t("delete_api_key"))
            table.add_row("[3]", t("telnyx_guide"))
            table.add_row("[0]", t("return_main"))
        else:
            table.add_row("[1]", t("config_api_key"))
            table.add_row("[2]", t("telnyx_guide"))
            table.add_row("[0]", t("return_main"))
        
        console.print(table)
        console.print()
        
        # 根据API状态提供不同的选项
        if t("configured") in status:
            choice = Prompt.ask(
                t("select_option"), 
                choices=["0", "1", "2", "3"], 
                default="0"
            )
        else:
            choice = Prompt.ask(
                t("select_option"), 
                choices=["0", "1", "2"], 
                default="0"
            )
        
        if choice == "0":
            return
        
        # 添加或修改API密钥
        if choice == "1":
            set_new_api_key()
        
        # 删除API密钥
        elif choice == "2" and t("configured") in status:
            delete_api_key()
        
        # Telnyx账号向导
        elif (choice == "3" and t("configured") in status) or (choice == "2" and t("not_configured") in status):
            telnyx_account_guide()

def set_new_api_key():
    """添加或修改API密钥"""
    console.print(f"\n[bold]{t('add_modify_key')}[/bold]")
    
    # 输入新的API密钥
    console.print(f"\n{t('enter_api_key')}")
    api_key = Prompt.ask("> ", password=False)  # 明文显示以便确认
    
    # 确认输入
    console.print(f"\n{t('key_input')}: [bold]{api_key}[/bold]")
    
    # 验证格式
    if not is_valid_api_key(api_key):
        print_warning(t("key_format_warning"))
        if not Confirm.ask(t("still_save")):
            print_info(t("operation_cancelled"))
            return
    
    # 保存前再次确认
    if Confirm.ask(t("confirm_save")):
        if set_api_key(api_key):
            print_success(t("key_saved"))
            
            # 尝试验证API密钥
            console.print(f"\n[bold]{t('verifying_key')}[/bold]")
            try:
                api = TelnyxAPI(api_key=api_key)
                # 使用正确的LNP查询端点测试API密钥
                response = api._make_request("GET", "/number_lookup/+14155552671", params={"type": "carrier"})
                print_success(t("key_verified"))
            except Exception as e:
                print_warning(f"{t('key_verify_failed')}: {str(e)}")
                
                # 提供更详细的错误信息和解决方案
                error_str = str(e).lower()
                if "401" in error_str:
                    console.print("\n[yellow]API认证错误(401):[/yellow]")
                    console.print("1. 您输入的API密钥无效或已过期")
                    console.print("2. 请检查密钥是否正确复制，没有多余的空格")
                elif "403" in error_str:
                    console.print("\n[yellow]API权限错误(403):[/yellow]")
                    console.print("1. 您的Telnyx账户可能未完成验证或未充值")
                    console.print("2. 请登录Telnyx账户确认账户状态并完成必要的验证步骤")
                elif "404" in error_str:
                    console.print("\n[yellow]API端点错误(404):[/yellow]")
                    console.print("1. Telnyx API接口可能已更改")
                    console.print("2. 请更新程序或联系技术支持")
                else:
                    console.print("\n[yellow]验证过程中出现其他错误:[/yellow]")
                    console.print("1. 密钥已保存，但可能无法正常工作")
                    console.print("2. 请检查网络连接")
                    console.print("3. 请联系Telnyx客服确认账户状态")
        else:
            print_error(t("delete_failed"))
    else:
        print_info(t("operation_cancelled"))
    
    input(f"\n{t('press_enter')} {t('to_continue')}...")

def delete_api_key():
    """删除API密钥"""
    console.print(f"\n[bold red]{t('delete_key_title')}[/bold red]")
    console.print(f"\n[yellow]{t('delete_warning')}[/yellow]")
    
    # 第一次确认
    if not Confirm.ask(f"\n{t('confirm_delete')}"):
        print_info(t("operation_cancelled"))
        input(f"\n{t('press_enter')} {t('to_continue')}...")
        return
    
    # 二次确认
    console.print(f"\n[bold red]{t('final_confirm')}[/bold red]")
    if Confirm.ask(t("confirm_delete_again")):
        try:
            # 假设有一个删除API密钥的函数，如果没有，需要实现它
            from lnptool.config import delete_api_key as delete_key
            if delete_key():
                print_success(t("key_deleted"))
            else:
                print_error(t("delete_failed"))
        except Exception as e:
            print_error(f"{t('delete_failed')}: {str(e)}")
    else:
        print_info(t("operation_cancelled"))
    
    input(f"\n{t('press_enter')} {t('to_continue')}...")

def telnyx_account_guide():
    """显示Telnyx账户指南"""
    clear_screen()
    show_logo()
    
    # 使用翻译函数来显示标题
    console.print(f"[bold]{t('telnyx_guide')}[/bold]\n")
    
    # 显示指南信息
    console.print(Panel(
        f"[cyan]Telnyx[/cyan] {t('is_telnyx_provider')}\n\n"
        f"1. {t('register_telnyx_account')}: [link=https://telnyx.com/sign-up]telnyx.com/sign-up[/link]\n\n"
        f"2. {t('add_payment_method')}\n\n"
        f"3. {t('get_api_key')}: [link=https://portal.telnyx.com/#/app/api-keys]portal.telnyx.com/#/app/api-keys[/link]\n\n"
        f"4. {t('verify_account_kyc')}\n\n"
        f"5. {t('enable_lnp_service')}: [link=https://portal.telnyx.com/#/app/number-lookup]portal.telnyx.com/#/app/number-lookup[/link]",
        title=t('quick_start_guide'),
        border_style="green"
    ))
    
    # 按任意键返回
    input(f"\n{t('press_enter')} {t('to_return')}...")

def lookup_number():
    """查询单个电话号码"""
    clear_screen()
    console.print(f"\n{t('single_lookup_title')}\n")
    
    # 简化提示，删除颜色标记，并确保+1后有空格
    phone_number = phone_input(f"{t('enter_phone')}", use_rich=True)
    
    # 如果用户取消输入，返回到主菜单
    if not phone_number:
        return
    
    # 检查API密钥
    if not is_configured():
        print_error(t("no_api_key"))
        input(f"\n{t('press_enter')} {t('to_return')}...")
        return
    
    # 执行查询
    try:
        console.print(f"\n[bold]{t('querying')}[/bold]")
        service = LookupService()
        result = service.lookup_number(phone_number)
        
        # 显示结果
        console.print(f"\n[bold]{t('query_result')}[/bold]")
        display_lookup_result(result)
    except Exception as e:
        print_error(f"{t('query_failed')}: {str(e)}")
        
        # 提供更详细的错误信息和解决方案
        error_str = str(e).lower()
        if "400" in error_str:
            console.print(f"\n[yellow]{t('error_400_title')}[/yellow]")
            console.print(f"1. {t('error_400_reason1')}")
            console.print(f"2. {t('error_400_reason2')}")
        elif "401" in error_str:
            console.print(f"\n[yellow]{t('error_401_title')}[/yellow]")
            console.print(f"1. {t('error_401_reason1')}")
            console.print(f"2. {t('error_401_reason2')}")
        elif "403" in error_str:
            console.print(f"\n[yellow]{t('error_403_title')}[/yellow]")
            console.print(f"1. {t('error_403_reason1')}")
            console.print(f"2. {t('error_403_reason2')}")
            console.print(f"3. {t('error_403_reason3')}")
        elif "404" in error_str:
            console.print(f"\n[yellow]{t('error_404_title')}[/yellow]")
            console.print(f"1. {t('error_404_reason1')}")
            console.print(f"2. {t('error_404_reason2')}")
        elif "408" in error_str:
            console.print(f"\n[yellow]{t('error_408_title')}[/yellow]")
            console.print(f"1. {t('error_408_reason1')}")
            console.print(f"2. {t('error_408_reason2')}")
        elif "422" in error_str:
            console.print(f"\n[yellow]{t('error_422_title')}[/yellow]")
            console.print(f"1. {t('error_422_reason1')}")
            console.print(f"2. {t('error_422_reason2')}")
        elif "429" in error_str:
            console.print(f"\n[yellow]{t('error_429_title')}[/yellow]")
            console.print(f"1. {t('error_429_reason1')}")
            console.print(f"2. {t('error_429_reason2')}")
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            console.print(f"\n[yellow]{t('error_5xx_title')}[/yellow]")
            console.print(f"1. {t('error_5xx_reason1')}")
            console.print(f"2. {t('error_5xx_reason2')}")
        else:
            console.print(f"\n[yellow]{t('error_unknown_title')}[/yellow]")
            console.print(f"1. {t('error_unknown_reason1')}")
            console.print(f"2. {t('error_unknown_reason2')}")
            console.print(f"3. {t('error_unknown_reason3')}")
    
    input(f"\n{t('press_enter')} {t('to_return')}...")

def batch_lookup():
    """批量查询CSV文件"""
    clear_screen()
    show_logo()
    console.print(f"[bold]{t('batch_lookup_title')}[/bold]\n")
    
    # 检查API密钥
    if not is_configured():
        print_error(t("no_api_key"))
        input(f"\n{t('press_enter')} {t('to_return')}...")
        return
    
    # 展示简化的CSV格式示例
    console.print(f"[bold cyan]{t('csv_format')}[/bold cyan]")
    
    # 创建更简单的示例表格，使用更短的列名
    example_table = Table(box=box.SIMPLE)
    example_table.add_column("phone", style="green")
    example_table.add_column(t("remark"), style="blue")
    
    example_table.add_row("8772427372", t("customer_a"))
    example_table.add_row("2025550179", t("customer_b"))
    example_table.add_row("4155552671", t("customer_c"))
    
    console.print(example_table)
    console.print(f"\n[italic]{t('csv_hint')}[/italic]\n")
    
    # 引导用户选择文件
    console.print(f"[bold]{t('step1')}[/bold] {t('select_csv_file')}")
    console.print(f"{t('enter_csv_path')}")
    console.print(f"[dim]{t('drag_drop_hint')}[/dim]")
    csv_file = input()

    # 提示用户输入成功
    if csv_file:
        console.print(f"[green]{t('file_selected')}: {csv_file}[/green]")
    
    # 检查文件是否存在，并修复拖放文件时可能产生的额外空格
    file_path = Path(csv_file.strip().strip('"').strip("'"))  # 额外添加strip()移除所有空白字符
    if not file_path.exists():
        print_error(f"{t('file_not_exist')}: {file_path}")
        input(f"\n{t('press_enter')} {t('to_return')}...")
        return
    
    # 检查是否为CSV文件
    if file_path.suffix.lower() != '.csv':
        print_warning(f"{t('not_csv_warning')}")
        if not Confirm.ask(t("continue_prompt")):
            return
    
    # 设置输出文件
    console.print(f"\n[bold]{t('step2')}[/bold] {t('set_output_file')}")
    default_output = file_path.with_name(f"{file_path.stem}_results.csv")
    console.print(f"[green]{t('recommended_output')}: {default_output}[/green]")
    output_file = Prompt.ask(
        t("enter_output_path"), 
        default=str(default_output)
    )
    
    # 确认开始查询
    console.print(f"\n[bold]{t('step3')}[/bold] {t('confirm_query_settings')}")
    console.print(f"{t('input_file')}: [cyan]{file_path}[/cyan]")
    console.print(f"{t('output_file')}: [cyan]{output_file}[/cyan]")
    
    # 尝试预览并统计CSV文件行数
    try:
        import csv
        row_count = 0
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            # 读取表头
            headers = next(reader, None)
            
            # 如果找到表头，显示预览
            if headers:
                # 查找可能的电话号码列
                phone_cols = [i for i, col in enumerate(headers) 
                             if col and ('phone' in col.lower() or 'number' in col.lower() or 'tel' in col.lower())]
                
                if phone_cols:
                    col_idx = phone_cols[0]
                    col_name = headers[col_idx]
                    console.print(f"[green]{t('detected_phone_col')}: {col_name} ({t('column_number').format(number=col_idx+1)})[/green]")
                else:
                    console.print(f"[yellow]{t('no_phone_col')}[/yellow]")
                
                # 统计行数
                for _ in reader:
                    row_count += 1
                
                console.print(f"[cyan]{t('estimated_queries').format(count=row_count)}[/cyan]")
                
                # 如果行数很多，给出提示
                if row_count > 100:
                    console.print(f"[yellow]{t('large_batch_warning')}[/yellow]")
    except Exception as e:
        console.print(f"[yellow]{t('file_preview_error')}: {str(e)}[/yellow]")
        console.print(f"[yellow]{t('will_process_anyway')}[/yellow]")
    
    # 确认开始查询
    if not Confirm.ask(f"\n{t('confirm_batch')}"):
        print_info(t("operation_cancelled"))
        input(f"\n{t('press_enter')} {t('to_return')}...")
        return
    
    # 执行批量查询
    try:
        console.print(f"\n[bold]{t('executing_batch')}[/bold]")
        console.print(f"[italic]{t('batch_wait')}[/italic]")
        
        service = LookupService()
        # 不指定具体列名，让服务自动检测
        results = service.batch_lookup_from_csv(
            csv_file=str(file_path),
            output_file=output_file
        )
        
        # 显示摘要
        console.print(f"\n[bold]{t('batch_summary')}[/bold]")
        display_batch_summary(results)
        
        print_success(f"\n{t('results_saved')} {output_file}")
        # 添加更明确的引导语句，提示用户查看详细报告
        console.print(f"[yellow]{t('error_in_report')}[/yellow]")
    
    except Exception as e:
        print_error(f"{t('batch_failed')}: {str(e)}")
        logger.error(f"批量查询错误: {e}", exc_info=True)
    
    finally:
        input(f"\n{t('press_enter')} {t('to_return')}...")

def cache_management():
    """缓存管理"""
    from lnptool.cache import Cache
    
    while True:
        clear_screen()
        show_logo()
        console.print(f"[bold]{t('cache_mgmt_title')}[/bold]\n")
        
        # 显示缓存菜单
        table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
        table.add_column(t("option"), style="cyan", justify="center")
        table.add_column(t("description"), style="white")
        
        table.add_row("[1]", t("show_stats"))
        table.add_row("[2]", t("clear_all"))
        table.add_row("[3]", t("clear_expired"))
        table.add_row("[4]", t("show_recent"))
        table.add_row("[0]", t("return_main"))
        
        console.print(table)
        console.print()
        
        choice = Prompt.ask(
            t("select_option"), 
            choices=["0", "1", "2", "3", "4"], 
            default="0"
        )
        
        if choice == "0":
            break
        
        cache = Cache()
        
        if choice == "1":
            # 显示缓存统计信息
            try:
                stats = cache.get_stats()
                
                console.print(f"\n[bold]{t('cache_stats')}:[/bold]")
                
                # 展示统计信息
                table = Table(title=t("cache_stats"), show_header=False, box=box.ROUNDED, expand=True)
                table.add_column(t("item"), style="cyan")
                table.add_column(t("value"), style="white")
                
                # 添加缓存统计行
                table.add_row(t("total_entries"), str(stats.get("total_entries", 0)))
                table.add_row(t("valid_entries"), str(stats.get("valid_entries", 0)))
                table.add_row(t("expired_entries"), str(stats.get("expired_entries", 0)))
                
                size_kb = stats.get("cache_size_bytes", 0) / 1024
                table.add_row(t("cache_size"), f"{size_kb:.2f} KB")
                
                ttl_hours = stats.get("cache_ttl_seconds", 0) / 3600
                table.add_row(t("cache_ttl"), f"{ttl_hours:.1f} {t('hours')}")
                
                console.print(table)
            except Exception as e:
                print_error(f"{t('error_occurred')}: {str(e)}")
            
            input(f"\n{t('press_enter')} {t('to_return')}...")
        
        elif choice == "2":
            # 清除所有缓存
            if Confirm.ask(f"\n{t('confirm_clear_all')}"):
                try:
                    if cache.clear():
                        print_success(t("all_cleared"))
                    else:
                        print_error(t("clear_failed"))
                except Exception as e:
                    print_error(f"{t('clear_failed')}: {str(e)}")
                    console.print(f"\n[yellow]{t('possible_solution')}:[/yellow]")
                    console.print(f"1. {t('check_disk_permission')}")
                    console.print(f"2. {t('file_locked')}")
                    console.print(f"3. {t('persistent_problem')}")
        
        elif choice == "3":
            # 清除过期缓存
            try:
                count = cache.clear_expired()
                print_success(f"{t('cleared_expired').format(count=count)}")
            except Exception as e:
                print_error(f"{t('clear_expired_failed')}: {str(e)}")
        
        elif choice == "4":
            # 显示最近查询
            try:
                limit = int(Prompt.ask(
                    f"\n{t('show_recent_count')}",
                    default="10"
                ))
                recent = cache.get_recent_lookups(limit)
                
                if not recent:
                    print_info(t("no_recent"))
                else:
                    console.print(f"\n[bold]{t('recent_lookups')}:[/bold]")
                    
                    table = Table(box=box.ROUNDED)
                    table.add_column(t("phone_number"), style="cyan")
                    table.add_column(t("query_time"), style="green")
                    
                    for number, timestamp in recent:
                        from lnptool.utils import format_timestamp
                        table.add_row(number, format_timestamp(timestamp))
                    
                    console.print(table)
            except Exception as e:
                print_error(f"{t('get_recent_failed')}: {str(e)}")
        
        input(f"\n{t('press_enter')} {t('to_return')}...")

def system_info():
    """显示系统信息"""
    clear_screen()
    show_logo()
    console.print(f"[bold]{t('system_info_title')}[/bold]\n")
    
    # 获取配置信息
    config = get_config()
    api_status, masked_key = check_api_key_status()
    
    table = Table(box=box.ROUNDED)
    table.add_column(t("item"), style="cyan")
    table.add_column(t("value"), style="green")
    
    # 基本信息
    table.add_row(t("api_status"), api_status)
    if t("configured") in api_status:
        table.add_row(t("api_key"), masked_key)
    
    # 配置信息
    table.add_row(t("api_cache_ttl"), f"{config.get('api_cache_ttl', 86400) / 3600:.1f} {t('hours')}")
    table.add_row(t("api_rate_limit"), f"{config.get('rate_limit', 2)} {t('requests_per_sec')}")
    
    # 缓存信息
    try:
        from lnptool.cache import Cache
        cache = Cache()
        stats = cache.get_stats()
        table.add_row(t("cache_entry_count"), str(stats.get("total_entries", 0)))
        size_kb = stats.get("cache_size_bytes", 0) / 1024
        table.add_row(t("cache_size"), f"{size_kb:.2f} KB")
    except Exception:
        pass
    
    # 获取CPU信息
    cpu_info = t("unknown")
    try:
        import platform
        import os
        from subprocess import run, PIPE
        
        os_name = platform.system()
        
        if os_name == "Darwin":  # macOS
            # 使用system_profiler获取更准确的硬件信息
            result = run(['system_profiler', 'SPHardwareDataType'], stdout=PIPE, text=True)
            # 检查是否是Apple Silicon
            is_apple_silicon = False
            
            for line in result.stdout.strip().split('\n'):
                if 'Apple M' in line or 'Chip' in line:
                    is_apple_silicon = True
                    parts = line.split(':')
                    if len(parts) > 1:
                        chip_info = parts[1].strip()
                        # 确保显示完整名称
                        if 'M1' in chip_info or 'M2' in chip_info or 'M3' in chip_info:
                            if not chip_info.startswith('Apple'):
                                chip_info = 'Apple ' + chip_info
                            if not 'Silicon' in chip_info:
                                chip_info = 'Apple Silicon ' + chip_info.replace('Apple ', '')
                        cpu_info = chip_info
                        break
            
            # 如果不是Apple Silicon，尝试获取Intel处理器信息
            if not is_apple_silicon:
                result = run(['sysctl', '-n', 'machdep.cpu.brand_string'], stdout=PIPE, stderr=PIPE, text=True)
                if result.stdout and not result.stderr:
                    cpu_info = result.stdout.strip()
                    # 格式化Intel处理器名称，确保包含完整信息
                    if 'Intel' in cpu_info and not cpu_info.startswith('Intel'):
                        cpu_info = 'Intel ' + cpu_info.replace('Intel', '').strip()
        elif os_name == "Windows":
            # Windows系统
            result = run('wmic cpu get name', stdout=PIPE, shell=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                cpu_info = lines[1].strip()
                # 格式化处理器名称，确保包含完整厂商名称
                if 'intel' in cpu_info.lower() and not cpu_info.lower().startswith('intel'):
                    cpu_info = 'Intel ' + cpu_info.replace('Intel', '').replace('intel', '').strip()
                elif 'amd' in cpu_info.lower() and not cpu_info.lower().startswith('amd'):
                    cpu_info = 'AMD ' + cpu_info.replace('AMD', '').replace('amd', '').strip()
        elif os_name == "Linux":
            # Linux系统
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            cpu_info = line.split(':')[1].strip()
                            # 格式化处理器名称
                            if 'intel' in cpu_info.lower() and not cpu_info.lower().startswith('intel'):
                                cpu_info = 'Intel ' + cpu_info.replace('Intel', '').replace('intel', '').strip()
                            elif 'amd' in cpu_info.lower() and not cpu_info.lower().startswith('amd'):
                                cpu_info = 'AMD ' + cpu_info.replace('AMD', '').replace('amd', '').strip()
                            break
    except Exception as e:
        cpu_info = f"{t('cannot_get')} ({str(e)})"

    # 获取内存信息
    mem_info = t("unknown")
    try:
        if os_name == "Darwin":  # macOS
            # 使用system_profiler获取更精确的信息
            result = run(['system_profiler', 'SPHardwareDataType'], stdout=PIPE, text=True)
            for line in result.stdout.strip().split('\n'):
                if 'Memory' in line:
                    mem_info = line.split(':')[1].strip()
                    break
            
            # 如果上面方法失败，尝试sysctl
            if mem_info == t("unknown"):
                result = run(['sysctl', '-n', 'hw.memsize'], stdout=PIPE, text=True)
                if result.stdout:
                    mem_bytes = int(result.stdout.strip())
                    mem_info = f"{mem_bytes // (1024**3)} GB"
        elif os_name == "Windows":
            # Windows系统
            result = run('wmic computersystem get totalphysicalmemory', stdout=PIPE, shell=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                mem_bytes = int(lines[1].strip())
                mem_info = f"{mem_bytes // (1024**3)} GB"
        elif os_name == "Linux":
            # Linux系统
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal'):
                            mem_kb = int(line.split()[1])
                            mem_info = f"{mem_kb // 1024 // 1024} GB"
                            break
    except Exception as e:
        mem_info = f"{t('cannot_get')} ({str(e)})"
    
    # Python版本
    import platform
    table.add_row(t("python_version"), platform.python_version())
    
    # 获取更友好的操作系统名称
    os_name = platform.system()
    os_version = platform.release()
    os_display = ""

    if os_name == "Darwin":
        # macOS系统
        try:
            from subprocess import run, PIPE
            # 尝试获取macOS版本号
            result = run(['sw_vers', '-productVersion'], stdout=PIPE, text=True)
            macos_version = result.stdout.strip()
            os_display = f"macOS {macos_version}"
        except:
            os_display = f"macOS (Darwin内核)"
    elif os_name == "Linux":
        # Linux系统，尝试获取发行版信息
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('PRETTY_NAME='):
                        dist_name = line.split('=')[1].strip().strip('"\'')
                        os_display = dist_name
                        break
        except:
            os_display = f"Linux"
    elif os_name == "Windows":
        # Windows系统，获取更详细的版本信息
        try:
            from subprocess import run, PIPE
            # 使用wmic获取版本信息
            result = run('wmic os get Caption', stdout=PIPE, shell=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                win_version = lines[1].strip()
                os_display = win_version
            else:
                # 备用方案：使用platform模块
                win_version = platform.version()
                if '10' in os_version:
                    os_display = f"Windows 10 ({win_version})"
                elif '11' in win_version:
                    os_display = f"Windows 11 ({win_version})"
                else:
                    os_display = f"Windows {os_version} ({win_version})"
        except:
            os_display = f"Windows {os_version}"

    # 如果没有获取到友好名称，使用默认值
    if not os_display:
        os_display = f"{os_name} {os_version}"

    # 添加操作系统和内核信息
    table.add_row(t("os_info"), os_display)
    table.add_row(t("kernel_version"), f"{os_name} {os_version}")
    
    # 添加CPU和内存信息
    table.add_row(t("cpu_model"), cpu_info)
    table.add_row(t("system_memory"), mem_info)
    
    console.print(table)
    
    input(f"\n{t('press_enter')} {t('to_return')}...")

def language_settings():
    """语言设置"""
    clear_screen()
    show_logo()
    
    # 获取当前语言和翻译内容
    current_lang = get_current_language()
    current_language_display = t("language_zh") if current_lang == 'zh_CN' else t("language_en")
    
    console.print(f"[bold]{t('language_settings')}[/bold]\n")
    console.print(f"{t('current_language')}: [cyan]{current_language_display}[/cyan]\n")
    
    # 显示选项
    console.print(f"[bold]1.[/bold] {t('language_zh')} (Chinese)")
    console.print(f"[bold]2.[/bold] {t('language_en')} (English)")
    console.print(f"[bold]0.[/bold] {t('language_return')}")
    
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
    
    # 按任意键返回主菜单
    input(f"\n{t('press_enter')} {t('to_return')}...")

def main():
    """主函数入口"""
    try:
        # 初始化翻译库
        set_translations(TRANSLATIONS)
        
        # 加载语言偏好设置
        load_language_preference()
        
        # 程序主循环
        while True:
            clear_screen()
            show_logo()
            show_main_menu()
            
            choice = Prompt.ask(
                t('select_option'),
                choices=["0", "1", "2", "3", "4", "5", "6"],
                default="0"
            )
            
            # 处理用户选择
            if choice == "1":
                configure_api_key()
            elif choice == "2":
                lookup_number()
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
        clear_screen()
        console.print(f"[bold green]{t('goodbye')}[/bold green]")
    
    except Exception as e:
        logger.error(f"未处理的异常: {e}", exc_info=True)
        traceback.print_exc()
        print_error(f"{t('program_error')}: {str(e)}")
        input(f"\n{t('press_any_key')}...")

if __name__ == "__main__":
    main() 