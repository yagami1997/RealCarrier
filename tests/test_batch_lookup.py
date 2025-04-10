#!/usr/bin/env python3
"""
批量查询测试脚本
用于测试增强后的批量查询功能
"""

import sys
import os
import time
import logging
import csv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# 配置日志级别
logging.basicConfig(level=logging.INFO)

# 尝试导入必要的模块
try:
    from lnptool.telnyx_api import TelnyxAPI
    from lnptool.i18n import set_language
    from lnptool.lookup import LookupService
    from lnptool.ui import UI
except ImportError as e:
    print(f"Error: {e}")
    print("Please run this script from the project root directory.")
    sys.exit(1)

console = Console()

def test_batch_lookup(phone_numbers, use_chinese=True, output_file=None):
    """测试批量查询功能"""
    # 设置语言
    if use_chinese:
        set_language("zh_CN")
    else:
        set_language("en_US")
    
    console.print(f"\n[bold]Testing batch lookup for {len(phone_numbers)} numbers[/bold]")
    
    if not output_file:
        timestamp = int(time.time())
        output_file = f"batch_result_{timestamp}.csv"
    
    try:
        # 创建API实例
        api = TelnyxAPI()
        
        # 检查API配置
        if not api.is_configured():
            console.print("[bold red]Error: Telnyx API key not configured![/bold red]")
            console.print("Please configure API key first with: lnp config set-key")
            return
        
        # 创建查询服务
        lookup_service = LookupService()
        
        # 执行批量查询
        console.print("[bold]Starting batch lookup...[/bold]")
        
        # 使用较低的请求频率，避免触发API速率限制
        results = lookup_service.batch_lookup(phone_numbers, output_file=output_file, rate_limit=1.0)
        
        # 显示摘要
        console.print(f"\n[bold green]Batch lookup complete![/bold green]")
        console.print(f"[bold]Total numbers processed:[/bold] {len(results)}")
        console.print(f"[bold]Results saved to:[/bold] {output_file}")
        
        # 统计成功和失败的查询
        successful = sum(1 for r in results if not r.status.startswith("error:"))
        failed = len(results) - successful
        
        console.print(f"[bold]Successful lookups:[/bold] {successful}")
        console.print(f"[bold]Failed lookups:[/bold] {failed}")
        
        # 显示数据丰富度统计
        enrichment_stats = {
            "normalized_carrier": 0,
            "caller_name": 0,
            "lrn": 0,
            "fraud_info": 0
        }
        
        for result in results:
            if result.normalized_carrier:
                enrichment_stats["normalized_carrier"] += 1
            if result.caller_name:
                enrichment_stats["caller_name"] += 1
            if result.lrn:
                enrichment_stats["lrn"] += 1
            if result.fraud_info and any(result.fraud_info.values()):
                enrichment_stats["fraud_info"] += 1
        
        console.print("\n[bold]Data Enrichment Statistics:[/bold]")
        for field, count in enrichment_stats.items():
            percentage = (count / len(results)) * 100 if results else 0
            console.print(f"[bold]{field}:[/bold] {count} ({percentage:.1f}%)")
        
        # 显示第一个成功的结果作为示例
        for result in results:
            if not result.status.startswith("error:"):
                console.print("\n[bold]Sample Result:[/bold]")
                
                result_dict = {
                    "phone_number": result.phone_number,
                    "carrier": result.carrier,
                    "normalized_carrier": result.normalized_carrier,
                    "caller_name": result.caller_name,
                    "line_type": result.line_type,
                    "valid_number": result.valid_number,
                    "ported": result.ported,
                    "ported_status": result.ported_status,
                    "previous_carrier": result.previous_carrier,
                    "lrn": result.lrn,
                    "city": result.city,
                    "state": result.state,
                    "provider": result.provider
                }
                
                UI.show_lookup_result(result_dict)
                break
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def read_numbers_from_file(file_path):
    """从文件读取电话号码"""
    numbers = []
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        console.print(f"[bold red]Error: File not found: {file_path}[/bold red]")
        return numbers
    
    # 读取文件
    try:
        if file_path.endswith('.csv'):
            with open(file_path, 'r', newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip():  # 检查是否为空行
                        numbers.append(row[0].strip())
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:  # 检查是否为空行
                        numbers.append(line)
        
        # 如果第一行看起来像标题，则移除
        if numbers and any(keyword in numbers[0].lower() for keyword in ['phone', 'number', 'tel']):
            numbers = numbers[1:]
        
        return numbers
    
    except Exception as e:
        console.print(f"[bold red]Error reading file: {e}[/bold red]")
        return []

def main():
    """主函数"""
    console.print("[bold]Telnyx API Batch Lookup Test[/bold]")
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        console.print("[bold]Usage:[/bold]")
        console.print("1. Test with file: python test_batch_lookup.py <file_path> [output_file] [language]")
        console.print("2. Test with numbers: python test_batch_lookup.py -n <number1> <number2> ... [language]")
        console.print("\n[bold]Examples:[/bold]")
        console.print("python test_batch_lookup.py numbers.csv")
        console.print("python test_batch_lookup.py numbers.csv results.csv en")
        console.print("python test_batch_lookup.py -n +14062189208 +16192370374 +13129457420")
        return
    
    # 处理参数
    if sys.argv[1] == '-n':
        # 直接使用命令行提供的号码
        if len(sys.argv) < 3:
            console.print("[bold red]Error: No phone numbers provided[/bold red]")
            return
        
        phone_numbers = sys.argv[2:]
        
        # 检查最后一个参数是否是语言选项
        use_chinese = True
        output_file = None
        
        if phone_numbers[-1].lower() in ['zh', 'en']:
            use_chinese = phone_numbers[-1].lower() == 'zh'
            phone_numbers = phone_numbers[:-1]
        
        test_batch_lookup(phone_numbers, use_chinese, output_file)
    
    else:
        # 从文件读取号码
        file_path = sys.argv[1]
        
        # 获取可选参数
        output_file = None
        use_chinese = True
        
        if len(sys.argv) >= 3 and not sys.argv[2].lower() in ['zh', 'en']:
            output_file = sys.argv[2]
        
        if len(sys.argv) >= 3:
            last_arg = sys.argv[-1].lower()
            if last_arg in ['zh', 'en']:
                use_chinese = last_arg == 'zh'
        
        # 读取号码
        phone_numbers = read_numbers_from_file(file_path)
        
        if not phone_numbers:
            console.print("[bold red]Error: No valid phone numbers found in file[/bold red]")
            return
        
        console.print(f"[bold]Found {len(phone_numbers)} phone numbers in {file_path}[/bold]")
        
        # 执行批量查询
        test_batch_lookup(phone_numbers, use_chinese, output_file)

if __name__ == "__main__":
    main() 