#!/usr/bin/env python3
"""
RealCarrier - Telnyx LNP美国电话号码查询工具
Alpha 0.1.0
"""

import os
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from rich.text import Text
from rich.layout import Layout

# 将项目根目录添加到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from lnptool.config import get_api_key, set_api_key, is_configured, get_config
from lnptool.telnyx_api import TelnyxAPI
from lnptool.lookup import LookupService, display_lookup_result, display_batch_summary
from lnptool.utils import is_valid_api_key, print_error, print_success, print_warning, print_info, phone_input

console = Console()

def clear_screen():
    """清除屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_logo():
    """显示程序标志"""
    # 创建主标题面板
    console.print(Panel.fit(
        "[bold blue]RealCarrier[/bold blue] - [cyan]美国电话号码状态查询器[/cyan]",
        border_style="green",
        padding=(1, 2),
        title="v0.1.0",
        subtitle="by Yagami1997"
    ))
    console.print()

def show_main_menu():
    """显示主菜单"""
    console.print("\n[bold cyan]RealCarrier Alpha[/bold cyan] - 美国电话号码查询工具\n")
    
    # 创建带有表情符号的菜单表格
    table = Table(show_header=False, box=box.ROUNDED)
    table.add_column("选项", style="cyan")
    table.add_column("功能描述", style="white")
    
    # 为每个选项添加表情符号
    table.add_row("[1]", "🔑 API密钥配置")
    table.add_row("[2]", "📱 查询单个电话号码")
    table.add_row("[3]", "📊 批量查询CSV文件")
    table.add_row("[4]", "💾 缓存管理")
    table.add_row("[5]", "ℹ️ 系统信息")
    table.add_row("[0]", "❌ 退出程序")
    
    console.print(table)
    console.print("请选择功能 [0-5]: ", end="")

def check_api_key_status():
    """检查API密钥状态"""
    api_key = get_api_key()
    if api_key:
        status = "[bold green]已配置[/bold green]"
        # 显示密钥前4位和后4位，中间用星号
        masked_key = f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}" if len(api_key) > 8 else "******"
        return status, masked_key
    else:
        return "[bold red]未配置[/bold red]", "无"

def configure_api_key():
    """配置API密钥"""
    clear_screen()
    show_logo()
    console.print("[bold]API密钥配置[/bold]\n")
    
    # 显示当前状态
    status, masked_key = check_api_key_status()
    console.print(f"当前API密钥状态: {status}")
    if "已配置" in status:
        console.print(f"当前API密钥: {masked_key}")
        console.print()
        
        # 询问是否重新配置
        if not Confirm.ask("是否要重新配置API密钥?"):
            return
    
    # 输入新的API密钥
    console.print("请输入您的Telnyx API密钥 (通常以KEY开头):")
    api_key = Prompt.ask("> ", password=False)  # 明文显示以便确认
    
    # 确认输入
    console.print(f"\n您输入的API密钥是: [bold]{api_key}[/bold]")
    
    # 验证格式
    if not is_valid_api_key(api_key):
        print_warning("API密钥格式可能不正确，通常以KEY开头。")
        if not Confirm.ask("是否仍要保存?"):
            print_info("操作已取消。")
            return
    
    # 保存前再次确认
    if Confirm.ask("确认保存此API密钥?"):
        if set_api_key(api_key):
            print_success("API密钥已成功配置!")
            
            # 尝试验证API密钥
            console.print("\n[bold]正在验证API密钥...[/bold]")
            try:
                api = TelnyxAPI(api_key=api_key)
                # 使用正确的LNP查询端点测试API密钥
                response = api._make_request("GET", "/number_lookup/+14155552671", params={"type": "carrier"})
                print_success("API密钥验证成功!")
            except Exception as e:
                print_warning(f"API密钥验证失败: {str(e)}")
                print_info("密钥已保存，但可能无法正常工作。请检查密钥是否正确。")
        else:
            print_error("保存API密钥时出错!")
    else:
        print_info("操作已取消。")
    
    input("\n按Enter键返回主菜单...")

def lookup_number():
    """查询单个电话号码"""
    clear_screen()
    print("\n查询单个电话号码\n")
    
    # 简化提示，删除颜色标记，并确保+1后有空格
    phone_number = phone_input("请输入10位美国电话号码 (例如：877-242-7372): ", use_rich=True)
    
    # 如果用户取消输入，返回到主菜单
    if not phone_number:
        return
    
    # 检查API密钥
    if not is_configured():
        print_error("未配置API密钥！请先配置API密钥。")
        input("\n按Enter键返回主菜单...")
        return
    
    # 执行查询
    try:
        console.print("\n[bold]正在查询...[/bold]")
        service = LookupService()
        result = service.lookup_number(phone_number)
        
        # 显示结果
        console.print("\n[bold]查询结果:[/bold]")
        display_lookup_result(result)
    except Exception as e:
        print_error(f"查询失败: {str(e)}")
    
    input("\n按Enter键返回主菜单...")

def batch_lookup():
    """批量查询CSV文件"""
    clear_screen()
    show_logo()
    console.print("[bold]批量查询CSV文件[/bold]\n")
    
    # 检查API密钥
    if not is_configured():
        print_error("未配置API密钥！请先配置API密钥。")
        input("\n按Enter键返回主菜单...")
        return
    
    # 输入CSV文件路径
    console.print("请输入CSV文件路径:")
    csv_file = Prompt.ask("> ")
    
    if not Path(csv_file).exists():
        print_error(f"文件不存在: {csv_file}")
        input("\n按Enter键返回主菜单...")
        return
    
    # 输入列名
    console.print("\n请输入包含电话号码的列名 (默认: phone_number):")
    column = Prompt.ask("> ", default="phone_number")
    
    # 输入输出文件
    console.print("\n请输入结果输出文件路径 (默认: results.csv):")
    output_file = Prompt.ask("> ", default="results.csv")
    
    # 执行批量查询
    try:
        console.print("\n[bold]正在执行批量查询...[/bold]")
        service = LookupService()
        results = service.batch_lookup_from_csv(
            csv_file=csv_file,
            output_file=output_file,
            number_column=column
        )
        
        # 显示摘要
        console.print("\n[bold]查询摘要:[/bold]")
        display_batch_summary(results)
        
        print_success(f"\n结果已保存至: {output_file}")
    except Exception as e:
        print_error(f"批量查询失败: {str(e)}")
    
    input("\n按Enter键返回主菜单...")

def cache_management():
    """缓存管理"""
    from lnptool.cache import Cache
    
    while True:
        clear_screen()
        show_logo()
        console.print("[bold]缓存管理[/bold]\n")
        
        # 显示缓存菜单
        table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
        table.add_column("选项", style="cyan", justify="center")
        table.add_column("描述", style="white")
        
        table.add_row("[1]", "显示缓存统计信息")
        table.add_row("[2]", "清除所有缓存")
        table.add_row("[3]", "清除过期缓存")
        table.add_row("[4]", "显示最近查询")
        table.add_row("[0]", "返回主菜单")
        
        console.print(table)
        console.print()
        
        choice = Prompt.ask("请选择", choices=["0", "1", "2", "3", "4"], default="0")
        
        if choice == "0":
            break
        
        cache = Cache()
        
        if choice == "1":
            # 显示缓存统计信息
            try:
                stats = cache.get_stats()
                
                console.print("\n[bold]缓存统计信息:[/bold]")
                
                table = Table(box=box.ROUNDED)
                table.add_column("项目", style="cyan")
                table.add_column("值", style="green")
                
                table.add_row("总条目数", str(stats.get("total_entries", 0)))
                table.add_row("有效条目数", str(stats.get("valid_entries", 0)))
                table.add_row("过期条目数", str(stats.get("expired_entries", 0)))
                
                size_kb = stats.get("cache_size_bytes", 0) / 1024
                table.add_row("缓存大小", f"{size_kb:.2f} KB")
                
                ttl_hours = stats.get("cache_ttl_seconds", 0) / 3600
                table.add_row("缓存有效期", f"{ttl_hours:.1f} 小时")
                
                console.print(table)
            except Exception as e:
                print_error(f"获取缓存统计信息失败: {str(e)}")
        
        elif choice == "2":
            # 清除所有缓存
            if Confirm.ask("\n确定要清除所有缓存吗?"):
                try:
                    if cache.clear():
                        print_success("所有缓存已清除!")
                    else:
                        print_error("清除缓存失败!")
                except Exception as e:
                    print_error(f"清除缓存失败: {str(e)}")
        
        elif choice == "3":
            # 清除过期缓存
            try:
                count = cache.clear_expired()
                print_success(f"已清除 {count} 个过期缓存条目!")
            except Exception as e:
                print_error(f"清除过期缓存失败: {str(e)}")
        
        elif choice == "4":
            # 显示最近查询
            try:
                limit = int(Prompt.ask("\n显示多少条最近查询?", default="10"))
                recent = cache.get_recent_lookups(limit)
                
                if not recent:
                    print_info("没有找到最近的查询记录。")
                else:
                    console.print("\n[bold]最近查询记录:[/bold]")
                    
                    table = Table(box=box.ROUNDED)
                    table.add_column("电话号码", style="cyan")
                    table.add_column("查询时间", style="green")
                    
                    for number, timestamp in recent:
                        from lnptool.utils import format_timestamp
                        table.add_row(number, format_timestamp(timestamp))
                    
                    console.print(table)
            except Exception as e:
                print_error(f"获取最近查询记录失败: {str(e)}")
        
        input("\n按Enter键继续...")

def system_info():
    """显示系统信息"""
    clear_screen()
    show_logo()
    console.print("[bold]系统信息[/bold]\n")
    
    # 获取配置信息
    config = get_config()
    api_status, masked_key = check_api_key_status()
    
    table = Table(box=box.ROUNDED)
    table.add_column("项目", style="cyan")
    table.add_column("值", style="green")
    
    # 基本信息
    table.add_row("API密钥状态", api_status)
    if "已配置" in api_status:
        table.add_row("API密钥", masked_key)
    
    # 配置信息
    table.add_row("API缓存有效期", f"{config.get('api_cache_ttl', 86400) / 3600:.1f} 小时")
    table.add_row("API请求速率限制", f"{config.get('rate_limit', 2)} 请求/秒")
    
    # 缓存信息
    try:
        from lnptool.cache import Cache
        cache = Cache()
        stats = cache.get_stats()
        table.add_row("缓存条目数", str(stats.get("total_entries", 0)))
        size_kb = stats.get("cache_size_bytes", 0) / 1024
        table.add_row("缓存大小", f"{size_kb:.2f} KB")
    except Exception:
        pass
    
    # Python版本
    import platform
    table.add_row("Python版本", platform.python_version())
    
    # 系统信息
    table.add_row("操作系统", f"{platform.system()} {platform.release()}")
    
    console.print(table)
    
    input("\n按Enter键返回主菜单...")

def main():
    """主函数"""
    try:
        while True:
            clear_screen()
            show_logo()
            
            # 显示GitHub链接（靠左对齐）
            console.print(f"项目地址: [link=https://github.com/yagami1997/RealCarrier]github.com/yagami1997/RealCarrier[/link]")
            console.print()
            
            # 显示API密钥状态
            status, masked_key = check_api_key_status()
            console.print(f"API密钥状态: {status}")
            if "已配置" in status:
                console.print(f"API密钥: {masked_key}")
            console.print()
            
            # 显示主菜单
            show_main_menu()
            
            # 获取用户选择
            choice = Prompt.ask("请选择", choices=["0", "1", "2", "3", "4", "5"], default="0")
            
            if choice == "0":
                clear_screen()
                console.print("[bold green]感谢使用RealCarrier! 再见![/bold green]")
                break
            elif choice == "1":
                configure_api_key()
            elif choice == "2":
                lookup_number()
            elif choice == "3":
                batch_lookup()
            elif choice == "4":
                cache_management()
            elif choice == "5":
                system_info()
    except KeyboardInterrupt:
        clear_screen()
        console.print("[bold green]程序已退出。感谢使用RealCarrier![/bold green]")
    except Exception as e:
        console.print(f"[bold red]发生错误: {str(e)}[/bold red]")
        input("\n按Enter键退出...")

if __name__ == "__main__":
    main() 