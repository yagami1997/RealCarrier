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
    title = f"电话号码 {formatted_phone} 查询结果"
    table = Table(title=title, show_header=False, box=box.ROUNDED, expand=True)
    table.add_column("字段", style="cyan")
    table.add_column("值", style="white")
    
    # 检查是否是错误结果
    if result.status.startswith("error:"):
        # 提取错误信息
        error_message = result.status[6:].strip()
        
        # 显示基本状态信息
        table.add_row("查询状态", "[red]失败[/red]")
        
        # 提供更详细的错误原因描述
        if "403" in error_message:
            table.add_row("错误原因", "[red]403错误，请检查Telnyx API账户状态，是否完成KYC认证或者余额足够[/red]")
        elif "401" in error_message:
            table.add_row("错误原因", "[red]401错误，API密钥无效或已过期，请重新设置密钥[/red]")
        elif "404" in error_message:
            table.add_row("错误原因", "[red]404错误，请检查号码格式是否正确，或该号码不存在于Telnyx数据库[/red]")
        elif "429" in error_message:
            table.add_row("错误原因", "[red]429错误，请求频率过高，请降低请求速率或稍后再试[/red]")
        elif any(code in error_message for code in ["500", "502", "503", "504"]):
            table.add_row("错误原因", "[red]服务器错误(5xx)，Telnyx服务暂时不可用，请稍后再试[/red]")
        elif "timeout" in error_message.lower():
            table.add_row("错误原因", "[red]请求超时，请检查网络连接或稍后再试[/red]")
        else:
            table.add_row("错误原因", "[red]未知API错误，请联系技术支持[/red]")
        
        console.print(table)
        return
    
    # 添加基本信息
    table.add_row("国家", result.country_code)
    table.add_row("运营商", result.carrier.name)
    table.add_row("号码类型", result.carrier.type)
    
    # 添加携号转网信息
    if result.portability:
        portable_status = "[green]是[/green]" if result.portability.portable else "[red]否[/red]"
        ported_status = "[green]是[/green]" if result.portability.ported else "[red]否[/red]"
        
        table.add_row("可携号转网", portable_status)
        table.add_row("已携号转网", ported_status)
        
        if result.portability.spid:
            table.add_row("服务商ID", result.portability.spid)
        
        if result.portability.ocn:
            table.add_row("运营商代码", result.portability.ocn)
        
        # 显示前一个运营商信息
        if result.portability.previous_carrier:
            table.add_row("前运营商", result.portability.previous_carrier.name)
            table.add_row("前号码类型", result.portability.previous_carrier.type)
    else:
        table.add_row("可携号转网", "[red]未知[/red]")
        table.add_row("已携号转网", "[red]未知[/red]")
    
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
    
    # 统计错误类型
    error_types = {}
    for result in results:
        if result.status.startswith("error:"):
            error_message = result.status[6:].strip()
            # 提取错误类型
            error_type = "其他错误"
            
            if "403" in error_message:
                error_type = "账户权限问题 (403)"
            elif "401" in error_message:
                error_type = "API密钥无效 (401)"
            elif "404" in error_message:
                error_type = "号码不存在 (404)"
            elif "429" in error_message:
                error_type = "请求频率限制 (429)"
            elif any(code in error_message for code in ["500", "502", "503", "504"]):
                error_type = "服务器错误 (5xx)"
            elif "timeout" in error_message.lower():
                error_type = "请求超时"
                
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    # 创建摘要表
    table = Table(title="批量查询摘要", show_header=True, box=box.ROUNDED)
    
    table.add_column("统计项", style="cyan")
    table.add_column("数值", style="white")
    table.add_column("百分比", style="green")
    
    table.add_row("总号码数", str(total), "100%")
    table.add_row("成功查询", str(successful), f"{successful/total*100:.1f}%" if total > 0 else "0%")
    table.add_row("查询失败", str(failed), f"{failed/total*100:.1f}%" if total > 0 else "0%")
    
    if successful > 0:
        table.add_row("已携号转网", str(ported_count), f"{ported_count/successful*100:.1f}%")
    
    console.print(table)
    
    # 显示运营商分布
    if carrier_counts:
        carrier_table = Table(title="运营商分布", show_header=True, box=box.ROUNDED)
        carrier_table.add_column("运营商", style="cyan")
        carrier_table.add_column("号码数", style="white")
        carrier_table.add_column("百分比", style="green")
        
        # 按数量排序
        sorted_carriers = sorted(carrier_counts.items(), key=lambda x: x[1], reverse=True)
        
        for carrier, count in sorted_carriers:
            carrier_table.add_row(carrier, str(count), f"{count/successful*100:.1f}%" if successful > 0 else "0%")
        
        console.print(carrier_table)
    
    # 显示错误类型统计
    if error_types:
        error_table = Table(title="错误类型统计", show_header=True, box=box.ROUNDED)
        error_table.add_column("错误类型", style="cyan")
        error_table.add_column("次数", style="white")
        error_table.add_column("百分比", style="red")
        
        # 按数量排序
        sorted_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        
        for error_type, count in sorted_errors:
            error_table.add_row(error_type, str(count), f"{count/failed*100:.1f}%" if failed > 0 else "0%")
        
        console.print(error_table)
