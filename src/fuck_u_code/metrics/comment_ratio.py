"""
注释覆盖率指标

评估代码的注释充分程度，检查关键函数和类的文档完整性。
"""

from typing import List, Dict, Any
from ..common.constants import LanguageType, COMMENT_RATIO_THRESHOLDS
from ..parsers.models import ParseResult, Function
from .interfaces import BaseMetric
from .models import MetricResult, Issue, Severity


class CommentRatioMetric(BaseMetric):
    """
    注释覆盖率指标
    
    评估代码注释的充分程度和质量。
    """
    
    def __init__(self):
        super().__init__(
            name="注释覆盖率",
            description="评估代码注释的充分程度，良好的注释有助于代码理解和维护",
            weight=0.15  # 15%权重
        )
    
    def _get_default_thresholds(self) -> Dict[str, Any]:
        """获取默认阈值配置"""
        return {
            "optimal_min": COMMENT_RATIO_THRESHOLDS["optimal_min"],    # 15%
            "optimal_max": COMMENT_RATIO_THRESHOLDS["optimal_max"],    # 25%
            "minimum": COMMENT_RATIO_THRESHOLDS["minimum"],            # 10%
            "doc_coverage_good": 0.8,   # 80%文档覆盖率为良好
            "doc_coverage_poor": 0.5,   # 50%以下为差
        }
    
    def analyze(self, parse_result: ParseResult) -> MetricResult:
        """
        分析注释覆盖率
        
        Args:
            parse_result: 解析结果
            
        Returns:
            MetricResult: 注释覆盖率指标结果
        """
        # 基本统计
        total_lines = parse_result.total_lines
        comment_lines = parse_result.comment_lines
        comment_ratio = parse_result.comment_ratio
        
        all_functions = parse_result.all_functions
        
        # 文档覆盖率统计
        doc_stats = self._analyze_documentation(all_functions, parse_result.classes)
        
        # 计算分数
        score = self._calculate_comment_score(comment_ratio, doc_stats)
        
        # 生成问题列表
        issues = self._generate_issues(comment_ratio, doc_stats, all_functions, parse_result.classes)
        
        # 详细信息
        details = {
            "total_lines": total_lines,
            "comment_lines": comment_lines,
            "comment_ratio": round(comment_ratio, 3),
            "comment_ratio_percentage": round(comment_ratio * 100, 1),
            **doc_stats,
            "comment_quality": self._assess_comment_quality(comment_ratio),
        }
        
        # 原始数据
        raw_data = {
            "comment_lines": comment_lines,
            "total_lines": total_lines,
            "functions_with_docstring": doc_stats["functions_with_docstring"],
            "functions_without_docstring": doc_stats["functions_without_docstring"],
            "classes_with_docstring": doc_stats["classes_with_docstring"],
            "classes_without_docstring": doc_stats["classes_without_docstring"],
        }
        
        result = self._create_metric_result(score, issues, details, raw_data)
        
        # 添加改进建议
        self._add_suggestions(result, comment_ratio, doc_stats)
        
        return result
    
    def _analyze_documentation(self, functions: List[Function], classes: List) -> Dict[str, Any]:
        """
        分析文档覆盖率
        
        Args:
            functions: 函数列表
            classes: 类列表
            
        Returns:
            Dict[str, Any]: 文档统计信息
        """
        # 函数文档统计
        functions_with_doc = [f for f in functions if f.docstring and f.docstring.strip()]
        functions_without_doc = [f for f in functions if not f.docstring or not f.docstring.strip()]
        
        function_doc_ratio = len(functions_with_doc) / len(functions) if functions else 0
        
        # 类文档统计
        classes_with_doc = [c for c in classes if c.docstring and c.docstring.strip()]
        classes_without_doc = [c for c in classes if not c.docstring or not c.docstring.strip()]
        
        class_doc_ratio = len(classes_with_doc) / len(classes) if classes else 0
        
        # 公共函数/方法文档统计（更重要）
        public_functions = [f for f in functions if not f.is_private]
        public_with_doc = [f for f in public_functions if f.docstring and f.docstring.strip()]
        public_doc_ratio = len(public_with_doc) / len(public_functions) if public_functions else 0
        
        # 复杂函数文档统计
        complex_functions = [f for f in functions if f.complexity > 10 or f.line_count > 50]
        complex_with_doc = [f for f in complex_functions if f.docstring and f.docstring.strip()]
        complex_doc_ratio = len(complex_with_doc) / len(complex_functions) if complex_functions else 0
        
        return {
            "total_functions": len(functions),
            "functions_with_docstring": len(functions_with_doc),
            "functions_without_docstring": len(functions_without_doc),
            "function_doc_ratio": round(function_doc_ratio, 3),
            "function_doc_percentage": round(function_doc_ratio * 100, 1),
            
            "total_classes": len(classes),
            "classes_with_docstring": len(classes_with_doc),
            "classes_without_docstring": len(classes_without_doc),
            "class_doc_ratio": round(class_doc_ratio, 3),
            "class_doc_percentage": round(class_doc_ratio * 100, 1),
            
            "public_functions": len(public_functions),
            "public_with_doc": len(public_with_doc),
            "public_doc_ratio": round(public_doc_ratio, 3),
            "public_doc_percentage": round(public_doc_ratio * 100, 1),
            
            "complex_functions": len(complex_functions),
            "complex_with_doc": len(complex_with_doc),
            "complex_doc_ratio": round(complex_doc_ratio, 3),
            "complex_doc_percentage": round(complex_doc_ratio * 100, 1),
            
            "overall_doc_ratio": round((function_doc_ratio + class_doc_ratio) / 2, 3) if functions or classes else 0,
        }
    
    def _calculate_comment_score(self, comment_ratio: float, doc_stats: Dict[str, Any]) -> float:
        """
        计算注释评分
        
        Args:
            comment_ratio: 注释比例
            doc_stats: 文档统计
            
        Returns:
            float: 评分 (0.0-1.0)
        """
        optimal_min = self.get_threshold("optimal_min", 0.15)
        optimal_max = self.get_threshold("optimal_max", 0.25)
        minimum = self.get_threshold("minimum", 0.10)
        
        # 1. 注释比例评分（40%权重）
        if optimal_min <= comment_ratio <= optimal_max:
            comment_score = 0.0  # 最佳范围
        elif comment_ratio < minimum:
            comment_score = 0.8  # 注释太少，严重问题
        elif comment_ratio < optimal_min:
            # 注释不足
            comment_score = 0.4 * (optimal_min - comment_ratio) / (optimal_min - minimum)
        else:
            # 注释过多
            excess = comment_ratio - optimal_max
            comment_score = min(0.6, 0.2 + excess * 2)  # 过度注释也不好
        
        # 2. 文档覆盖率评分（60%权重）
        overall_doc_ratio = doc_stats["overall_doc_ratio"]
        public_doc_ratio = doc_stats["public_doc_ratio"]
        complex_doc_ratio = doc_stats["complex_doc_ratio"]
        
        # 加权计算文档覆盖率评分
        doc_score = (
            (1 - overall_doc_ratio) * 0.4 +      # 整体文档覆盖率 40%
            (1 - public_doc_ratio) * 0.4 +       # 公共接口文档覆盖率 40%
            (1 - complex_doc_ratio) * 0.2        # 复杂函数文档覆盖率 20%
        )
        
        # 综合评分
        final_score = comment_score * 0.4 + doc_score * 0.6
        
        return min(1.0, max(0.0, final_score))
    
    def _generate_issues(self, comment_ratio: float, doc_stats: Dict[str, Any], 
                        functions: List[Function], classes: List) -> List[Issue]:
        """
        生成注释问题列表
        
        Args:
            comment_ratio: 注释比例
            doc_stats: 文档统计
            functions: 函数列表
            classes: 类列表
            
        Returns:
            List[Issue]: 问题列表
        """
        issues = []
        
        minimum = self.get_threshold("minimum", 0.10)
        optimal_min = self.get_threshold("optimal_min", 0.15)
        optimal_max = self.get_threshold("optimal_max", 0.25)
        
        # 检查总体注释比例
        if comment_ratio < minimum:
            issues.append(Issue(
                message=f"注释比例过低 ({comment_ratio*100:.1f}%)，远低于建议的最低标准",
                severity=Severity.HIGH,
                rule_name="insufficient_comments",
                suggestion=f"建议将注释比例提升至{optimal_min*100:.0f}%-{optimal_max*100:.0f}%",
                context={"comment_ratio": comment_ratio, "threshold": minimum}
            ))
        elif comment_ratio < optimal_min:
            issues.append(Issue(
                message=f"注释比例偏低 ({comment_ratio*100:.1f}%)，建议增加注释",
                severity=Severity.MEDIUM,
                rule_name="low_comments",
                suggestion=f"建议将注释比例提升至{optimal_min*100:.0f}%-{optimal_max*100:.0f}%",
                context={"comment_ratio": comment_ratio, "threshold": optimal_min}
            ))
        elif comment_ratio > optimal_max * 1.5:  # 超过37.5%认为过多
            issues.append(Issue(
                message=f"注释比例过高 ({comment_ratio*100:.1f}%)，可能存在冗余注释",
                severity=Severity.LOW,
                rule_name="excessive_comments",
                suggestion="检查是否存在无用注释，保持注释简洁有效",
                context={"comment_ratio": comment_ratio, "threshold": optimal_max}
            ))
        
        # 检查函数文档
        functions_without_doc = [f for f in functions if not f.docstring or not f.docstring.strip()]
        if functions_without_doc:
            # 优先检查公共函数
            public_without_doc = [f for f in functions_without_doc if not f.is_private]
            if public_without_doc:
                for func in public_without_doc[:5]:  # 最多显示5个
                    issues.append(Issue(
                        message=f"公共函数 '{func.name}' 缺少文档字符串",
                        severity=Severity.MEDIUM,
                        line_number=func.start_line,
                        rule_name="missing_function_docstring",
                        suggestion="添加函数文档字符串，说明功能、参数和返回值",
                        context={"function_name": func.name, "is_public": True}
                    ))
            
            # 检查复杂函数
            complex_without_doc = [f for f in functions_without_doc 
                                 if f.complexity > 10 or f.line_count > 50]
            if complex_without_doc:
                for func in complex_without_doc[:3]:  # 最多显示3个
                    issues.append(Issue(
                        message=f"复杂函数 '{func.name}' 缺少文档字符串",
                        severity=Severity.HIGH,
                        line_number=func.start_line,
                        rule_name="missing_complex_function_docstring",
                        suggestion="复杂函数应该有详细的文档说明",
                        context={
                            "function_name": func.name,
                            "complexity": func.complexity,
                            "line_count": func.line_count
                        }
                    ))
        
        # 检查类文档
        classes_without_doc = [c for c in classes if not c.docstring or not c.docstring.strip()]
        if classes_without_doc:
            for cls in classes_without_doc[:5]:  # 最多显示5个
                issues.append(Issue(
                    message=f"类 '{cls.name}' 缺少文档字符串",
                    severity=Severity.MEDIUM,
                    line_number=cls.start_line,
                    rule_name="missing_class_docstring",
                    suggestion="添加类文档字符串，说明类的用途和主要功能",
                    context={"class_name": cls.name}
                ))
        
        return issues
    
    def _assess_comment_quality(self, comment_ratio: float) -> str:
        """
        评估注释质量等级
        
        Args:
            comment_ratio: 注释比例
            
        Returns:
            str: 质量等级
        """
        optimal_min = self.get_threshold("optimal_min", 0.15)
        optimal_max = self.get_threshold("optimal_max", 0.25)
        minimum = self.get_threshold("minimum", 0.10)
        
        if optimal_min <= comment_ratio <= optimal_max:
            return "优秀"
        elif comment_ratio >= minimum and comment_ratio < optimal_min:
            return "良好"
        elif comment_ratio < minimum:
            return "不足"
        elif comment_ratio > optimal_max * 1.5:
            return "过多"
        else:
            return "一般"
    
    def _add_suggestions(self, result: MetricResult, comment_ratio: float, doc_stats: Dict[str, Any]) -> None:
        """
        添加改进建议
        
        Args:
            result: 指标结果
            comment_ratio: 注释比例
            doc_stats: 文档统计
        """
        minimum = self.get_threshold("minimum", 0.10)
        optimal_min = self.get_threshold("optimal_min", 0.15)
        
        if comment_ratio < minimum:
            result.add_suggestion("注释严重不足，建议为主要函数和复杂逻辑添加注释")
        elif comment_ratio < optimal_min:
            result.add_suggestion("适当增加注释，特别是复杂算法和业务逻辑部分")
        
        if doc_stats["public_doc_ratio"] < 0.8:
            result.add_suggestion("公共接口缺少文档，建议为所有公共函数添加文档字符串")
        
        if doc_stats["complex_doc_ratio"] < 0.7:
            result.add_suggestion("复杂函数缺少文档，建议为高复杂度函数添加详细说明")
        
        if doc_stats["class_doc_ratio"] < 0.8:
            result.add_suggestion("类缺少文档，建议为所有类添加文档字符串")
        
        if result.issue_count > 0:
            result.add_suggestion("遵循文档规范，使用统一的文档格式（如Google风格或Numpy风格）")
            result.add_suggestion("注释应该说明'为什么'而不仅仅是'做什么'")
            result.add_suggestion("定期检查和更新注释，确保与代码保持同步")
    
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