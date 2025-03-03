"""
命令行入口模块 - 处理命令行参数和交互
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from lnptool.config import get_config, set_api_key, delete_api_key, update_config_setting, is_configured
from lnptool.cache import Cache
from lnptool.lookup import LookupService, display_lookup_result, display_batch_summary
from lnptool.utils import (
    configure_logging, validate_phone_number, validate_csv_file, 
    format_timestamp, print_error, print_warning, print_success, 
    print_info, safe_input, is_valid_api_key
)

console = Console()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='启用详细日志记录')
def cli(verbose: bool) -> None:
    """
    Telnyx LNP查询工具 - 查询美国电话号码的运营商信息和携号转网状态
    """
    # 配置日志记录
    configure_logging(verbose)


@cli.group()
def config() -> None:
    """配置管理命令"""
    pass


@config.command('set-key')
def config_set_key() -> None:
    """配置Telnyx API密钥"""
    # 提示用户输入API密钥
    api_key = safe_input("请输入Telnyx API密钥 (例如: KEY_1234...): ", password=True)
    
    # 验证API密钥格式
    if not is_valid_api_key(api_key):
        print_warning("API密钥格式可能不正确，通常以KEY_开头。是否仍要保存？(y/n)")
        confirm = safe_input("", password=False).lower()
        if confirm != 'y':
            print_info("操作已取消。")
            return
    
    # 保存API密钥
    if set_api_key(api_key):
        print_success("API密钥已成功配置。")
    else:
        print_error("保存API密钥时出错。")


@config.command('delete-key')
def config_delete_key() -> None:
    """删除已保存的API密钥"""
    if not is_configured():
        print_warning("未找到已保存的API密钥。")
        return
    
    # 确认删除
    print_warning("即将删除已保存的API密钥。此操作不可撤销。")
    confirm = safe_input("确认删除? (y/n): ", password=False).lower()
    
    if confirm == 'y':
        if delete_api_key():
            print_success("API密钥已删除。")
        else:
            print_error("删除API密钥时出错。")
    else:
        print_info("操作已取消。")


@config.command('show')
def config_show() -> None:
    """显示当前配置"""
    config_data = get_config()
    
    table = click.rich.table.Table(title="当前配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")
    
    for key, value in config_data.items():
        table.add_row(key, str(value))
    
    # 添加API密钥状态
    if is_configured():
        table.add_row("api_key", "已配置")
    else:
        table.add_row("api_key", "未配置")
    
    console.print(table)


@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key: str, value: str) -> None:
    """设置配置项值"""
    if key not in ['api_cache_ttl', 'rate_limit']:
        print_error(f"未知配置项: {key}")
        print_info("可用的配置项: api_cache_ttl, rate_limit")
        return
    
    # 尝试转换值类型
    try:
        if key == 'api_cache_ttl':
            value_converted = int(value)
        elif key == 'rate_limit':
            value_converted = float(value)
    except ValueError:
        print_error(f"无效的值: {value}")
        return
    
    # 更新配置
    if update_config_setting(key, value_converted):
        print_success(f"已更新配置项 {key} = {value}")
    else:
        print_error(f"更新配置失败")


@cli.command('lookup')
@click.argument('phone_number', callback=validate_phone_number)
@click.option('--no-cache', is_flag=True, help='禁用缓存')
def lookup(phone_number: str, no_cache: bool) -> None:
    """查询单个电话号码的信息"""
    try:
        service = LookupService(use_cache=not no_cache)
        result = service.lookup_number(phone_number)
        display_lookup_result(result)
    except Exception as e:
        print_error(f"查询失败: {str(e)}")
        logging.exception("查询出错", exc_info=e)
        sys.exit(1)


@cli.command('batch')
@click.argument('csv_file', callback=validate_csv_file)
@click.option('--output', '-o', type=str, help='输出CSV文件路径')
@click.option('--column', '-c', type=str, default='phone_number', help='包含电话号码的列名')
@click.option('--rate-limit', type=float, help='每秒API请求数限制')
@click.option('--no-cache', is_flag=True, help='禁用缓存')
def batch(csv_file: str, output: Optional[str], column: str, rate_limit: Optional[float], no_cache: bool) -> None:
    """批量查询CSV文件中的电话号码"""
    try:
        # 获取配置的速率限制
        if rate_limit is None:
            config = get_config()
            rate_limit = config.get('rate_limit', 2.0)
        
        service = LookupService(use_cache=not no_cache)
        results = service.batch_lookup_from_csv(
            csv_file=csv_file,
            output_file=output,
            number_column=column,
            rate_limit=rate_limit
        )
        
        # 显示批量查询摘要
        display_batch_summary(results)
        
    except Exception as e:
        print_error(f"批量查询失败: {str(e)}")
        logging.exception("批量查询出错", exc_info=e)
        sys.exit(1)


@cli.group()
def cache() -> None:
    """缓存管理命令"""
    pass


@cache.command('clear')
def cache_clear() -> None:
    """清除所有缓存"""
    try:
        cache = Cache()
        if cache.clear():
            print_success("缓存已清除。")
        else:
            print_error("清除缓存失败。")
    except Exception as e:
        print_error(f"操作失败: {str(e)}")
        logging.exception("清除缓存出错", exc_info=e)


@cache.command('clear-expired')
def cache_clear_expired() -> None:
    """清除过期缓存"""
    try:
        cache = Cache()
        count = cache.clear_expired()
        print_success(f"已清除 {count} 个过期缓存条目。")
    except Exception as e:
        print_error(f"操作失败: {str(e)}")
        logging.exception("清除过期缓存出错", exc_info=e)


@cache.command('info')
def cache_info() -> None:
    """显示缓存统计信息"""
    try:
        cache = Cache()
        stats = cache.get_stats()
        
        table = click.rich.table.Table(title="缓存统计")
        table.add_column("项目", style="cyan")
        table.add_column("值", style="green")
        
        table.add_row("总条目数", str(stats.get("total_entries", 0)))
        table.add_row("有效条目数", str(stats.get("valid_entries", 0)))
        table.add_row("过期条目数", str(stats.get("expired_entries", 0)))
        
        if stats.get("oldest_entry_time"):
            table.add_row("最早缓存时间", format_timestamp(stats.get("oldest_entry_time")))
            
        if stats.get("newest_entry_time"):
            table.add_row("最新缓存时间", format_timestamp(stats.get("newest_entry_time")))
        
        size_kb = stats.get("cache_size_bytes", 0) / 1024
        table.add_row("缓存大小", f"{size_kb:.2f} KB")
        
        ttl_hours = stats.get("cache_ttl_seconds", 0) / 3600
        table.add_row("缓存有效期", f"{ttl_hours:.1f} 小时")
        
        console.print(table)
        
    except Exception as e:
        print_error(f"操作失败: {str(e)}")
        logging.exception("获取缓存信息出错", exc_info=e)


@cache.command('recent')
@click.option('--limit', '-n', type=int, default=10, help='显示的记录数')
def cache_recent(limit: int) -> None:
    """显示最近的查询"""
    try:
        cache = Cache()
        recent = cache.get_recent_lookups(limit)
        
        if not recent:
            print_info("没有找到最近的查询记录。")
            return
        
        table = click.rich.table.Table(title="最近查询")
        table.add_column("电话号码", style="cyan")
        table.add_column("查询时间", style="green")
        
        for number, timestamp in recent:
            table.add_row(number, format_timestamp(timestamp))
        
        console.print(table)
        
    except Exception as e:
        print_error(f"操作失败: {str(e)}")
        logging.exception("获取最近查询记录出错", exc_info=e)


if __name__ == '__main__':
    cli()
