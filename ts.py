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

# 严格的时间戳匹配模式 - 报告格式
REPORT_TIMESTAMP_SECTION = r"## 时间信息\n- 报告生成时间（PST）: .*?\[Timestamp: \d+\]\n- 最后更新时间（PST）: .*?\[Timestamp: \d+\]"
REPORT_GENERATION_TIME = r"报告生成时间（PST）: (.*?)\[Timestamp: (\d+)\]"
REPORT_UPDATE_TIME = r"最后更新时间（PST）: .*?\[Timestamp: \d+\]"

# README格式的时间戳匹配模式
README_TIMESTAMP_SECTION = r"## 📅 (?:Document Information|文档信息)\n- \*\*(?:Last Updated|最后更新)\*\*: .*? \(Pacific Time\)\n- \*\*(?:Timestamp|时间戳)\*\*: \d+"
README_UPDATE_TIME = r"\*\*(?:Last Updated|最后更新)\*\*: (.*?) \(Pacific Time\)"
README_TIMESTAMP = r"\*\*(?:Timestamp|时间戳)\*\*: (\d+)"

def get_pst_time():
    """获取当前的PST时间"""
    now = int(time.time())
    pst = pytz.timezone('America/Los_Angeles')
    pst_time = datetime.fromtimestamp(now, pst)
    return now, pst_time.strftime(TIMESTAMP_FORMAT)

def validate_file_format(content):
    """验证文件格式是否正确"""
    # 检查是否为README文件
    if "RealCarrier" in content and "Beta v1.0.0" in content:
        if not re.search(r"## 📅 (?:Document Information|文档信息)", content):
            return False, "缺少文档信息部分"
        return True, "README"
    
    # 检查是否为报告文件
    if not ("# 日报" in content or "# 周报" in content):
        return False, "缺少报告标题"
    
    if "---" not in content:
        return False, "缺少分隔线"
    
    if "报告人：" not in content or "报告日期：" not in content:
        return False, "缺少报告人或报告日期信息"
    
    # 检查时间戳部分是否在文件末尾
    if not re.search(REPORT_TIMESTAMP_SECTION + r"\s*$", content):
        return False, "时间戳部分不在文件末尾或格式不正确"
    
    return True, "REPORT"

def update_readme_timestamp(content, is_chinese=False):
    """更新README文件的时间戳"""
    now, pst_str = get_pst_time()
    
    if is_chinese:
        new_timestamp_section = (
            "## 📅 文档信息\n"
            f"- **最后更新**: {pst_str} (Pacific Time)\n"
            f"- **时间戳**: {now}"
        )
    else:
        new_timestamp_section = (
            "## 📅 Document Information\n"
            f"- **Last Updated**: {pst_str} (Pacific Time)\n"
            f"- **Timestamp**: {now}"
        )
    
    return re.sub(README_TIMESTAMP_SECTION + r"\s*$", new_timestamp_section, content)

def update_report_timestamp(content):
    """更新报告文件的时间戳"""
    now, pst_str = get_pst_time()
    
    # 保留原始的报告生成时间
    gen_time_match = re.search(REPORT_GENERATION_TIME, content)
    if not gen_time_match:
        raise Exception("无法找到报告生成时间")
    
    gen_time, gen_timestamp = gen_time_match.groups()
    
    new_timestamp_section = (
        "## 时间信息\n"
        f"- 报告生成时间（PST）: {gen_time}[Timestamp: {gen_timestamp}]\n"
        f"- 最后更新时间（PST）: {pst_str} [Timestamp: {now}]"
    )
    
    return re.sub(REPORT_TIMESTAMP_SECTION + r"\s*$", new_timestamp_section, content)

def update_timestamp(file_path):
    """更新文件中的时间戳"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证文件格式
        is_valid, file_type = validate_file_format(content)
        if not is_valid:
            print(f"❌ 文件格式错误 {file_path}: {file_type}")
            return False
        
        # 根据文件类型选择更新方式
        if file_type == "README":
            is_chinese = "README.zh.md" in file_path
            content = update_readme_timestamp(content, is_chinese)
        else:
            content = update_report_timestamp(content)
        
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