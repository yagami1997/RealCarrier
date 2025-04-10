#!/usr/bin/env python3
"""
Telnyx API 功能测试脚本
用于测试增强后的TelnyxAPI功能
"""

import sys
import logging
from rich.console import Console
from rich.table import Table

# 配置日志级别
logging.basicConfig(level=logging.INFO)

# 尝试导入必要的模块
try:
    from lnptool.telnyx_api import TelnyxAPI
    from lnptool.i18n import set_language
    from lnptool.ui import UI
except ImportError as e:
    print(f"Error: {e}")
    print("Please run this script from the project root directory.")
    sys.exit(1)

console = Console()

def test_lookup_number(phone_number: str, use_chinese: bool = True):
    """测试号码查询功能"""
    # 设置语言
    if use_chinese:
        set_language("zh_CN")
    else:
        set_language("en_US")
    
    console.print(f"\n[bold]Testing phone number lookup for: {phone_number}[/bold]")
    
    try:
        # 创建API实例
        api = TelnyxAPI()
        
        # 检查API配置
        if not api.is_configured():
            console.print("[bold red]Error: Telnyx API key not configured![/bold red]")
            console.print("Please configure API key first with: lnp config set-key")
            return
        
        # 执行查询
        console.print("[bold]Querying...[/bold]")
        result = api.lookup_number(phone_number)
        
        # 显示查询结果
        if result:
            # 转换为字典以便显示
            result_dict = {
                "phone_number": result.phone_number,
                "carrier": result.carrier,
                "normalized_carrier": result.normalized_carrier,
                "caller_name": result.caller_name,
                "line_type": result.line_type,
                "valid_number": result.valid_number,
                "portable": result.portable,
                "ported": result.ported,
                "ported_status": result.ported_status,
                "ported_date": result.ported_date,
                "previous_carrier": result.previous_carrier,
                "city": result.city,
                "state": result.state,
                "lrn": result.lrn,
                "fraud_info": str(result.fraud_info) if result.fraud_info else None,
                "record_type": result.record_type,
                "provider": result.provider,
                "raw_data": str(result.raw_data)[:100] + "..." if result.raw_data else None
            }
            
            # 通过UI显示结果
            UI.show_lookup_result(result_dict)
            
            # 也显示原始数据摘要
            console.print("\n[bold]Raw Data Preview:[/bold]")
            table = Table(show_header=True)
            table.add_column("Field", style="cyan")
            table.add_column("Value")
            
            # 添加原始数据的关键部分
            if result.raw_data and "data" in result.raw_data:
                data = result.raw_data.get("data", {})
                
                # 显示carrier信息
                carrier_info = data.get("carrier", {})
                if carrier_info:
                    carrier_str = str({k: v for k, v in carrier_info.items() if v is not None})
                    table.add_row("carrier", carrier_str)
                
                # 显示caller_name信息
                caller_info = data.get("caller_name", {})
                if caller_info:
                    caller_str = str({k: v for k, v in caller_info.items() if v is not None})
                    table.add_row("caller_name", caller_str)
                
                # 显示portability信息
                port_info = data.get("portability", {})
                if port_info:
                    port_str = str({k: v for k, v in port_info.items() if v is not None})
                    table.add_row("portability", port_str)
                
                # 显示fraud信息
                fraud_info = data.get("fraud", {})
                if fraud_info:
                    fraud_str = str({k: v for k, v in fraud_info.items() if v is not None})
                    table.add_row("fraud", fraud_str)
                
                table.add_row("valid_number", str(data.get("valid_number")))
                table.add_row("record_type", str(data.get("record_type")))
            
            console.print(table)
        else:
            console.print("[bold red]No result returned![/bold red]")
    
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def main():
    """主函数"""
    console.print("[bold]Telnyx API Enhanced Features Test[/bold]")
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        console.print("[bold]Usage: python test_telnyx_api.py <phone_number> [language][/bold]")
        console.print("Example: python test_telnyx_api.py +14062189208 en")
        console.print("Language options: zh (Chinese, default), en (English)")
        return
    
    # 获取电话号码
    phone_number = sys.argv[1]
    
    # 获取语言设置
    use_chinese = True
    if len(sys.argv) >= 3 and sys.argv[2].lower() == "en":
        use_chinese = False
    
    # 执行测试
    test_lookup_number(phone_number, use_chinese)

if __name__ == "__main__":
    main() 