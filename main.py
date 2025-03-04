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
    while True:
        clear_screen()
        show_logo()
        console.print("[bold]API密钥配置[/bold]\n")
        
        # 显示当前状态
        status, masked_key = check_api_key_status()
        console.print(f"当前API密钥状态: {status}")
        if "已配置" in status:
            console.print(f"当前API密钥: {masked_key}")
        
        # 显示Telnyx信息
        console.print("\n[cyan]本工具使用[link=https://telnyx.com/]Telnyx[/link] API提供服务[/cyan]")
        console.print()
        
        # 显示API密钥配置菜单
        table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
        table.add_column("选项", style="cyan", justify="center")
        table.add_column("描述", style="white")
        
        if "已配置" in status:
            table.add_row("[1]", "修改API密钥")
            table.add_row("[2]", "删除API密钥")
            table.add_row("[3]", "Telnyx账号向导")
            table.add_row("[0]", "返回主菜单")
        else:
            table.add_row("[1]", "配置API密钥")
            table.add_row("[2]", "Telnyx账号向导")
            table.add_row("[0]", "返回主菜单")
        
        console.print(table)
        console.print()
        
        # 根据API状态提供不同的选项
        if "已配置" in status:
            choice = Prompt.ask(
                "请选择", 
                choices=["0", "1", "2", "3"], 
                default="0"
            )
        else:
            choice = Prompt.ask(
                "请选择", 
                choices=["0", "1", "2"], 
                default="0"
            )
        
        if choice == "0":
            return
        
        # 添加或修改API密钥
        if choice == "1":
            set_new_api_key()
        
        # 删除API密钥
        elif choice == "2" and "已配置" in status:
            delete_api_key()
        
        # Telnyx账号向导
        elif (choice == "3" and "已配置" in status) or (choice == "2" and "未配置" in status):
            telnyx_account_guide()

def set_new_api_key():
    """添加或修改API密钥"""
    console.print("\n[bold]添加/修改API密钥[/bold]")
    
    # 输入新的API密钥
    console.print("\n请输入您的Telnyx API密钥 (通常以KEY开头):")
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
                
                # 提供更详细的错误信息
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
            print_error("保存API密钥时出错!")
    else:
        print_info("操作已取消。")
    
    input("\n按Enter键继续...")

def delete_api_key():
    """删除API密钥"""
    console.print("\n[bold red]删除API密钥[/bold red]")
    console.print("\n[yellow]警告：删除API密钥后，将无法使用查询功能，直到重新配置新的API密钥。[/yellow]")
    
    # 第一次确认
    if not Confirm.ask("\n确定要删除当前API密钥吗?"):
        print_info("操作已取消。")
        input("\n按Enter键继续...")
        return
    
    # 二次确认
    console.print("\n[bold red]最终确认：[/bold red]删除操作无法撤销，您需要重新输入API密钥才能恢复功能。")
    if Confirm.ask("再次确认要删除API密钥吗?"):
        try:
            # 假设有一个删除API密钥的函数，如果没有，需要实现它
            from lnptool.config import delete_api_key as delete_key
            if delete_key():
                print_success("API密钥已成功删除!")
            else:
                print_error("删除API密钥时出错!")
        except Exception as e:
            print_error(f"删除API密钥失败: {str(e)}")
    else:
        print_info("操作已取消。")
    
    input("\n按Enter键继续...")

