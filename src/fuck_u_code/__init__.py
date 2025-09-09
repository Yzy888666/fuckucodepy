"""
fuck-u-code Python版本 - 代码质量分析工具

一个专为挖掘"屎山代码"设计的工具，能无情揭露代码的丑陋真相。
"""

__version__ = "1.0.0"
__author__ = "fuck-u-code Team"
__email__ = "team@fuck-u-code.com"

from .analyzers.code_analyzer import CodeAnalyzer
from .common.constants import LanguageType, QualityLevel
from .common.exceptions import FuckUCodeException

__all__ = [
    "CodeAnalyzer", 
    "LanguageType", 
    "QualityLevel", 
    "FuckUCodeException",
    "__version__"
]