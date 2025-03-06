#!/usr/bin/env python
"""
翻译检查脚本
用于检查翻译的完整性和一致性
"""

from i18n import print_translation_issues, get_translation_stats

if __name__ == "__main__":
    print("=== 翻译统计 ===")
    stats = get_translation_stats()
    for lang, count in stats.items():
        print(f"{lang}: {count} 个翻译")
    print()
    
    print_translation_issues() 