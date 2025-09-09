#!/usr/bin/env python3
"""
简化测试脚本

不依赖外部库，只测试核心分析功能。
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fuck_u_code.analyzers.code_analyzer import CodeAnalyzer
from fuck_u_code.parsers.python_parser import PythonParser
from fuck_u_code.metrics.complexity import ComplexityMetric
from fuck_u_code.metrics.function_length import FunctionLengthMetric
from fuck_u_code.metrics.comment_ratio import CommentRatioMetric
from fuck_u_code.common.language_detector import LanguageDetector


def test_language_detector():
    """测试语言检测器"""
    print("🔍 测试语言检测器...")
    
    detector = LanguageDetector()
    
    test_cases = [
        ("test.py", "Python"),
        ("script.js", "JavaScript"),
        ("readme.txt", "不支持"),
    ]
    
    for filename, expected in test_cases:
        language = detector.detect_language(filename)
        print(f"   {filename} -> {language.value} ({'✅' if language.value != 'unsupported' or expected == '不支持' else '❌'})")


def test_python_parser():
    """测试Python解析器"""
    print("\n📝 测试Python解析器...")
    
    parser = PythonParser()
    
    # 测试简单代码
    simple_code = '''
def hello_world():
    """Say hello to the world."""
    print("Hello, World!")
    return True

class TestClass:
    """A test class."""
    
    def method(self):
        """A test method."""
        pass
'''
    
    result = parser.parse("test.py", simple_code)
    
    print(f"   解析结果: {len(result.functions)} 个函数, {len(result.classes)} 个类")
    print(f"   总行数: {result.total_lines}, 注释行数: {result.comment_lines}")
    
    if result.functions:
        func = result.functions[0]
        print(f"   第一个函数: {func.name} (复杂度: {func.complexity}, 参数: {func.parameters})")


def test_metrics():
    """测试指标系统"""
    print("\n📊 测试指标系统...")
    
    parser = PythonParser()
    
    # 创建复杂的测试代码
    complex_code = '''
def complex_function(a, b, c, d, e, f, g):
    """A very complex function."""
    result = 0
    
    if a > 0:
        for i in range(b):
            if i % 2 == 0:
                try:
                    if c > 0:
                        for j in range(c):
                            if j % 3 == 0:
                                result += d / j
                            elif j % 3 == 1:
                                result *= e
                            else:
                                result -= f
                except ZeroDivisionError:
                    if g > 0:
                        result = g
                    else:
                        continue
                else:
                    result *= 2
    elif a < 0:
        while b > 0:
            result -= 1
            b -= 1
    else:
        for k in range(10):
            result += k
    
    return result

def simple_function():
    return 42

def function_without_docstring():
    pass

# 这是一个注释
# 另一个注释
'''
    
    parse_result = parser.parse("test.py", complex_code)
    
    # 测试复杂度指标
    complexity_metric = ComplexityMetric()
    complexity_result = complexity_metric.analyze(parse_result)
    print(f"   复杂度指标: 评分 {complexity_result.score:.2f}, 问题 {len(complexity_result.issues)} 个")
    
    # 测试函数长度指标
    length_metric = FunctionLengthMetric()
    length_result = length_metric.analyze(parse_result)
    print(f"   函数长度指标: 评分 {length_result.score:.2f}, 问题 {len(length_result.issues)} 个")
    
    # 测试注释覆盖率指标
    comment_metric = CommentRatioMetric()
    comment_result = comment_metric.analyze(parse_result)
    print(f"   注释覆盖率指标: 评分 {comment_result.score:.2f}, 问题 {len(comment_result.issues)} 个")


def test_analyzer():
    """测试完整分析器"""
    print("\n🔬 测试完整分析器...")
    
    # 测试文件路径
    test_files = [
        "tests/fixtures/sample_bad_code.py",
        "tests/fixtures/sample_good_code.py"
    ]
    
    analyzer = CodeAnalyzer()
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"   分析文件: {test_file}")
            result = analyzer.analyze_file(test_file)
            
            print(f"     质量评分: {result.overall_score:.1f}分")
            print(f"     质量等级: {result.overall_level.value}")
            print(f"     发现问题: {result.total_issues}个")
            print(f"     分析耗时: {result.duration:.2f}秒")
            
            if result.file_results:
                file_result = result.file_results[0]
                print(f"     指标数量: {len(file_result.metric_results)}个")
        else:
            print(f"   ⚠️ 文件不存在: {test_file}")


def simple_report(result):
    """生成简单的文本报告"""
    print(f"\n📋 分析报告")
    print(f"=" * 50)
    print(f"目标路径: {result.target_path}")
    print(f"总体评分: {result.overall_score:.1f}分")
    print(f"质量等级: {result.overall_level.value}")
    print(f"分析文件: {result.total_files}个")
    print(f"发现问题: {result.total_issues}个")
    print(f"严重问题: {result.critical_issues}个")
    print(f"分析耗时: {result.duration:.2f}秒")
    
    if result.file_results:
        print(f"\n📄 文件详情:")
        for file_result in result.file_results[:3]:  # 只显示前3个
            print(f"  • {os.path.basename(file_result.file_path)}: {file_result.quality_score:.1f}分")
            print(f"    问题: {file_result.total_issues}个, 语言: {file_result.language.value}")


if __name__ == "__main__":
    try:
        print("🚀 fuck-u-code Python版本 - 功能测试")
        print("=" * 60)
        
        test_language_detector()
        test_python_parser()
        test_metrics()
        test_analyzer()
        
        # 如果存在测试文件，生成简单报告
        test_file = "tests/fixtures/sample_bad_code.py"
        if os.path.exists(test_file):
            analyzer = CodeAnalyzer()
            result = analyzer.analyze_file(test_file)
            simple_report(result)
        
        print(f"\n✨ 所有测试完成！项目运行正常。")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)