"""
指标系统数据模型

定义指标计算结果的数据结构。
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class Severity(Enum):
    """问题严重程度"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Issue:
    """
    代码问题信息
    
    Attributes:
        message: 问题描述
        severity: 严重程度
        line_number: 行号
        column: 列号
        rule_name: 规则名称
        suggestion: 修复建议
        context: 上下文信息
    """
    message: str
    severity: Severity = Severity.MEDIUM
    line_number: Optional[int] = None
    column: Optional[int] = None
    rule_name: Optional[str] = None
    suggestion: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    @property
    def severity_score(self) -> float:
        """获取严重程度对应的分数"""
        severity_scores = {
            Severity.INFO: 0.1,
            Severity.LOW: 0.3,
            Severity.MEDIUM: 0.5,
            Severity.HIGH: 0.7,
            Severity.CRITICAL: 1.0,
        }
        return severity_scores.get(self.severity, 0.5)
    
    def __str__(self) -> str:
        result = self.message
        if self.line_number:
            result = f"第{self.line_number}行: {result}"
        if self.suggestion:
            result += f" (建议: {self.suggestion})"
        return result


@dataclass
class MetricResult:
    """
    指标计算结果
    
    Attributes:
        metric_name: 指标名称
        score: 评分 (0.0-1.0，越低表示质量越好)
        weight: 权重 (0.0-1.0)
        description: 指标描述
        issues: 问题列表
        details: 详细信息
        raw_data: 原始数据
        suggestions: 改进建议
    """
    metric_name: str
    score: float
    weight: float = 1.0
    description: str = ""
    issues: List[Issue] = None
    details: Dict[str, Any] = None
    raw_data: Dict[str, Any] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.details is None:
            self.details = {}
        if self.raw_data is None:
            self.raw_data = {}
        if self.suggestions is None:
            self.suggestions = []
    
    @property
    def weighted_score(self) -> float:
        """获取加权分数"""
        return self.score * self.weight
    
    @property
    def issue_count(self) -> int:
        """获取问题数量"""
        return len(self.issues)
    
    @property
    def critical_issues(self) -> List[Issue]:
        """获取严重问题列表"""
        return [issue for issue in self.issues if issue.severity == Severity.CRITICAL]
    
    @property
    def high_issues(self) -> List[Issue]:
        """获取高严重性问题列表"""
        return [issue for issue in self.issues if issue.severity == Severity.HIGH]
    
    @property
    def grade(self) -> str:
        """获取等级评定"""
        if self.score <= 0.2:
            return "优秀"
        elif self.score <= 0.4:
            return "良好"
        elif self.score <= 0.6:
            return "一般"
        elif self.score <= 0.8:
            return "较差"
        else:
            return "糟糕"
    
    def add_issue(self, issue: Issue) -> None:
        """添加问题"""
        self.issues.append(issue)
    
    def add_suggestion(self, suggestion: str) -> None:
        """添加改进建议"""
        if suggestion not in self.suggestions:
            self.suggestions.append(suggestion)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "metric_name": self.metric_name,
            "score": self.score,
            "weight": self.weight,
            "weighted_score": self.weighted_score,
            "grade": self.grade,
            "description": self.description,
            "issue_count": self.issue_count,
            "critical_issues": len(self.critical_issues),
            "high_issues": len(self.high_issues),
            "details": self.details,
            "raw_data": self.raw_data,
            "suggestions": self.suggestions,
        }
    
    def __str__(self) -> str:
        return f"MetricResult({self.metric_name}, score={self.score:.2f}, issues={self.issue_count})"


@dataclass
class MetricSummary:
    """
    指标汇总信息
    
    Attributes:
        total_metrics: 指标总数
        overall_score: 总体评分
        weighted_score: 加权评分
        total_issues: 问题总数
        critical_issues: 严重问题数
        high_issues: 高严重性问题数
        grade: 总体等级
        details: 详细统计
    """
    total_metrics: int
    overall_score: float
    weighted_score: float
    total_issues: int
    critical_issues: int
    high_issues: int
    grade: str
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
    
    @classmethod
    def from_results(cls, results: List[MetricResult]) -> 'MetricSummary':
        """从指标结果列表创建汇总"""
        if not results:
            return cls(0, 0.0, 0.0, 0, 0, 0, "未评估")
        
        total_weight = sum(result.weight for result in results)
        if total_weight == 0:
            weighted_score = sum(result.score for result in results) / len(results)
        else:
            weighted_score = sum(result.weighted_score for result in results) / total_weight
        
        overall_score = sum(result.score for result in results) / len(results)
        total_issues = sum(result.issue_count for result in results)
        critical_issues = sum(len(result.critical_issues) for result in results)
        high_issues = sum(len(result.high_issues) for result in results)
        
        # 确定总体等级
        if weighted_score <= 0.2:
            grade = "优秀"
        elif weighted_score <= 0.4:
            grade = "良好"
        elif weighted_score <= 0.6:
            grade = "一般"
        elif weighted_score <= 0.8:
            grade = "较差"
        else:
            grade = "糟糕"
        
        # 详细统计
        details = {
            "metric_scores": {result.metric_name: result.score for result in results},
            "metric_grades": {result.metric_name: result.grade for result in results},
            "metric_issues": {result.metric_name: result.issue_count for result in results},
        }
        
        return cls(
            total_metrics=len(results),
            overall_score=overall_score,
            weighted_score=weighted_score,
            total_issues=total_issues,
            critical_issues=critical_issues,
            high_issues=high_issues,
            grade=grade,
            details=details
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_metrics": self.total_metrics,
            "overall_score": self.overall_score,
            "weighted_score": self.weighted_score,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "high_issues": self.high_issues,
            "grade": self.grade,
            "details": self.details,
        }