"""
查询业务逻辑模块 - 处理电话号码查询的核心逻辑
"""

import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import box

from lnptool.telnyx_api import TelnyxAPI, LookupResult, CarrierInfo, PortabilityInfo
from lnptool.cache import Cache
from lnptool.config import get_api_key, is_configured
from lnptool.i18n import t

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
            try:
                # 修改为静默模式，减少错误信息输出
                result = self.api.lookup_number(formatted_number)
                
                # 检查是否是错误结果，但不输出日志
                if result.status.startswith("error:"):
                    return result
                
                # 缓存结果（如果查询成功）
                if self.use_cache and self.cache:
                    self.cache.set(formatted_number, result.dict())
                
                return result
            except Exception as e:
                logger.error(f"Unexpected error during lookup: {e}")
                # 创建一个安全的错误结果对象
                return LookupResult(
                    phone_number=formatted_number,
                    country_code="US",
                    carrier=CarrierInfo(
                        name="Error", 
                        type="unknown", 
                        mobile_country_code=None, 
                        mobile_network_code=None
                    ),
                    portability=PortabilityInfo(
                        portable=False,
                        ported=False,
                        spid=None,
                        ocn=None,
                        previous_carrier=None
                    ),
                    status=f"error: 查询过程中出现意外错误 - {str(e)}",
                    lookup_time=time.time(),
                    request_id=None
                )
    
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
        
        # 使用Rich进度条，简化显示
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("", total=len(unique_numbers))
            
            for i, number in enumerate(unique_numbers):
                # 控制API请求速率
                current_time = time.time()
                if i > 0 and current_time - last_request_time < delay:
                    time.sleep(delay - (current_time - last_request_time))
                
                # 查询号码，使用静默模式
                try:
                    result = self.lookup_number(number)
                except Exception as e:
                    # 捕获所有异常并创建错误结果对象，但不重复输出详细错误
                    error_message = str(e)
                    
                    # 创建错误结果对象
                    result = LookupResult(
                        phone_number=number,
                        country_code="Unknown",
                        carrier=CarrierInfo(
                            name="Error",
                            type="unknown",
                            mobile_country_code=None,
                            mobile_network_code=None
                        ),
                        portability=PortabilityInfo(
                            portable=False,
                            ported=False,
                            spid=None,
                            ocn=None,
                            previous_carrier=None
                        ),
                        status=f"error: {error_message}",
                        lookup_time=time.time(),
                        request_id=None
                    )
                
                results.append(result)
                last_request_time = time.time()
                
                # 更新进度，简化描述
                progress.update(task, advance=1)
        
        # 如果指定了输出文件，保存结果
        if output_file:
            self.export_results_to_csv(results, output_file)
            console.print(f"[green]{t('results_saved_to')}：[bold]{output_file}[/bold][/green]")
            
        return results
    
    def batch_lookup_from_csv(self, csv_file, phone_column=None, output_file=None):
        """
        从CSV文件执行批量查询
        
        Args:
            csv_file: CSV文件路径
            phone_column: 电话号码列名或索引
            output_file: 输出文件路径
        """
        from rich.progress import Progress
        
        # 读取CSV文件
        try:
            # 尝试不同的编码
            encodings = ['utf-8-sig', 'utf-8', 'gbk', 'latin-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    break  # 如果成功读取，跳出循环
                except UnicodeDecodeError:
                    continue  # 如果解码错误，尝试下一个编码
            
            if df is None:
                # 所有编码都失败，使用最通用的latin-1
                df = pd.read_csv(csv_file, encoding='latin-1')
        
        except Exception as e:
            raise ValueError(f"无法读取CSV文件: {str(e)}")
        
        # 确定电话号码列
        if phone_column is None:
            # 自动检测电话号码列
            for col in df.columns:
                if 'phone' in col.lower() or 'number' in col.lower() or 'tel' in col.lower():
                    phone_column = col
                    break
            
            # 如果没有找到明确的电话号码列，使用第一列
            if phone_column is None:
                phone_column = df.columns[0]
        
        # 获取要查询的电话号码列表
        phone_numbers = df[phone_column].astype(str).tolist()
        
        # 创建带进度条的批量查询
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold green]{t('read_numbers_from_csv')}[/bold green] {len(phone_numbers)} {t('numbers')}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task(t("processing"), total=len(phone_numbers))
            
            for phone in phone_numbers:
                # 查询电话号码
                result = self.lookup_number(phone)
                results.append(result)
                
                # 更新进度
                progress.update(task, advance=1)
        
        # 将结果写入CSV文件
        if output_file:
            self.export_results_to_csv(results, output_file)
            console.print(f"[green]{t('results_saved_to')}: {output_file}[/green]")
        
        return results
    
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
    显示查询结果
    
    Args:
        result: 查询结果
    """
    # 将E.164格式号码转换为美式格式显示
    phone_e164 = result.phone_number
    
    # 确保是美国号码格式并提取数字部分
    if phone_e164.startswith("+1") and len(phone_e164) >= 12:
        digits = phone_e164[2:]  # 去掉+1前缀
        formatted_phone = f"({digits[:3]}){digits[3:6]}-{digits[6:]}"
    else:
        formatted_phone = phone_e164  # 如果不是标准格式，则保持原样
    
    # 创建表格
    title = f"{t('phone_number')} {formatted_phone}"
    table = Table(title=title, show_header=False, box=box.ROUNDED, expand=True)
    table.add_column(t("field"), style="cyan")
    table.add_column(t("value"), style="white")
    
    # 检查是否是错误结果
    if result.status.startswith("error:"):
        # 提取错误信息
        error_message = result.status[6:].strip()
        
        # 显示基本状态信息
        table.add_row(t("query_status"), "[red]" + t("failed") + "[/red]")
        
        # 提供更详细的错误原因描述
        if "403" in error_message:
            table.add_row(t("error_reason"), "[red]" + t("error_403") + "[/red]")
        elif "401" in error_message:
            table.add_row(t("error_reason"), "[red]" + t("error_401") + "[/red]")
        elif "404" in error_message:
            table.add_row(t("error_reason"), "[red]" + t("error_404") + "[/red]")
        elif "429" in error_message:
            table.add_row(t("error_reason"), "[red]" + t("error_429") + "[/red]")
        elif any(code in error_message for code in ["500", "502", "503", "504"]):
            table.add_row(t("error_reason"), "[red]" + t("error_5xx") + "[/red]")
        elif "timeout" in error_message.lower():
            table.add_row(t("error_reason"), "[red]" + t("error_timeout") + "[/red]")
        else:
            table.add_row(t("error_reason"), "[red]" + t("error_unknown") + "[/red]")
        
        console.print(table)
        return
    
    # 添加基本信息
    table.add_row(t("country"), result.country_code)
    table.add_row(t("carrier"), result.carrier.name)
    table.add_row(t("number_type"), result.carrier.type)
    
    # 添加携号转网信息
    if result.portability:
        portable_status = "[green]" + t("yes") + "[/green]" if result.portability.portable else "[red]" + t("no") + "[/red]"
        ported_status = "[green]" + t("yes") + "[/green]" if result.portability.ported else "[red]" + t("no") + "[/red]"
        
        table.add_row(t("portable"), portable_status)
        table.add_row(t("ported"), ported_status)
        
        if result.portability.spid:
            table.add_row(t("service_provider_id"), result.portability.spid)
        
        if result.portability.ocn:
            table.add_row(t("carrier_code"), result.portability.ocn)
        
        # 显示前一个运营商信息
        if result.portability.previous_carrier:
            table.add_row(t("previous_carrier"), result.portability.previous_carrier.name)
            table.add_row(t("previous_number_type"), result.portability.previous_carrier.type)
    else:
        table.add_row(t("portable"), "[red]" + t("unknown") + "[/red]")
        table.add_row(t("ported"), "[red]" + t("unknown") + "[/red]")
    
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
    
    # 计算携号转网比例
    ported = sum(1 for r in results if r.status == "success" and r.portability and r.portability.ported)
    
    # 统计不同运营商数量
    carrier_count = {}
    for result in results:
        if result.status == "success":
            carrier_name = result.carrier.name
            carrier_count[carrier_name] = carrier_count.get(carrier_name, 0) + 1
    
    # 统计错误类型
    error_types = {}
    for result in results:
        if result.status.startswith("error:"):
            error_msg = result.status[6:].strip()
            
            # 分类错误类型
            if "403" in error_msg:
                error_type = t("error_403_short")
            elif "401" in error_msg:
                error_type = t("error_401_short")
            elif "404" in error_msg:
                error_type = t("error_404_short")
            elif "429" in error_msg:
                error_type = t("error_429_short")
            elif any(code in error_msg for code in ["500", "502", "503", "504"]):
                error_type = t("error_5xx_short")
            elif "timeout" in error_msg.lower():
                error_type = t("error_timeout_short")
            else:
                error_type = t("error_unknown_short")
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    # 创建总体摘要表格
    summary_table = Table(title=t("batch_result_summary"), show_header=True, box=box.ROUNDED)
    summary_table.add_column(t("summary_item"), style="cyan")
    summary_table.add_column(t("count"), style="white")
    summary_table.add_column(t("percentage"), style="green")
    
    # 添加摘要行
    summary_table.add_row(t("total_numbers"), str(total), "100%")
    summary_table.add_row(
        t("successful_queries"), 
        str(successful), 
        f"{successful/total*100:.1f}%" if total > 0 else "0%"
    )
    summary_table.add_row(
        t("failed_queries"), 
        str(failed), 
        f"{failed/total*100:.1f}%" if total > 0 else "0%"
    )
    
    if successful > 0:
        summary_table.add_row(
            t("ported_numbers"), 
            str(ported), 
            f"{ported/successful*100:.1f}%"
        )
    
    console.print(summary_table)
    
    # 显示运营商分布
    if carrier_count:
        carrier_table = Table(title=t("carrier_distribution"), show_header=True, box=box.ROUNDED)
        carrier_table.add_column(t("carrier"), style="cyan")
        carrier_table.add_column(t("count"), style="white")
        carrier_table.add_column(t("percentage"), style="green")
        
        # 按数量排序
        sorted_carriers = sorted(carrier_count.items(), key=lambda x: x[1], reverse=True)
        
        for carrier, count in sorted_carriers:
            carrier_table.add_row(carrier, str(count), f"{count/successful*100:.1f}%" if successful > 0 else "0%")
        
        console.print(carrier_table)
    
    # 显示错误类型统计
    if error_types:
        error_table = Table(title=t("error_type_stats"), show_header=True, box=box.ROUNDED)
        error_table.add_column(t("error_type"), style="cyan")
        error_table.add_column(t("count"), style="white")
        error_table.add_column(t("percentage"), style="red")
        
        # 按数量排序
        sorted_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        
        for error_type, count in sorted_errors:
            error_table.add_row(error_type, str(count), f"{count/failed*100:.1f}%" if failed > 0 else "0%")
        
        console.print(error_table)
