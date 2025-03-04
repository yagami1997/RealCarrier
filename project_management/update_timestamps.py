#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RealCarrier项目文档时间戳更新工具
用于将项目管理文档中的时间戳更新为统一的太平洋时间格式

使用方法:
1. 直接运行此脚本: python update_timestamps.py
2. 指定目录更新: python update_timestamps.py --dir project_management/templates
"""

import os
import re
import sys
import argparse
from datetime import datetime
import pytz

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
    """更新指定文件中的时间戳"""
    # 获取当前时间和时间戳
    current_time = get_pacific_time()
    current_timestamp = get_pacific_timestamp()
    timestamp_format = f"{current_time} [Timestamp: {current_timestamp}]"
    
    # 如果文件不存在，则跳过
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 更新各种时间戳格式
        updated_content = content
        patterns = [
            # 项目管理文档中的时间格式
            r'- \*\*最后更新\*\*: .*',
            r'- \*\*最后修改\*\*: .*',
            r'- \*\*更新时间\*\*: .*',
            r'- \*\*创建时间\*\*: .*',
            r'- \*\*创建日期\*\*: .*',
            r'- 最后更新时间（.*）: .*',
            r'- 报告生成时间（.*）: .*',
            
            # 其他可能的时间格式
            r'# 最后更新时间（.*）: .*',
            r'\*报告日期：.*\*',
            r'- \*\*日期\*\*: \d{4}(-\d{2}){2}',
            r'- \*\*时间段\*\*: .* 至 .*'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                # 特殊处理日期范围格式
                if '时间段' in pattern and match:
                    # 时间段保持原始开始日期不变，只更新结束日期
                    date_range = match.group(0)
                    parts = date_range.split('至')
                    if len(parts) == 2:
                        start_date = parts[0].strip()
                        today = current_time.split(' ')[0]
                        updated_content = updated_content.replace(
                            date_range,
                            f"{start_date} 至 {today}"
                        )
                    continue
                
                # 获取匹配项前缀
                prefix = re.sub(r': .*', ': ', match.group(0))
                
                # 替换时间戳
                updated_content = re.sub(
                    pattern,
                    f"{prefix}{timestamp_format}",
                    updated_content
                )
        
        # 如果内容有变化，写回文件
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            print(f"已更新文件: {file_path}")
            return True
        else:
            print(f"无需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"更新文件失败: {file_path}, 错误: {str(e)}")
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
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    
    if args.dir:
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