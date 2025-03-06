#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
时间戳更新工具
用于更新项目文档中的时间戳信息
"""

import os
import re
import time
import glob
import argparse
from datetime import datetime
import pytz

# 时间戳格式
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMESTAMP_PATTERN = r"\[Timestamp: (\d+)\]"

def update_timestamp(file_path):
    """更新文件中的时间戳"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 获取当前时间戳
        now = int(time.time())
        
        # 获取太平洋时间
        pst = pytz.timezone('America/Los_Angeles')
        pst_time = datetime.fromtimestamp(now, pst)
        pst_str = pst_time.strftime(TIMESTAMP_FORMAT)
        
        # 查找并替换中文时间戳（最后更新时间）
        if "最后更新时间" in content:
            content = re.sub(
                r"最后更新时间（\w+）: .*?\[Timestamp: \d+\]", 
                f"最后更新时间（PST）: {pst_str} [Timestamp: {now}]", 
                content
            )
        
        # 查找并替换中文时间戳（最后更新）
        if "最后更新" in content and "最后更新时间" not in content:
            content = re.sub(
                r"最后更新\S*: .*?\(Pacific Time\)", 
                f"最后更新**: {pst_str} (Pacific Time)", 
                content
            )
            
            # 更新时间戳
            content = re.sub(
                r"时间戳\S*: \d+", 
                f"时间戳**: {now}", 
                content
            )
        
        # 查找并替换英文时间戳
        if "Last Updated" in content:
            content = re.sub(
                r"Last Updated\S*: .*?\(Pacific Time\)", 
                f"Last Updated**: {pst_str} (Pacific Time)", 
                content
            )
            
            # 更新时间戳
            content = re.sub(
                r"Timestamp\S*: \d+", 
                f"Timestamp**: {now}", 
                content
            )
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新: {file_path}")
        return True
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {str(e)}")
        return False

def process_directory(directory, pattern="*.md"):
    """处理目录中的所有匹配文件"""
    success_count = 0
    fail_count = 0
    
    # 获取所有匹配的文件
    files = glob.glob(os.path.join(directory, pattern))
    
    if not files:
        print(f"⚠️ 在 {directory} 中未找到匹配 {pattern} 的文件")
        return 0, 0
    
    for file_path in files:
        if update_timestamp(file_path):
            success_count += 1
        else:
            fail_count += 1
    
    return success_count, fail_count

def main():
    parser = argparse.ArgumentParser(description="更新文档时间戳工具")
    parser.add_argument("--dir", "-d", help="要处理的目录", default=".")
    parser.add_argument("--pattern", "-p", help="文件匹配模式", default="*.md")
    parser.add_argument("--recursive", "-r", action="store_true", help="是否递归处理子目录")
    
    args = parser.parse_args()
    
    total_success = 0
    total_fail = 0
    
    if args.recursive:
        for root, _, _ in os.walk(args.dir):
            success, fail = process_directory(root, args.pattern)
            total_success += success
            total_fail += fail
    else:
        total_success, total_fail = process_directory(args.dir, args.pattern)
    
    print(f"\n📊 统计信息:")
    print(f"  ✅ 成功更新: {total_success} 个文件")
    print(f"  ❌ 更新失败: {total_fail} 个文件")
    print(f"  🔄 总处理数: {total_success + total_fail} 个文件")

if __name__ == "__main__":
    main() 