"""
查询业务逻辑模块 - 处理电话号码查询的核心逻辑
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import csv
import json
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from lnptool.telnyx_api import TelnyxAPI, LookupResult
from lnptool.cache import Cache
from lnptool.config import get_api_key, is_configured

logger = logging.getLogger(__name__)
console = Console()


class LookupService:
    """电话号码查询服务"""
    
    def __init__(self, use_cache: bool = True):
        """
        初始化查询服务
        
        Args:
            use_cache: 是否使用缓存
        """
        self.api = TelnyxAPI()
        self.cache = Cache() if use_cache else None
        self.use_cache = use_cache
    
    def lookup_number(self, phone_number: str) -> LookupResult:
        """
        查询单个电话号码
        
        Args:
            phone_number: 要查询的电话号码
            
        Returns:
            LookupResult: 查询结果
        """
        # 格式化电话号码
        formatted_number = TelnyxAPI._format_phone_number(phone_number)
        
        # 检查是否配置了API密钥
        if not is_configured():
            console.print("[bold red]错误：未配置API密钥。[/bold red]请先运行 'lnp config set-key' 设置API密钥。")
            raise RuntimeError("API key not configured")
        
        # 检查缓存
        cache_hit = False
        if self.use_cache and self.cache:
            cached_result = self.cache.get(formatted_number)
            if cached_result:
                logger.debug(f"Cache hit for {formatted_number}")
                cache_hit = True
                try:
                    # 处理缓存数据，确保所有字段类型正确
                    self._sanitize_cached_data(cached_result)
                    # 从缓存创建结果对象
                    return LookupResult.parse_obj(cached_result)
                except Exception as e:
                    logger.error(f"Error parsing cached result: {e}")
                    cache_hit = False
        
        if not cache_hit:
            # 通过API查询
            with console.status(f"查询号码 {formatted_number} 中...", spinner="dots"):
                result = self.api.lookup_number(formatted_number)
                
                # 缓存结果（如果查询成功）
                if result.status == "success" and self.use_cache and self.cache:
                    self.cache.set(formatted_number, result.dict())
                
                return result
    
    def _sanitize_cached_data(self, data: Dict[str, Any]) -> None:
        """
        确保缓存数据中的字段类型正确，防止出现类型错误
        
        Args:
            data: 要清理的缓存数据
        """
        # 确保基本字段类型正确
        if "phone_number" in data and not isinstance(data["phone_number"], str):
            data["phone_number"] = str(data["phone_number"]) if data["phone_number"] is not None else ""
            
        if "country_code" in data and not isinstance(data["country_code"], str):
            data["country_code"] = str(data["country_code"]) if data["country_code"] is not None else "US"
            
        if "status" in data and not isinstance(data["status"], str):
            data["status"] = str(data["status"]) if data["status"] is not None else "unknown"
            
        if "request_id" in data and data["request_id"] is not None and not isinstance(data["request_id"], str):
            data["request_id"] = str(data["request_id"])
        
        # 处理carrier字段
        if "carrier" in data and isinstance(data["carrier"], dict):
            carrier = data["carrier"]
            
            if "name" in carrier and not isinstance(carrier["name"], str):
                carrier["name"] = str(carrier["name"]) if carrier["name"] is not None else "Unknown"
                
            if "type" in carrier and not isinstance(carrier["type"], str):
                carrier["type"] = str(carrier["type"]) if carrier["type"] is not None else "Unknown"
                
            if "mobile_country_code" in carrier and carrier["mobile_country_code"] is not None and not isinstance(carrier["mobile_country_code"], str):
                carrier["mobile_country_code"] = str(carrier["mobile_country_code"])
                
            if "mobile_network_code" in carrier and carrier["mobile_network_code"] is not None and not isinstance(carrier["mobile_network_code"], str):
                carrier["mobile_network_code"] = str(carrier["mobile_network_code"])
        
        # 处理portability字段
        if "portability" in data and isinstance(data["portability"], dict):
            portability = data["portability"]
            
            if "portable" in portability and not isinstance(portability["portable"], bool):
                portability["portable"] = bool(portability["portable"])
                
            if "ported" in portability and not isinstance(portability["ported"], bool):
                portability["ported"] = bool(portability["ported"])
                
            if "spid" in portability and portability["spid"] is not None and not isinstance(portability["spid"], str):
                portability["spid"] = str(portability["spid"])
                
            if "ocn" in portability and portability["ocn"] is not None and not isinstance(portability["ocn"], str):
                portability["ocn"] = str(portability["ocn"])
            
            # 处理previous_carrier字段
            if "previous_carrier" in portability and isinstance(portability["previous_carrier"], dict):
                prev_carrier = portability["previous_carrier"]
                
                if "name" in prev_carrier and not isinstance(prev_carrier["name"], str):
                    prev_carrier["name"] = str(prev_carrier["name"]) if prev_carrier["name"] is not None else "Unknown"
                    
                if "type" in prev_carrier and not isinstance(prev_carrier["type"], str):
                    prev_carrier["type"] = str(prev_carrier["type"]) if prev_carrier["type"] is not None else "Unknown"
                    
                if "mobile_country_code" in prev_carrier and prev_carrier["mobile_country_code"] is not None and not isinstance(prev_carrier["mobile_country_code"], str):
                    prev_carrier["mobile_country_code"] = str(prev_carrier["mobile_country_code"])
                    
                if "mobile_network_code" in prev_carrier and prev_carrier["mobile_network_code"] is not None and not isinstance(prev_carrier["mobile_network_code"], str):
                    prev_carrier["mobile_network_code"] = str(prev_carrier["mobile_network_code"])
    
    def batch_lookup(self, 
                    numbers: List[str], 
                    output_file: Optional[str] = None,
                    rate_limit: float = 2.0) -> List[LookupResult]:
        """
        批量查询电话号码
        
        Args:
            numbers: 要查询的电话号码列表
            output_file: 输出CSV文件路径
            rate_limit: 每秒最大请求数
            
        Returns:
            List[LookupResult]: 查询结果列表
        """
        # 检查是否配置了API密钥
        if not is_configured():
            console.print("[bold red]错误：未配置API密钥。[/bold red]请先运行 'lnp config set-key' 设置API密钥。")
            raise RuntimeError("API key not configured")
        
        results = []
        unique_numbers = list(set(numbers))  # 去重
        delay = 1.0 / rate_limit  # 控制请求速率的延迟
        last_request_time = 0
        
        # 使用Rich进度条
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("正在查询...", total=len(unique_numbers))
            
            for i, number in enumerate(unique_numbers):
                # 控制API请求速率
                current_time = time.time()
                if i > 0 and current_time - last_request_time < delay:
                    time.sleep(delay - (current_time - last_request_time))
                
                # 查询号码
                result = self.lookup_number(number)
                results.append(result)
                last_request_time = time.time()
                
                # 更新进度
                progress.update(task, advance=1, description=f"正在查询 ({i+1}/{len(unique_numbers)})")
        
        # 导出结果到CSV
        if output_file:
            self.export_results_to_csv(results, output_file)
            console.print(f"[green]查询结果已保存至：[bold]{output_file}[/bold][/green]")
        
        return results
    
    def batch_lookup_from_csv(self, 
                             csv_file: str, 
                             output_file: Optional[str] = None,
                             number_column: str = "phone_number",
                             rate_limit: float = 2.0) -> List[LookupResult]:
        """
        从CSV文件批量查询电话号码
        
        Args:
            csv_file: 输入CSV文件路径
            output_file: 输出CSV文件路径
            number_column: 包含电话号码的列名
            rate_limit: 每秒最大请求数
            
        Returns:
            List[LookupResult]: 查询结果列表
        """
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file)
            
            if number_column not in df.columns:
                available_columns = ", ".join(df.columns)
                console.print(f"[bold red]错误：CSV文件中没有找到名为 '{number_column}' 的列。[/bold red]")
                console.print(f"可用的列：{available_columns}")
                raise ValueError(f"Column '{number_column}' not found in CSV file")
            
            # 提取电话号码列表
            numbers = df[number_column].astype(str).tolist()
            console.print(f"从CSV文件中读取了 [bold]{len(numbers)}[/bold] 个号码")
            
            # 设置默认输出文件
            if not output_file:
                base_name = Path(csv_file).stem
                output_file = f"{base_name}_results.csv"
            
            # 执行批量查询
            return self.batch_lookup(numbers, output_file, rate_limit)
        
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            console.print(f"[bold red]错误：无法解析CSV文件：[/bold red]{str(e)}")
            raise
        except FileNotFoundError:
            console.print(f"[bold red]错误：找不到文件：[/bold red]{csv_file}")
            raise
    
    @staticmethod
    def export_results_to_csv(results: List[LookupResult], output_file: str) -> None:
        """
        将查询结果导出到CSV文件
        
        Args:
            results: 查询结果列表
            output_file: 输出文件路径
        """
        # 准备数据
        data = []
        for result in results:
            row = {
                "phone_number": result.phone_number,
                "country_code": result.country_code,
                "carrier_name": result.carrier.name,
                "carrier_type": result.carrier.type,
                "status": result.status
            }
            
            # 添加携号转网信息
            if result.portability:
                row.update({
                    "portable": result.portability.portable,
                    "ported": result.portability.ported,
                    "spid": result.portability.spid or "",
                    "ocn": result.portability.ocn or ""
                })
                
                # 添加前一个运营商信息
                if result.portability.previous_carrier:
                    row.update({
                        "previous_carrier_name": result.portability.previous_carrier.name,
                        "previous_carrier_type": result.portability.previous_carrier.type
                    })
                else:
                    row.update({
                        "previous_carrier_name": "",
                        "previous_carrier_type": ""
                    })
            else:
                row.update({
                    "portable": False,
                    "ported": False,
                    "spid": "",
                    "ocn": "",
                    "previous_carrier_name": "",
                    "previous_carrier_type": ""
                })
            
            data.append(row)
        
        # 创建DataFrame并导出到CSV
        try:
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Results exported to {output_file}")
        except Exception as e:
            logger.error(f"Failed to export results to CSV: {e}")
            console.print(f"[bold red]错误：导出结果失败：[/bold red]{str(e)}")
            raise


def display_lookup_result(result: LookupResult) -> None:
    """
    在控制台漂亮地显示查询结果
    
    Args:
        result: 查询结果
    """
    # 创建一个表格
    table = Table(title=f"电话号码: {result.phone_number}", show_header=False, box=True)
    
    table.add_column("属性", style="cyan")
    table.add_column("值", style="white")
    
    # 添加基本信息
    table.add_row("国家", result.country_code)
    table.add_row("运营商", result.carrier.name)
    table.add_row("号码类型", result.carrier.type)
    
    # 添加携号转网信息
    if result.portability:
        table.add_row("是否可携号转网", "是" if result.portability.portable else "否")
        table.add_row("是否已携号转网", "是" if result.portability.ported else "否")
        
        if result.portability.ported and result.portability.previous_carrier:
            table.add_row("原运营商", result.portability.previous_carrier.name)
        
        if result.portability.spid:
            table.add_row("服务商ID", result.portability.spid)
        
        if result.portability.ocn:
            table.add_row("运营商代码", result.portability.ocn)
    
    # 添加查询状态信息
    if result.status != "success":
        table.add_row("查询状态", f"[bold red]{result.status}[/bold red]")
    
    console.print(table)


def display_batch_summary(results: List[LookupResult]) -> None:
    """
    显示批量查询的摘要信息
    
    Args:
        results: 查询结果列表
    """
    # 计算统计信息
    total = len(results)
    successful = sum(1 for r in results if r.status == "success")
    failed = total - successful
    
    # 计算运营商分布
    carrier_counts = {}
    for result in results:
        if result.status == "success":
            carrier_name = result.carrier.name
            carrier_counts[carrier_name] = carrier_counts.get(carrier_name, 0) + 1
    
    # 计算携号转网统计
    ported_count = sum(1 for r in results if r.status == "success" and r.portability and r.portability.ported)
    
    # 创建摘要表
    table = Table(title="批量查询摘要", show_header=True)
    
    table.add_column("统计项", style="cyan")
    table.add_column("数值", style="white")
    table.add_column("百分比", style="green")
    
    table.add_row("总号码数", str(total), "100%")
    table.add_row("成功查询", str(successful), f"{successful/total*100:.1f}%" if total > 0 else "0%")
    table.add_row("查询失败", str(failed), f"{failed/total*100:.1f}%" if total > 0 else "0%")
    table.add_row("已携号转网", str(ported_count), f"{ported_count/successful*100:.1f}%" if successful > 0 else "0%")
    
    console.print(table)
    
    # 显示运营商分布
    if carrier_counts:
        carrier_table = Table(title="运营商分布", show_header=True)
        carrier_table.add_column("运营商", style="cyan")
        carrier_table.add_column("号码数", style="white")
        carrier_table.add_column("百分比", style="green")
        
        # 按数量排序
        sorted_carriers = sorted(carrier_counts.items(), key=lambda x: x[1], reverse=True)
        
        for carrier, count in sorted_carriers:
            carrier_table.add_row(carrier, str(count), f"{count/successful*100:.1f}%" if successful > 0 else "0%")
        
        console.print(carrier_table)
