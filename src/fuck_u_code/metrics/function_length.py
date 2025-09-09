"""
函数长度指标

评估函数长度合理性，检查函数是否过长。
"""

from typing import List, Dict, Any
from ..common.constants import LanguageType, FUNCTION_LENGTH_THRESHOLDS, PARAMETER_COUNT_THRESHOLDS
from ..parsers.models import ParseResult, Function
from .interfaces import BaseMetric
from .models import MetricResult, Issue, Severity


class FunctionLengthMetric(BaseMetric):
    """
    函数长度指标
    
    评估函数长度的合理性，识别过长的函数。
    """
    
    def __init__(self):
        super().__init__(
            name="函数长度",
            description="评估函数长度的合理性，过长的函数难以理解和维护",
            weight=0.20  # 20%权重
        )
    
    def _get_default_thresholds(self) -> Dict[str, Any]:
        """获取默认阈值配置"""
        return {
            # 函数长度阈值
            "length_excellent": FUNCTION_LENGTH_THRESHOLDS["excellent"],  # 20行
            "length_good": FUNCTION_LENGTH_THRESHOLDS["good"],            # 40行
            "length_poor": FUNCTION_LENGTH_THRESHOLDS["poor"],            # 120行
            
            # 参数数量阈值
            "param_excellent": PARAMETER_COUNT_THRESHOLDS["excellent"],   # 3个
            "param_good": PARAMETER_COUNT_THRESHOLDS["good"],            # 5个
            "param_poor": PARAMETER_COUNT_THRESHOLDS["poor"],            # 8个
        }
    
    def analyze(self, parse_result: ParseResult) -> MetricResult:
        """
        分析函数长度
        
        Args:
            parse_result: 解析结果
            
        Returns:
            MetricResult: 函数长度指标结果
        """
        all_functions = parse_result.all_functions
        
        if not all_functions:
            return self._create_metric_result(
                score=0.0,
                details={"message": "没有找到函数"},
                raw_data={"function_count": 0}
            )
        
        # 收集长度数据
        lengths = [func.line_count for func in all_functions]
        param_counts = [func.parameters for func in all_functions]
        
        # 计算统计信息
        avg_length = sum(lengths) / len(lengths)
        max_length = max(lengths)
        avg_params = sum(param_counts) / len(param_counts)
        max_params = max(param_counts)
        
        # 计算分数
        score = self._calculate_length_score(all_functions)
        
        # 生成问题列表
        issues = self._generate_issues(all_functions)
        
        # 详细信息
        details = {
            "function_count": len(all_functions),
            "average_length": round(avg_length, 1),
            "max_length": max_length,
            "min_length": min(lengths),
            "average_parameters": round(avg_params, 1),
            "max_parameters": max_params,
            "length_distribution": self._get_length_distribution(lengths),
            "parameter_distribution": self._get_parameter_distribution(param_counts),
        }
        
        # 原始数据
        raw_data = {
            "lengths": lengths,
            "parameter_counts": param_counts,
            "functions": [
                {
                    "name": func.name,
                    "length": func.line_count,
                    "parameters": func.parameters,
                    "start_line": func.start_line,
                    "class_name": func.class_name,
                }
                for func in all_functions
            ]
        }
        
        result = self._create_metric_result(score, issues, details, raw_data)
        
        # 添加改进建议
        self._add_suggestions(result, avg_length, max_length, avg_params, max_params)
        
        return result
    
    def _calculate_length_score(self, functions: List[Function]) -> float:
        """
        计算函数长度评分
        
        Args:
            functions: 函数列表
            
        Returns:
            float: 评分 (0.0-1.0)
        """
        if not functions:
            return 0.0
        
        lengths = [func.line_count for func in functions]
        param_counts = [func.parameters for func in functions]
        
        avg_length = sum(lengths) / len(lengths)
        avg_params = sum(param_counts) / len(param_counts)
        
        # 基于平均长度计算分数（权重70%）
        length_score = self._calculate_score_by_threshold(
            avg_length,
            {
                "excellent": self.get_threshold("length_excellent", 20),
                "good": self.get_threshold("length_good", 40),
                "poor": self.get_threshold("length_poor", 120),
            }
        )
        
        # 基于平均参数数量计算分数（权重30%）
        param_score = self._calculate_score_by_threshold(
            avg_params,
            {
                "excellent": self.get_threshold("param_excellent", 3),
                "good": self.get_threshold("param_good", 5),
                "poor": self.get_threshold("param_poor", 8),
            }
        )
        
        # 综合评分
        base_score = length_score * 0.7 + param_score * 0.3
        
        # 考虑极长函数的惩罚
        very_long_count = sum(1 for length in lengths if length > 200)
        if very_long_count > 0:
            penalty = min(0.3, very_long_count / len(functions))
            base_score += penalty
        
        # 考虑参数过多函数的惩罚
        many_params_count = sum(1 for count in param_counts if count > 10)
        if many_params_count > 0:
            penalty = min(0.2, many_params_count / len(functions))
            base_score += penalty
        
        return min(1.0, base_score)
    
    def _generate_issues(self, functions: List[Function]) -> List[Issue]:
        """
        生成函数长度问题列表
        
        Args:
            functions: 函数列表
            
        Returns:
            List[Issue]: 问题列表
        """
        issues = []
        
        length_good = self.get_threshold("length_good", 40)
        length_poor = self.get_threshold("length_poor", 120)
        param_good = self.get_threshold("param_good", 5)
        param_poor = self.get_threshold("param_poor", 8)
        
        for func in functions:
            # 检查函数长度
            if func.line_count > length_poor:
                severity = Severity.CRITICAL if func.line_count > 200 else Severity.HIGH
                message = f"函数 '{func.name}' 过长 ({func.line_count}行)"
                suggestion = "建议拆分函数，遵循单一职责原则"
                
                issues.append(Issue(
                    message=message,
                    severity=severity,
                    line_number=func.start_line,
                    rule_name="long_function",
                    suggestion=suggestion,
                    context={
                        "function_name": func.name,
                        "length": func.line_count,
                        "threshold": length_poor,
                        "class_name": func.class_name,
                    }
                ))
            
            elif func.line_count > length_good:
                message = f"函数 '{func.name}' 较长 ({func.line_count}行)"
                suggestion = "考虑将函数拆分为更小的函数"
                
                issues.append(Issue(
                    message=message,
                    severity=Severity.MEDIUM,
                    line_number=func.start_line,
                    rule_name="medium_long_function",
                    suggestion=suggestion,
                    context={
                        "function_name": func.name,
                        "length": func.line_count,
                        "threshold": length_good,
                    }
                ))
            
            # 检查参数数量
            if func.parameters > param_poor:
                severity = Severity.HIGH if func.parameters > 10 else Severity.MEDIUM
                message = f"函数 '{func.name}' 参数过多 ({func.parameters}个)"
                suggestion = "建议使用对象参数或数据类封装多个参数"
                
                issues.append(Issue(
                    message=message,
                    severity=severity,
                    line_number=func.start_line,
                    rule_name="too_many_parameters",
                    suggestion=suggestion,
                    context={
                        "function_name": func.name,
                        "parameter_count": func.parameters,
                        "threshold": param_poor,
                    }
                ))
            
            elif func.parameters > param_good:
                message = f"函数 '{func.name}' 参数较多 ({func.parameters}个)"
                suggestion = "考虑减少参数数量，提高函数内聚性"
                
                issues.append(Issue(
                    message=message,
                    severity=Severity.LOW,
                    line_number=func.start_line,
                    rule_name="many_parameters",
                    suggestion=suggestion,
                    context={
                        "function_name": func.name,
                        "parameter_count": func.parameters,
                        "threshold": param_good,
                    }
                ))
        
        return issues
    
    def _get_length_distribution(self, lengths: List[int]) -> Dict[str, int]:
        """
        获取函数长度分布统计
        
        Args:
            lengths: 长度列表
            
        Returns:
            Dict[str, int]: 分布统计
        """
        distribution = {
            "short_1_20": 0,     # 1-20行
            "medium_21_40": 0,   # 21-40行
            "long_41_80": 0,     # 41-80行
            "very_long_81_120": 0,  # 81-120行
            "extreme_121_plus": 0,  # 121行以上
        }
        
        for length in lengths:
            if 1 <= length <= 20:
                distribution["short_1_20"] += 1
            elif 21 <= length <= 40:
                distribution["medium_21_40"] += 1
            elif 41 <= length <= 80:
                distribution["long_41_80"] += 1
            elif 81 <= length <= 120:
                distribution["very_long_81_120"] += 1
            else:
                distribution["extreme_121_plus"] += 1
        
        return distribution
    
    def _get_parameter_distribution(self, param_counts: List[int]) -> Dict[str, int]:
        """
        获取参数数量分布统计
        
        Args:
            param_counts: 参数数量列表
            
        Returns:
            Dict[str, int]: 分布统计
        """
        distribution = {
            "few_0_3": 0,      # 0-3个
            "normal_4_5": 0,   # 4-5个
            "many_6_8": 0,     # 6-8个
            "too_many_9_plus": 0,  # 9个以上
        }
        
        for count in param_counts:
            if 0 <= count <= 3:
                distribution["few_0_3"] += 1
            elif 4 <= count <= 5:
                distribution["normal_4_5"] += 1
            elif 6 <= count <= 8:
                distribution["many_6_8"] += 1
            else:
                distribution["too_many_9_plus"] += 1
        
        return distribution
    
    def _add_suggestions(self, result: MetricResult, avg_length: float, max_length: int,
                        avg_params: float, max_params: int) -> None:
        """
        添加改进建议
        
        Args:
            result: 指标结果
            avg_length: 平均长度
            max_length: 最大长度
            avg_params: 平均参数数
            max_params: 最大参数数
        """
        if avg_length > 60:
            result.add_suggestion("项目函数平均长度偏高，建议重构长函数")
        
        if max_length > 200:
            result.add_suggestion("存在极长函数，建议优先重构")
        
        if avg_params > 6:
            result.add_suggestion("函数参数数量普遍偏多，考虑使用对象参数")
        
        if max_params > 10:
            result.add_suggestion("存在参数过多的函数，建议重新设计接口")
        
        if result.issue_count > 0:
            result.add_suggestion("遵循单一职责原则，将复杂函数拆分为多个简单函数")
            result.add_suggestion("考虑提取公共逻辑，减少代码重复")
            result.add_suggestion("使用配置对象或建造者模式处理多参数情况")
        
        long_function_ratio = len([i for i in result.issues if "长" in i.message]) / max(1, result.issue_count)
        if long_function_ratio > 0.5:
            result.add_suggestion("长函数比例较高，建议制定函数重构标准")
    
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