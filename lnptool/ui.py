"""
用户界面模块 - 提供TUI（文本用户界面）组件和功能
"""

import os
import sys
import platform
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.layout import Layout

from lnptool.i18n import t
from lnptool.utils import print_error, print_success, print_warning, print_info, format_phone_number

# 初始化控制台
console = Console()

class UI:
    """用户界面类，提供TUI组件和功能"""
    
    @staticmethod
    def clear_screen() -> None:
        """清除屏幕"""
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
    
    @staticmethod
    def show_logo() -> None:
        """显示应用程序标志"""
        console = Console()
        
        # 导入国际化函数
        from lnptool.i18n import t
        
        # 设置ASCII艺术字符logo
        logo_text = """
 ____            _  ____                _           
|  _ \ ___  __ _| |/ ___|__ _ _ __ _ __(_) ___ _ __ 
| |_) / _ \/ _` | | |   / _` | '__| '__| |/ _ \ '__|
|  _ <  __/ (_| | | |__| (_| | |  | |  | |  __/ |   
|_| \_\___|\__,_|_|\____\__,_|_|  |_|  |_|\___|_|   
        """
        
        # 设置版本和其他信息
        version_text = "Beta v1.0.0"
        subtitle_text = t("supports_telnyx_twilio") if t("supports_telnyx_twilio") != "supports_telnyx_twilio" else "支持 Telnyx & Twilio API"
        author_text = "By Yagami"
        repo_text = t("repository_address") + ": https://github.com/yagami1997/RealCarrier"
        
        # 获取API配置状态
        from lnptool.telnyx_api import TelnyxAPI
        from lnptool.twilio_api import TwilioAPI
        
        # 实例化API客户端并检查状态
        telnyx_api = TelnyxAPI()
        twilio_api = TwilioAPI()
        
        # 获取各提供商状态
        configured_text = t("configured") if t("configured") != "configured" else "已配置"
        not_configured_text = t("not_configured") if t("not_configured") != "not_configured" else "未配置"
        telnyx_status = f"[green]{configured_text}[/green]" if telnyx_api.is_configured() else f"[red]{not_configured_text}[/red]"
        twilio_status = f"[green]{configured_text}[/green]" if twilio_api.is_configured() else f"[red]{not_configured_text}[/red]"
        
        api_status_text = f"Telnyx API: {telnyx_status}\nTwilio API: {twilio_status}"
        
        # 创建标志面板
        panel = Panel(
            f"[bold cyan]{logo_text}[/bold cyan]\n" +
            f"[yellow]{version_text}[/yellow]\n" +
            f"[white]{subtitle_text}[/white]\n" +
            f"[green]{author_text}[/green]\n" +
            f"[blue]{repo_text}[/blue]\n" +
            f"{api_status_text}",
            title=f"[bold]{t('app_title')}[/bold]",
            border_style="cyan",
            expand=False
        )
        
        console.print(panel)
    
    @staticmethod
    def show_main_menu() -> None:
        """显示主菜单"""
        console.print(f"\n[bold]{t('main_menu')}[/bold]\n")
        
        # 显示菜单选项
        console.print(f"[bold]1.[/bold] {t('menu_option_1')}")
        console.print(f"[bold]2.[/bold] {t('menu_option_2')}")
        console.print(f"[bold]3.[/bold] {t('menu_option_3')}")
        console.print(f"[bold]4.[/bold] {t('menu_option_4')}")
        console.print(f"[bold]5.[/bold] {t('menu_option_5')}")
        console.print(f"[bold]6.[/bold] {t('menu_option_6')}")
        console.print(f"[bold]0.[/bold] {t('menu_option_0')}")
    
    @staticmethod
    def show_api_config_menu(is_configured: bool, api_key: Optional[str] = None) -> None:
        """
        显示API配置菜单
        
        Args:
            is_configured: API是否已配置
            api_key: 当前API密钥（如果已配置）
        """
        console.print(f"\n[bold]{t('api_config_title')}[/bold]\n")
        
        # 显示当前状态
        status_table = Table(show_header=False, box=box.SIMPLE)
        status_table.add_column("Item", style="cyan")
        status_table.add_column("Value")
        
        status_text = f"[green]{t('configured')}[/green]" if is_configured else f"[red]{t('not_configured')}[/red]"
        key_text = f"[dim]{'*' * 8}{api_key[-4:]}[/dim]" if api_key else f"[dim]{t('none')}[/dim]"
        
        status_table.add_row(t('api_status'), status_text)
        status_table.add_row(t('current_api_key'), key_text)
        
        console.print(status_table)
        console.print("")
        
        # 显示菜单选项
        if is_configured:
            console.print(f"[bold]1.[/bold] {t('modify_api_key')}")
            console.print(f"[bold]2.[/bold] {t('delete_api_key')}")
        else:
            console.print(f"[bold]1.[/bold] {t('config_api_key')}")
        
        console.print(f"[bold]0.[/bold] {t('return_main')}")
    
    @staticmethod
    def show_lookup_result(result: Dict[str, Any]) -> None:
        """
        显示查询结果
        
        Args:
            result: 查询结果字典
        """
        # 创建结果表格
        result_table = Table(box=box.ROUNDED, show_header=False)
        result_table.add_column(t('field'), style="cyan")
        result_table.add_column(t('value'), style="white")
        
        # 格式化电话号码
        phone_number = result.get('phone_number', t('unknown'))
        if phone_number and phone_number != t('unknown'):
            import re
            # 移除所有非数字字符
            phone_digits = re.sub(r'\D', '', phone_number)
            # 如果是11位且以1开头，去掉1
            if len(phone_digits) == 11 and phone_digits.startswith('1'):
                phone_digits = phone_digits[1:]
            # 如果是10位，则格式化为(XXX) XXX-XXXX
            if len(phone_digits) == 10:
                display_phone = format_phone_number(phone_digits)
                phone_number = display_phone
        
        # 添加基本信息
        result_table.add_row(t('phone_number'), f"[bold]{phone_number}[/bold]")
        result_table.add_row(t('carrier'), f"[yellow]{result.get('carrier', t('unknown'))}[/yellow]")
        
        # 添加线路类型（使用不同颜色）
        line_type = result.get('line_type', t('unknown'))
        if line_type == 'mobile':
            line_type_display = f"[green]{t('mobile_phone')}[/green]"
        elif line_type == 'landline':
            line_type_display = f"[blue]{t('landline_phone')}[/blue]"
        elif line_type == 'voip':
            line_type_display = f"[magenta]{t('voip_phone')}[/magenta]"
        else:
            line_type_display = f"[dim]{t('unknown')}[/dim]"
        result_table.add_row(t('line_type'), line_type_display)
        
        # 添加其他信息
        if result.get('portable') is not None:
            result_table.add_row(t('portable'), f"[green]{t('yes')}[/green]" if result['portable'] else f"[red]{t('no')}[/red]")
        
        # 添加查询提供商信息
        result_table.add_row(t('query_provider'), f"[blue]{result.get('provider', t('unknown'))}[/blue]")
        
        # 显示结果面板
        console.print(Panel(
            result_table,
            title=f"[bold]📋 {t('query_result')}[/bold]",
            border_style="green"
        ))
    
    @staticmethod
    def show_batch_summary(total, success, failed, output_path):
        """显示批量查询结果摘要"""
        console = Console()
        
        console.print(f"\n[bold green]{t('batch_query_complete')}![/]")
        
        # 创建表格
        table = Table(title=t('query_result_summary'), show_header=True, header_style="bold cyan")
        table.add_column(t('item'), style="cyan")
        table.add_column(t('count'), style="yellow")
        
        # 添加行
        table.add_row(t('total'), str(total))
        table.add_row(t('success'), str(success))
        table.add_row(t('failed'), str(failed))
        table.add_row(t('success_rate'), f"{success/total*100:.2f}%" if total > 0 else "0%")
        
        # 显示表格
        console.print(table)
        
        # 显示输出文件路径
        console.print(f"\n[bold]{t('result_saved_to')}:[/] [green]{output_path}[/]")
    
    @staticmethod
    def show_cache_stats(stats: Dict[str, Any]) -> None:
        """
        显示缓存统计信息
        
        Args:
            stats: 缓存统计信息字典
        """
        # 创建统计表格
        stats_table = Table(box=box.ROUNDED)
        stats_table.add_column(t('item'), style="cyan")
        stats_table.add_column(t('value'))
        
        # 添加统计行
        for item, value in stats.items():
            stats_table.add_row(t(item), str(value))
        
        # 显示表格
        console.print(Panel(stats_table, title=f"[bold]{t('cache_stats')}[/bold]", border_style="magenta"))
    
    @staticmethod
    def show_system_info(info: Dict[str, Any]) -> None:
        """
        显示系统信息
        
        Args:
            info: 系统信息字典
        """
        # 创建系统信息表格
        info_table = Table(box=box.ROUNDED)
        info_table.add_column(t('item'), style="cyan")
        info_table.add_column(t('value'))
        
        # 添加信息行
        for item, value in info.items():
            info_table.add_row(t(item), str(value))
        
        # 显示表格
        console.print(Panel(info_table, title=f"[bold]{t('system_info')}[/bold]", border_style="yellow"))
    
    @staticmethod
    def show_language_settings(current_language: str) -> None:
        """
        显示语言设置
        
        Args:
            current_language: 当前语言代码
        """
        console.print(f"\n[bold]{t('language_settings')}[/bold]\n")
        
        # 显示当前语言
        current_language_display = t("language_zh") if current_language == 'zh_CN' else t("language_en")
        console.print(f"{t('current_language')}: [cyan]{current_language_display}[/cyan]\n")
        
        # 显示选项
        console.print(f"[bold]1.[/bold] {t('language_zh')} (Chinese)")
        console.print(f"[bold]2.[/bold] {t('language_en')} (English)")
        console.print(f"[bold]0.[/bold] {t('return_main')}")
    
    @staticmethod
    def show_provider_info(provider_info: Dict[str, Any]) -> None:
        """
        显示提供商信息
        
        Args:
            provider_info: 提供商信息字典
        """
        # 创建提供商信息表格
        info_table = Table(box=box.ROUNDED)
        info_table.add_column(t('item'), style="cyan")
        info_table.add_column(t('value'))
        
        # 添加信息行
        for item, value in provider_info.items():
            if isinstance(value, bool):
                formatted_value = f"[green]是[/green]" if value else f"[red]否[/red]"
            else:
                formatted_value = str(value)
            
            info_table.add_row(t(item), formatted_value)
        
        # 显示表格
        console.print(Panel(info_table, title=f"[bold]{t('provider_info')}[/bold]", border_style="blue"))
    
    @staticmethod
    def show_single_lookup_menu(last_provider=None):
        """显示单号查询菜单"""
        console = Console()
        
        # 显示上次使用的API提供商（如果有）
        if last_provider:
            provider_name = "Telnyx" if last_provider == "telnyx" else "Twilio"
            console.print(f"\n[bold cyan]{t('last_used_api_provider')}:[/] [yellow]{provider_name}[/]")
        
        # 显示菜单选项
        console.print(f"\n[bold]{t('select_query_interface')}:[/]")
        console.print(f"[bold cyan]1.[/] {t('use')} [yellow]Telnyx[/] API")
        console.print(f"[bold cyan]2.[/] {t('use')} [yellow]Twilio[/] API")
        
        if last_provider:
            console.print(f"[bold cyan]3.[/] {t('use_last_provider')} ([yellow]{provider_name}[/])")
        
        console.print(f"[bold cyan]0.[/] {t('return_main')}")
        console.print("")
    
    @staticmethod
    def show_phone_input() -> None:
        """显示电话号码输入提示"""
        console.print(Panel(
            f"📝 {t('enter_us_phone')}:\n" +
            f"[dim]• {t('supported_format')}: {t('ten_digits')} ({t('example')}: 866-377-0294)\n" +
            f"• {t('country_code_auto_added')}[/dim]",
            border_style="blue"
        ))
    
    @staticmethod
    def show_phone_confirmation(formatted_number: str) -> None:
        """显示电话号码确认"""
        # 如果电话号码是E.164格式（+1XXXXXXXXXX），则转换为(XXX) XXX-XXXX格式
        import re
        
        # 移除所有非数字字符
        phone_digits = re.sub(r'\D', '', formatted_number)
        
        # 如果是11位且以1开头，去掉1
        if len(phone_digits) == 11 and phone_digits.startswith('1'):
            phone_digits = phone_digits[1:]
        
        # 如果是10位，则格式化为(XXX) XXX-XXXX
        if len(phone_digits) == 10:
            display_number = format_phone_number(phone_digits)
        else:
            display_number = formatted_number
        
        console.print(Panel(
            f"{t('your_input_number')}: [bold]{display_number}[/bold]\n" +
            f"{t('confirm_continue_query')}[Y/n]",
            border_style="blue"
        ))
    
    @staticmethod
    def show_lookup_progress() -> None:
        """显示查询进度"""
        console.print(f"[bold]🔍 {t('querying')}...[/bold]")
    
    @staticmethod
    def show_lookup_error(error: str) -> None:
        """显示查询错误信息"""
        console = Console()
        
        # 确保错误信息不为空
        if not error or error == "None":
            error = t('unknown_error_check_api')
        
        # 创建错误面板
        error_panel = Panel(
            f"[bold red]❌ {t('query_failed')}[/bold red]\n[white]{error}[/white]",
            title=t('error_message'),
            border_style="red"
        )
        
        console.print(error_panel)
    
    @staticmethod
    def show_return_prompt() -> None:
        """显示返回提示"""
        console.print(f"\n[dim]{t('press_enter_return')}...[/dim]") 