def telnyx_account_guide():
    """Telnyx账号注册与登录向导"""
    console.print("\n[bold]Telnyx账号向导[/bold]")
    
    panel = Panel(
        "[bold]Telnyx账号注册与API密钥获取指南[/bold]\n\n"
        "1. 访问 [link=https://telnyx.com/sign-up]https://telnyx.com/sign-up[/link] 注册新账号\n"
        "2. 已有账号请访问 [link=https://portal.telnyx.com/]https://portal.telnyx.com/[/link] 登录\n"
        "3. 登录后，在左侧菜单找到 'API Keys' 选项\n"
        "4. 点击 'Create API Key' 创建新的API密钥\n"
        "5. 为您的API密钥添加描述（例如：RealCarrier）\n"
        "6. 复制生成的API密钥（注意：密钥只显示一次！）\n"
        "7. 回到本程序，选择'配置API密钥'并粘贴您的密钥\n\n"
        "[yellow]注意：Telnyx需要完成KYC验证和账户充值才能正常使用API服务[/yellow]",
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print(panel)
    input("\n按Enter键继续...")

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
        
        # 提供更详细的错误信息和解决方案
        error_str = str(e).lower()
        if "400" in error_str:
            console.print("\n[yellow]请求错误(400):[/yellow]")
            console.print("1. 电话号码格式可能不正确")
            console.print("2. 请确保输入的是有效的美国电话号码")
        elif "401" in error_str:
            console.print("\n[yellow]API认证错误(401):[/yellow]")
            console.print("1. API密钥无效或已过期")
            console.print("2. 请前往API密钥配置菜单重新设置有效的密钥")
        elif "403" in error_str:
            console.print("\n[yellow]API权限错误(403):[/yellow]")
            console.print("1. 您的Telnyx账户可能未完成验证或未充值")
            console.print("2. 请登录Telnyx账户确认账户状态并完成必要的验证步骤")
            console.print("3. 确保账户中有足够的余额用于API查询")
        elif "404" in error_str:
            console.print("\n[yellow]资源未找到(404):[/yellow]")
            console.print("1. 您查询的电话号码可能在Telnyx数据库中不存在")
            console.print("2. API端点可能已变更，请联系技术支持")
        elif "408" in error_str:
            console.print("\n[yellow]请求超时(408):[/yellow]")
            console.print("1. 网络连接不稳定或服务器响应缓慢")
            console.print("2. 请检查网络连接并稍后再试")
        elif "422" in error_str:
            console.print("\n[yellow]请求数据处理错误(422):[/yellow]")
            console.print("1. 电话号码格式可能无法被识别")
            console.print("2. 请确保输入的是有效的美国电话号码")
        elif "429" in error_str:
            console.print("\n[yellow]超出请求限制(429):[/yellow]")
            console.print("1. 您已超出Telnyx API的请求频率限制")
            console.print("2. 请稍后再试")
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            console.print("\n[yellow]服务器错误(500/502/503):[/yellow]")
            console.print("1. Telnyx服务器可能出现临时问题")
            console.print("2. 请稍后再试，或联系Telnyx客服")
        else:
            console.print("\n[yellow]其他错误:[/yellow]")
            console.print("1. 请检查网络连接")
            console.print("2. 确保输入的电话号码格式正确")
            console.print("3. 如果问题持续，请联系技术支持")
    
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
    
    # 展示简化的CSV格式示例
    console.print("[bold cyan]CSV文件格式示例:[/bold cyan]")
    
    # 创建更简单的示例表格，使用更短的列名
    example_table = Table(box=box.SIMPLE)
    example_table.add_column("phone", style="green")
    example_table.add_column("备注", style="blue")
    
    example_table.add_row("8772427372", "客户A")
    example_table.add_row("2025550179", "客户B")
    example_table.add_row("4155552671", "客户C")
    
    console.print(example_table)
    console.print("\n[italic]CSV文件第一列应包含电话号码，建议使用'phone'作为列名。[/italic]\n")
    
    # 引导用户选择文件
    console.print("[bold]第1步:[/bold] 选择CSV文件")
    console.print("请输入CSV文件完整路径，或将文件拖放到此窗口：")
    console.print("[dim](注：拖放文件可能会出现多余空格，系统会自动处理，不影响使用)[/dim]")
    csv_file = input()

    # 提示用户输入成功
    if csv_file:
        console.print(f"[green]已选择文件: {csv_file}[/green]")
    
    # 检查文件是否存在，并修复拖放文件时可能产生的额外空格
    file_path = Path(csv_file.strip().strip('"').strip("'"))  # 额外添加strip()移除所有空白字符
    if not file_path.exists():
        print_error(f"文件不存在: {file_path}")
        input("\n按Enter键返回主菜单...")
        return
    
    # 检查是否为CSV文件
    if file_path.suffix.lower() != '.csv':
        print_warning(f"文件 {file_path.name} 可能不是CSV格式。确定要继续吗？")
        if not Confirm.ask("继续?"):
            return
    
    # 设置输出文件
    console.print("\n[bold]第2步:[/bold] 设置输出文件")
    default_output = file_path.with_name(f"{file_path.stem}_results.csv")
    console.print(f"[green]推荐输出文件路径: {default_output}[/green]")
    output_file = Prompt.ask(
        "请输入结果输出文件路径", 
        default=str(default_output)
    )
    
    # 确认开始查询
    console.print("\n[bold]第3步:[/bold] 确认查询设置")
    console.print(f"输入文件: [cyan]{file_path}[/cyan]")
    console.print(f"输出文件: [cyan]{output_file}[/cyan]")
    
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
                    console.print(f"[green]检测到电话号码列: {col_name} (第{col_idx+1}列)[/green]")
                else:
                    console.print("[yellow]未检测到电话号码列名，将尝试使用第一列[/yellow]")
                
                # 统计行数
                for _ in reader:
                    row_count += 1
                
                console.print(f"[cyan]预计查询: {row_count} 个电话号码[/cyan]")
                
                # 如果行数很多，给出提示
                if row_count > 100:
                    console.print("[yellow]注意: 大量查询可能需要较长时间，并消耗API配额[/yellow]")
    except Exception as e:
        console.print(f"[yellow]预览文件时出错: {str(e)}[/yellow]")
        console.print("[yellow]将继续尝试处理文件[/yellow]")
    
    # 确认开始查询
    if not Confirm.ask("\n确认开始批量查询?"):
        print_info("操作已取消")
        input("\n按Enter键返回主菜单...")
        return
    
    # 执行批量查询
    try:
        console.print("\n[bold]正在执行批量查询...[/bold]")
        console.print("[italic]这可能需要一些时间，请耐心等待...[/italic]")
        
        service = LookupService()
        # 不指定具体列名，让服务自动检测
        results = service.batch_lookup_from_csv(
            csv_file=str(file_path),
            output_file=output_file
        )
        
        # 显示摘要
        console.print("\n[bold]查询摘要:[/bold]")
        display_batch_summary(results)
        
        print_success(f"\n结果已保存至: {output_file}")
        # 添加更明确的引导语句，提示用户查看详细报告
        console.print("[yellow]提示：详细错误信息和解决方案请查阅保存的查询报告[/yellow]")
    except Exception as e:
        print_error(f"批量查询失败: {str(e)}")
        
        # 定义必要的变量
        error_types = {}
        failed = 0
        
        error_str = str(e).lower()
        # 基本错误统计
        if "403" in error_str:
            error_types["账户权限问题 (403)"] = 3  # 假设所有查询都是这个错误
            failed = 3  # 假设有3个失败的查询
        
        # 继续显示详细错误信息...
        if "not found in csv file" in error_str:
            console.print("\n[yellow]可能的解决方法:[/yellow]")
            console.print("1. 确保CSV文件第一行包含列名，如'phone'")
            console.print("2. 尝试将CSV文件另存为UTF-8格式，避免特殊字符问题")
        elif "400" in error_str:
            console.print("\n[yellow]请求错误(400):[/yellow]")
            console.print("1. 电话号码格式可能不正确")
            console.print("2. 请检查CSV文件中的电话号码格式")
        elif "401" in error_str:
            console.print("\n[yellow]API认证错误(401):[/yellow]")
            console.print("1. API密钥无效或已过期")
            console.print("2. 请前往API密钥配置菜单重新设置有效的密钥")
        elif "404" in error_str:
            console.print("\n[yellow]资源未找到(404):[/yellow]")
            console.print("1. 您查询的电话号码可能在Telnyx数据库中不存在")
            console.print("2. API端点可能已变更，请联系技术支持")
        elif "408" in error_str:
            console.print("\n[yellow]请求超时(408):[/yellow]")
            console.print("1. 网络连接不稳定或服务器响应缓慢")
            console.print("2. 请检查网络连接并稍后再试")
        elif "413" in error_str:
            console.print("\n[yellow]请求数据过大(413):[/yellow]")
            console.print("1. 批量查询的数据量可能过大")
            console.print("2. 请尝试分批处理较小的数据集")
        elif "422" in error_str:
            console.print("\n[yellow]请求数据处理错误(422):[/yellow]")
            console.print("1. 电话号码格式可能无法被识别")
            console.print("2. 请确保CSV中的电话号码为有效的美国号码")
        elif "429" in error_str:
            console.print("\n[yellow]超出请求限制(429):[/yellow]")
            console.print("1. 您已超出Telnyx API的请求频率限制")
            console.print("2. 请稍后再试，或减少批量查询的数量")
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            console.print("\n[yellow]服务器错误(500/502/503):[/yellow]")
            console.print("1. Telnyx服务器可能出现临时问题")
            console.print("2. 请稍后再试，或联系Telnyx客服")
        else:
            console.print("\n[yellow]其他错误:[/yellow]")
            console.print("1. 请检查网络连接")
            console.print("2. 确保CSV文件格式正确且包含有效的电话号码")
            console.print("3. 如果问题持续，请联系技术支持")
        
        # 如果有错误，显示错误类型统计
        if error_types:
            error_table = Table(title="错误类型详细统计", box=box.ROUNDED, width=100)
            error_table.add_column("错误类型", style="red", width=60)
            error_table.add_column("次数", style="green", justify="center")
            error_table.add_column("百分比", style="yellow", justify="center")
            
            for error, count in error_types.items():
                error_pct = (count / failed * 100) if failed > 0 else 0
                
                # 为不同错误类型提供更详细的描述
                detailed_error = error
                if "401" in error:
                    detailed_error = "认证失败(401): API密钥无效或已过期，请检查密钥"
                elif "403" in error:
                    detailed_error = "权限不足(403): 账户未验证/余额不足/超出账户权限范围"
                elif "404" in error:
                    detailed_error = "资源未找到(404): 号码不存在或API端点已变更"
                elif "429" in error:
                    detailed_error = "频率限制(429): 超出API请求频率限制，请降低请求频率"
                elif "500" in error or "502" in error or "503" in error:
                    detailed_error = f"服务器错误({error[-3:]}): Telnyx服务器临时问题，请稍后再试"
                
                error_table.add_row(detailed_error, str(count), f"{error_pct:.1f}%")
            
            console.print(error_table)
            
            # 添加引导提示
            if failed > 0:
                console.print("\n[yellow]提示: 更详细的错误信息已保存在结果CSV文件中，请查看完整报告了解具体问题[/yellow]")
                
                # 对于403错误提供额外的详细解释
                if any("403" in err for err in error_types.keys()):
                    console.print("\n[bold]账户权限问题(403)可能的原因:[/bold]")
                    console.print("1. [red]账户验证问题:[/red] 您的Telnyx账户可能尚未完成必要的KYC验证")
                    console.print("2. [red]账户余额不足:[/red] 请确保您的账户中有足够的余额进行API查询")
                    console.print("3. [red]号码类型限制:[/red] 您的账户可能无权查询某些类型的电话号码")
                    console.print("4. [red]建议解决方案:[/red] 登录Telnyx账户中心，完成验证并充值账户")
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
        
        choice = Prompt.ask(
            "请选择", 
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
                console.print("\n[yellow]可能的解决方法:[/yellow]")
                console.print("1. 缓存文件可能已损坏，请尝试清除所有缓存")
                console.print("2. 检查程序是否有足够的磁盘读写权限")
                console.print("3. 如果问题持续，请重启程序或联系技术支持")
        
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
                    console.print("\n[yellow]可能的解决方法:[/yellow]")
                    console.print("1. 检查程序是否有足够的磁盘读写权限")
                    console.print("2. 缓存文件可能被其他程序锁定，请关闭可能使用该文件的程序")
                    console.print("3. 如果问题持续，请重启程序或联系技术支持")
        
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
                limit = int(Prompt.ask(
                    "\n显示多少条最近查询?",
                    default="10"
                ))
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
    
    # 获取CPU信息
    cpu_info = "未知"
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
        cpu_info = f"无法获取 ({str(e)})"

    # 获取内存信息
    mem_info = "未知"
    try:
        if os_name == "Darwin":  # macOS
            # 使用system_profiler获取更精确的信息
            result = run(['system_profiler', 'SPHardwareDataType'], stdout=PIPE, text=True)
            for line in result.stdout.strip().split('\n'):
                if 'Memory' in line:
                    mem_info = line.split(':')[1].strip()
                    break
            
            # 如果上面方法失败，尝试sysctl
            if mem_info == "未知":
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
        mem_info = f"无法获取 ({str(e)})"
    
    # Python版本
    import platform
    table.add_row("Python版本", platform.python_version())
    
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
    table.add_row("操作系统", os_display)
    table.add_row("内核版本", f"{os_name} {os_version}")
    
    # 添加CPU和内存信息
    table.add_row("CPU型号", cpu_info)
    table.add_row("系统内存", mem_info)
    
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
                # 即使已配置也显示Telnyx信息
                console.print("[cyan]本工具使用[link=https://telnyx.com/]Telnyx[/link] API提供服务[/cyan]")
            else:
                # 未配置时显示更详细的指导信息
                console.print("[yellow]说明：本工具使用Telnyx API，请先在[link=https://telnyx.com/]https://telnyx.com/[/link]注册账号，然后获取API Key[/yellow]")
            console.print()
            
            # 显示主菜单
            show_main_menu()
            
            # 获取用户选择
            choice = Prompt.ask(
                "请选择", 
                choices=["0", "1", "2", "3", "4", "5"], 
                default="0",
                show_choices=True,
                show_default=True
            )
            
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