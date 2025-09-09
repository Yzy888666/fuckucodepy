"""
循环复杂度指标

计算代码的圈复杂度，评估代码的逻辑复杂程度。
"""

from typing import List, Dict, Any
from ..common.constants import LanguageType, COMPLEXITY_THRESHOLDS
from ..parsers.models import ParseResult, Function
from .interfaces import BaseMetric
from .models import MetricResult, Issue, Severity


class ComplexityMetric(BaseMetric):
    """
    循环复杂度指标
    
    计算函数的循环复杂度，识别过于复杂的函数。
    """
    
    def __init__(self):
        super().__init__(
            name="循环复杂度",
            description="测量函数控制流的复杂程度，复杂度越高表示函数越难理解和维护",
            weight=0.30  # 30%权重
        )
    
    def _get_default_thresholds(self) -> Dict[str, Any]:
        """获取默认阈值配置"""
        return {
            "excellent": COMPLEXITY_THRESHOLDS["excellent"],    # 5
            "good": COMPLEXITY_THRESHOLDS["good"],              # 10
            "average": COMPLEXITY_THRESHOLDS["average"],        # 15
            "poor": COMPLEXITY_THRESHOLDS["poor"],              # 20
        }
    
    def analyze(self, parse_result: ParseResult) -> MetricResult:
        """
        分析循环复杂度
        
        Args:
            parse_result: 解析结果
            
        Returns:
            MetricResult: 复杂度指标结果
        """
        all_functions = parse_result.all_functions
        
        if not all_functions:
            return self._create_metric_result(
                score=0.0,
                details={"message": "没有找到函数"},
                raw_data={"function_count": 0, "total_complexity": 0}
            )
        
        # 收集复杂度数据
        complexities = [func.complexity for func in all_functions]
        total_complexity = sum(complexities)
        average_complexity = total_complexity / len(complexities)
        max_complexity = max(complexities)
        
        # 计算分数
        score = self._calculate_complexity_score(all_functions)
        
        # 生成问题列表
        issues = self._generate_issues(all_functions)
        
        # 详细信息
        details = {
            "function_count": len(all_functions),
            "average_complexity": round(average_complexity, 2),
            "max_complexity": max_complexity,
            "min_complexity": min(complexities),
            "complexity_distribution": self._get_complexity_distribution(complexities),
        }
        
        # 原始数据
        raw_data = {
            "complexities": complexities,
            "total_complexity": total_complexity,
            "functions": [
                {
                    "name": func.name,
                    "complexity": func.complexity,
                    "start_line": func.start_line,
                    "line_count": func.line_count,
                }
                for func in all_functions
            ]
        }
        
        result = self._create_metric_result(score, issues, details, raw_data)
        
        # 添加改进建议
        self._add_suggestions(result, average_complexity, max_complexity)
        
        return result
    
    def _calculate_complexity_score(self, functions: List[Function]) -> float:
        """
        计算复杂度评分
        
        Args:
            functions: 函数列表
            
        Returns:
            float: 评分 (0.0-1.0)
        """
        if not functions:
            return 0.0
        
        complexities = [func.complexity for func in functions]
        average_complexity = sum(complexities) / len(complexities)
        
        # 基于平均复杂度计算基础分数
        base_score = self._calculate_score_by_threshold(
            average_complexity,
            {
                "excellent": self.get_threshold("excellent", 5),
                "good": self.get_threshold("good", 10),
                "poor": self.get_threshold("poor", 20),
            }
        )
        
        # 考虑高复杂度函数的惩罚
        high_complexity_count = sum(1 for c in complexities if c > 15)
        high_complexity_ratio = high_complexity_count / len(complexities)
        penalty = high_complexity_ratio * 0.3  # 最多30%惩罚
        
        # 考虑最大复杂度的影响
        max_complexity = max(complexities)
        if max_complexity > 30:
            penalty += 0.2  # 额外20%惩罚
        elif max_complexity > 20:
            penalty += 0.1  # 额外10%惩罚
        
        return min(1.0, base_score + penalty)
    
    def _generate_issues(self, functions: List[Function]) -> List[Issue]:
        """
        生成复杂度问题列表
        
        Args:
            functions: 函数列表
            
        Returns:
            List[Issue]: 问题列表
        """
        issues = []
        
        excellent_threshold = self.get_threshold("excellent", 5)
        good_threshold = self.get_threshold("good", 10)
        poor_threshold = self.get_threshold("poor", 20)
        
        for func in functions:
            complexity = func.complexity
            
            if complexity > poor_threshold:
                severity = Severity.CRITICAL if complexity > 30 else Severity.HIGH
                message = f"函数 '{func.name}' 循环复杂度过高 ({complexity})"
                suggestion = "建议拆分函数，将复杂逻辑分解为多个简单函数"
                
                issues.append(Issue(
                    message=message,
                    severity=severity,
                    line_number=func.start_line,
                    rule_name="high_complexity",
                    suggestion=suggestion,
                    context={
                        "function_name": func.name,
                        "complexity": complexity,
                        "threshold": poor_threshold,
                        "class_name": func.class_name,
                    }
                ))
            
            elif complexity > good_threshold:
                message = f"函数 '{func.name}' 循环复杂度较高 ({complexity})"
                suggestion = "考虑简化控制流，减少嵌套层次"
                
                issues.append(Issue(
                    message=message,
                    severity=Severity.MEDIUM,
                    line_number=func.start_line,
                    rule_name="medium_complexity",
                    suggestion=suggestion,
                    context={
                        "function_name": func.name,
                        "complexity": complexity,
                        "threshold": good_threshold,
                    }
                ))
        
        return issues
    
    def _get_complexity_distribution(self, complexities: List[int]) -> Dict[str, int]:
        """
        获取复杂度分布统计
        
        Args:
            complexities: 复杂度列表
            
        Returns:
            Dict[str, int]: 分布统计
        """
        distribution = {
            "low_1_5": 0,       # 1-5
            "medium_6_10": 0,   # 6-10
            "high_11_15": 0,    # 11-15
            "very_high_16_20": 0,  # 16-20
            "extreme_21_plus": 0,  # 21+
        }
        
        for complexity in complexities:
            if 1 <= complexity <= 5:
                distribution["low_1_5"] += 1
            elif 6 <= complexity <= 10:
                distribution["medium_6_10"] += 1
            elif 11 <= complexity <= 15:
                distribution["high_11_15"] += 1
            elif 16 <= complexity <= 20:
                distribution["very_high_16_20"] += 1
            else:
                distribution["extreme_21_plus"] += 1
        
        return distribution
    
    def _add_suggestions(self, result: MetricResult, avg_complexity: float, max_complexity: int) -> None:
        """
        添加改进建议
        
        Args:
            result: 指标结果
            avg_complexity: 平均复杂度
            max_complexity: 最大复杂度
        """
        if avg_complexity > 15:
            result.add_suggestion("项目整体复杂度偏高，建议重构复杂函数")
        
        if max_complexity > 30:
            result.add_suggestion("存在极度复杂的函数，建议优先重构")
        
        if result.issue_count > 0:
            result.add_suggestion("使用单一职责原则，将复杂函数拆分为多个简单函数")
            result.add_suggestion("考虑使用设计模式（如策略模式、状态模式）简化复杂逻辑")
            result.add_suggestion("减少嵌套层次，使用早期返回模式")
        
        high_complexity_ratio = len([i for i in result.issues if i.severity in [Severity.HIGH, Severity.CRITICAL]]) / max(1, result.issue_count)
        if high_complexity_ratio > 0.3:
            result.add_suggestion("高复杂度函数比例较高，建议制定代码重构计划")
    
    def supported_languages(self) -> List[LanguageType]:
        """支持的语言类型"""
        return [
            LanguageType.PYTHON,
            LanguageType.JAVASCRIPT,
            LanguageType.TYPESCRIPT,
            LanguageType.JAVA,
            LanguageType.C,
            LanguageType.CPP,
        ]