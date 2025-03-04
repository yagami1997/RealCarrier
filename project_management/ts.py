#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RealCarrier项目文档时间戳更新工具
用于将项目管理文档中的时间戳更新为统一的太平洋时间格式

使用方法:
1. 直接运行此脚本: python ts.py
2. 指定目录更新: python ts.py --dir project_management/templates
3. 更新项目根目录README: python ts.py --root
"""

import os
import re
import sys
import argparse
from datetime import datetime
import pytz
import time

def get_pacific_time():
    """获取太平洋时间，格式：YYYY-MM-DD HH:MM:SS"""
    pacific_tz = pytz.timezone('America/Los_Angeles')
    pacific_time = datetime.now(pacific_tz)
    return pacific_time.strftime('%Y-%m-%d %H:%M:%S')

def get_pacific_timestamp():
    """获取太平洋时间戳（秒）"""
    pacific_tz = pytz.timezone('America/Los_Angeles')
    pacific_time = datetime.now(pacific_tz)
    return int(pacific_time.timestamp())

def update_timestamp_in_file(file_path):
    """更新文件中的时间戳"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 获取当前太平洋时间
    pacific_time = get_pacific_time()
    timestamp = int(time.time())
    
    # 定义时间戳正则表达式模式
    patterns = [
        # 标准格式: 2023-01-01 12:00:00 (Pacific Time)
        (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \(Pacific Time\)', f'{pacific_time} (Pacific Time)'),
        
        # 简化格式: 2023-01-01 12:00:00 PST
        (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} PST', f'{pacific_time} PST'),
        
        # 时间戳格式: timestamp: 1234567890
        (r'timestamp: \d+', f'timestamp: {timestamp}'),
        
        # README.md 特定格式
        (r'- \*\*最后更新日期\*\*: .*', f'- **最后更新日期**: {pacific_time} (Pacific Time)'),
        (r'- \*\*时间戳\*\*: \d+', f'- **时间戳**: {timestamp}'),
        
        # pyproject.toml 特定格式
        (r'# 最后更新时间（PST）: .*', f'# 最后更新时间（PST）: {pacific_time}'),
    ]
    
    # 应用所有模式
    updated_content = content
    updates_made = 0
    
    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, updated_content)
        if count > 0:
            updated_content = new_content
            updates_made += count
    
    # 如果有更新，写回文件
    if updates_made > 0:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print(f"已更新 {file_path} 中的 {updates_made} 处时间戳")
        return True
    else:
        print(f"文件无需更新: {file_path}")
        return False

def update_timestamps_in_directory(directory_path):
    """更新指定目录及其子目录中所有Markdown文件的时间戳"""
    if not os.path.exists(directory_path):
        print(f"目录不存在: {directory_path}")
        return
    
    updated_count = 0
    total_count = 0
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(('.md', '.txt')):
                total_count += 1
                file_path = os.path.join(root, file)
                if update_timestamp_in_file(file_path):
                    updated_count += 1
    
    print(f"统计: 总共{total_count}个文件，更新了{updated_count}个文件")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='更新项目管理文档中的时间戳')
    parser.add_argument('--dir', type=str, help='指定要更新的目录')
    parser.add_argument('--root', action='store_true', help='更新项目根目录的README.md文件')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    
    if args.root:
        # 更新项目根目录的README.md文件
        root_readme = 'README.md'
        if os.path.exists(root_readme):
            print(f"更新项目根目录README.md文件...")
            if update_timestamp_in_file(root_readme):
                print("项目README.md文件已更新")
            else:
                print("项目README.md文件无需更新")
        else:
            print(f"项目根目录README.md文件不存在")
    elif args.dir:
        print(f"开始更新指定目录: {args.dir}")
        update_timestamps_in_directory(args.dir)
    else:
        # 默认更新项目管理目录
        project_management_dir = 'project_management'
        
        if not os.path.exists(project_management_dir):
            print(f"项目管理目录不存在: {project_management_dir}")
            sys.exit(1)
        
        print(f"开始更新项目管理文档时间戳...")
        update_timestamps_in_directory(project_management_dir)
    
    print("\n时间戳更新完成！")
    print(f"当前太平洋时间: {get_pacific_time()}")
    print(f"当前时间戳: {get_pacific_timestamp()}") 