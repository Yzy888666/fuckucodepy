#!/usr/bin/env python3
"""
简单的功能验证脚本

测试fuck-u-code的基本功能是否正常工作。
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fuck_u_code.analyzers.code_analyzer import CodeAnalyzer
from fuck_u_code.reports.terminal_reporter import TerminalReporter
from fuck_u_code.reports.markdown_reporter import MarkdownReporter


def test_basic_functionality():
    """测试基本功能"""
    print("🚀 开始测试fuck-u-code基本功能...")
    
    # 测试文件路径
    bad_code_file = "tests/fixtures/sample_bad_code.py"
    good_code_file = "tests/fixtures/sample_good_code.py"
    
    analyzer = CodeAnalyzer()
    
    # 测试坏代码分析
    print(f"\n📄 分析坏代码文件: {bad_code_file}")
    if os.path.exists(bad_code_file):
        result_bad = analyzer.analyze_file(bad_code_file)
        print(f"✅ 分析完成！质量评分: {result_bad.overall_score:.1f}分")
        print(f"   发现问题: {result_bad.total_issues}个")
        print(f"   严重问题: {result_bad.critical_issues}个")
    else:
        print(f"❌ 文件不存在: {bad_code_file}")
    
    # 测试好代码分析
    print(f"\n📄 分析好代码文件: {good_code_file}")
    if os.path.exists(good_code_file):
        result_good = analyzer.analyze_file(good_code_file)
        print(f"✅ 分析完成！质量评分: {result_good.overall_score:.1f}分")
        print(f"   发现问题: {result_good.total_issues}个")
        print(f"   严重问题: {result_good.critical_issues}个")
    else:
        print(f"❌ 文件不存在: {good_code_file}")
    
    # 测试终端报告
    print(f"\n📊 生成终端报告...")
    if os.path.exists(bad_code_file):
        terminal_reporter = TerminalReporter()
        terminal_report = terminal_reporter.generate(result_bad, summary=True)
        print("✅ 终端报告生成成功")
        # print(terminal_report[:200] + "..." if len(terminal_report) > 200 else terminal_report)
    
    # 测试Markdown报告
    print(f"\n📝 生成Markdown报告...")
    if os.path.exists(bad_code_file):
        markdown_reporter = MarkdownReporter()
        markdown_report = markdown_reporter.generate(result_bad)
        print("✅ Markdown报告生成成功")
        print(f"   报告长度: {len(markdown_report)}字符")
    
    print(f"\n🎉 所有测试完成！")


def test_directory_analysis():
    """测试目录分析"""
    print(f"\n🔍 测试目录分析功能...")
    
    analyzer = CodeAnalyzer()
    
    # 分析当前目录的src
    src_dir = "src"
    if os.path.exists(src_dir):
        print(f"   分析目录: {src_dir}")
        result = analyzer.analyze(src_dir)
        print(f"✅ 目录分析完成！")
        print(f"   分析文件: {result.total_files}个")
        print(f"   总体评分: {result.overall_score:.1f}分")
        print(f"   总问题数: {result.total_issues}个")
    else:
        print(f"❌ 目录不存在: {src_dir}")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_directory_analysis()
        
        print(f"\n✨ 项目验证完成！fuck-u-code Python版本运行正常。")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)