"""
解析器模块

负责将不同编程语言的源代码解析为统一的抽象语法树(AST)表示，
提取函数信息、注释信息等关键数据供后续分析使用。
"""

from .interfaces import Parser, ParseResult
from .models import Function, ParseResult as ParseResultModel
from .factory import ParserFactory
from .python_parser import PythonParser

__all__ = [
    "Parser",
    "ParseResult", 
    "ParseResultModel",
    "Function",
    "ParserFactory",
    "PythonParser",
]