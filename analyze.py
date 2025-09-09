#!/usr/bin/env python3
"""
简单的代码分析脚本
用法: python analyze.py [文件路径或目录]
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fuck_u_code.analyzers.code_analyzer import CodeAnalyzer
from fuck_u_code.reports.simple_reporter import SimpleReporter

def main():
    # 获取要分析的路径
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = "."  # 默认分析当前目录
    
    print(f"🔍 分析路径: {target_path}")
    print("=" * 50)
    
    try:
        # 创建分析器
        analyzer = CodeAnalyzer()
        
        # 执行分析
        result = analyzer.analyze(target_path)
        
        # 生成报告
        reporter = SimpleReporter()
        report = reporter.generate(result)
        
        print(report)
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())