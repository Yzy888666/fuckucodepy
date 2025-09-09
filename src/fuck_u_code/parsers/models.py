"""
解析器数据模型

定义解析结果的数据结构，包括函数信息、解析结果等。
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Dict
from ..common.constants import LanguageType


@dataclass
class Function:
    """
    函数信息模型
    
    Attributes:
        name: 函数名
        start_line: 开始行号（从1开始）
        end_line: 结束行号
        complexity: 循环复杂度
        parameters: 参数数量
        return_type: 返回类型（如果可获取）
        docstring: 文档字符串
        ast_node: AST节点引用（用于进一步分析）
        is_async: 是否为异步函数
        is_generator: 是否为生成器函数
        decorators: 装饰器列表
        class_name: 所属类名（如果是方法）
        visibility: 可见性（public, private, protected）
    """
    name: str
    start_line: int
    end_line: int
    complexity: int = 1
    parameters: int = 0
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    ast_node: Optional[Any] = None
    is_async: bool = False
    is_generator: bool = False
    decorators: List[str] = None
    class_name: Optional[str] = None
    visibility: str = "public"
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []
    
    @property
    def line_count(self) -> int:
        """获取函数行数"""
        return self.end_line - self.start_line + 1
    
    @property
    def is_method(self) -> bool:
        """是否为类方法"""
        return self.class_name is not None
    
    @property
    def is_private(self) -> bool:
        """是否为私有函数/方法"""
        return self.visibility == "private" or self.name.startswith('_')
    
    def __str__(self) -> str:
        result = f"{self.name}({self.parameters} params)"
        if self.class_name:
            result = f"{self.class_name}.{result}"
        return result


@dataclass
class Class:
    """
    类信息模型
    
    Attributes:
        name: 类名
        start_line: 开始行号
        end_line: 结束行号
        methods: 方法列表
        base_classes: 基类列表
        docstring: 文档字符串
        ast_node: AST节点引用
    """
    name: str
    start_line: int
    end_line: int
    methods: List[Function] = None
    base_classes: List[str] = None
    docstring: Optional[str] = None
    ast_node: Optional[Any] = None
    
    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.base_classes is None:
            self.base_classes = []
    
    @property
    def line_count(self) -> int:
        """获取类行数"""
        return self.end_line - self.start_line + 1
    
    @property
    def method_count(self) -> int:
        """获取方法数量"""
        return len(self.methods)


@dataclass
class ParseResult:
    """
    解析结果模型
    
    Attributes:
        file_path: 文件路径
        language: 语言类型
        functions: 函数列表
        classes: 类列表
        total_lines: 总行数
        code_lines: 代码行数（排除空行和注释）
        comment_lines: 注释行数
        import_statements: 导入语句列表
        ast_root: AST根节点
        encoding: 文件编码
        parse_time: 解析耗时（秒）
        errors: 解析错误列表
    """
    file_path: str
    language: LanguageType
    functions: List[Function] = None
    classes: List[Class] = None
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    import_statements: List[str] = None
    ast_root: Optional[Any] = None
    encoding: str = "utf-8"
    parse_time: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.functions is None:
            self.functions = []
        if self.classes is None:
            self.classes = []
        if self.import_statements is None:
            self.import_statements = []
        if self.errors is None:
            self.errors = []
    
    @property
    def function_count(self) -> int:
        """获取函数总数"""
        # 包括独立函数和类方法
        total = len(self.functions)
        for cls in self.classes:
            total += len(cls.methods)
        return total
    
    @property
    def class_count(self) -> int:
        """获取类数量"""
        return len(self.classes)
    
    @property
    def all_functions(self) -> List[Function]:
        """获取所有函数（包括类方法）"""
        all_funcs = list(self.functions)
        for cls in self.classes:
            all_funcs.extend(cls.methods)
        return all_funcs
    
    @property
    def average_function_length(self) -> float:
        """获取平均函数长度"""
        all_funcs = self.all_functions
        if not all_funcs:
            return 0.0
        
        total_lines = sum(func.line_count for func in all_funcs)
        return total_lines / len(all_funcs)
    
    @property
    def average_complexity(self) -> float:
        """获取平均复杂度"""
        all_funcs = self.all_functions
        if not all_funcs:
            return 1.0
        
        total_complexity = sum(func.complexity for func in all_funcs)
        return total_complexity / len(all_funcs)
    
    @property
    def comment_ratio(self) -> float:
        """获取注释比例"""
        if self.total_lines == 0:
            return 0.0
        return self.comment_lines / self.total_lines
    
    @property
    def has_errors(self) -> bool:
        """是否有解析错误"""
        return len(self.errors) > 0
    
    def add_error(self, error: str) -> None:
        """添加解析错误"""
        self.errors.append(error)
    
    def get_function_by_name(self, name: str) -> Optional[Function]:
        """根据名称查找函数"""
        for func in self.all_functions:
            if func.name == name:
                return func
        return None
    
    def get_functions_by_complexity(self, min_complexity: int) -> List[Function]:
        """获取复杂度超过阈值的函数"""
        return [func for func in self.all_functions if func.complexity >= min_complexity]
    
    def get_long_functions(self, min_lines: int) -> List[Function]:
        """获取行数超过阈值的函数"""
        return [func for func in self.all_functions if func.line_count >= min_lines]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "file_path": self.file_path,
            "language": self.language.value,
            "function_count": self.function_count,
            "class_count": self.class_count,
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "comment_ratio": self.comment_ratio,
            "average_function_length": self.average_function_length,
            "average_complexity": self.average_complexity,
            "import_count": len(self.import_statements),
            "parse_time": self.parse_time,
            "has_errors": self.has_errors,
            "error_count": len(self.errors),
        }
    
    def __str__(self) -> str:
        return (f"ParseResult({self.file_path}, {self.language.value}, "
                f"{self.function_count} functions, {self.total_lines} lines)")


@dataclass 
class ParseError:
    """
    解析错误信息
    
    Attributes:
        message: 错误消息
        line_number: 错误行号
        column: 错误列号
        error_type: 错误类型
        suggestion: 修复建议
    """
    message: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    error_type: str = "parse_error"
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        result = self.message
        if self.line_number:
            result = f"第{self.line_number}行: {result}"
        if self.suggestion:
            result += f" (建议: {self.suggestion})"
        return result