"""
指标系统模块

实现七大代码质量评估指标：
1. 循环复杂度 (Complexity)
2. 函数长度 (Function Length) 
3. 注释覆盖率 (Comment Ratio)
4. 错误处理 (Error Handling)
5. 命名规范 (Naming Convention)
6. 代码重复度 (Code Duplication)
7. 代码结构 (Structure Analysis)
"""

from .interfaces import Metric, MetricResult
from .models import MetricResult as MetricResultModel, Issue
from .factory import MetricFactory, get_metric_factory
from .complexity import ComplexityMetric
from .function_length import FunctionLengthMetric
from .comment_ratio import CommentRatioMetric

__all__ = [
    "Metric",
    "MetricResult",
    "MetricResultModel", 
    "Issue",
    "MetricFactory",
    "get_metric_factory",
    "ComplexityMetric",
    "FunctionLengthMetric", 
    "CommentRatioMetric",
]