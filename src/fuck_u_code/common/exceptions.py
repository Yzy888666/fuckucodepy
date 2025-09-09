"""
异常定义模块

定义项目中使用的所有异常类，提供详细的错误信息和处理建议。
"""

from typing import Optional


class FuckUCodeException(Exception):
    """
    fuck-u-code基础异常类
    
    所有项目相关异常的基类，提供统一的异常处理接口。
    """
    
    def __init__(
        self, 
        message: str, 
        suggestion: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
    
    def __str__(self) -> str:
        result = self.message
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        if self.error_code:
            result += f"\n错误代码: {self.error_code}"
        return result


class ParseError(FuckUCodeException):
    """
    解析错误
    
    在解析源代码时发生的错误，如语法错误、编码问题等。
    """
    
    def __init__(
        self, 
        message: str, 
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message, suggestion, "PARSE_ERROR")
        self.file_path = file_path
        self.line_number = line_number
    
    def __str__(self) -> str:
        result = self.message
        if self.file_path:
            result = f"解析文件 '{self.file_path}' 时发生错误: {result}"
        if self.line_number:
            result += f" (第{self.line_number}行)"
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        return result


class AnalysisError(FuckUCodeException):
    """
    分析错误
    
    在代码质量分析过程中发生的错误。
    """
    
    def __init__(
        self, 
        message: str, 
        metric_name: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message, suggestion, "ANALYSIS_ERROR")
        self.metric_name = metric_name
    
    def __str__(self) -> str:
        result = self.message
        if self.metric_name:
            result = f"指标 '{self.metric_name}' 分析时发生错误: {result}"
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        return result


class FileNotFoundError(FuckUCodeException):
    """
    文件不存在错误
    
    当指定的文件或目录不存在时抛出。
    """
    
    def __init__(self, file_path: str):
        message = f"文件或目录不存在: {file_path}"
        suggestion = "请检查路径是否正确，或使用绝对路径"
        super().__init__(message, suggestion, "FILE_NOT_FOUND")
        self.file_path = file_path


class UnsupportedLanguageError(FuckUCodeException):
    """
    不支持的语言错误
    
    当遇到不支持的编程语言时抛出。
    """
    
    def __init__(self, language: str, file_path: Optional[str] = None):
        message = f"不支持的编程语言: {language}"
        suggestion = "请检查文件扩展名，或查看支持的语言列表"
        super().__init__(message, suggestion, "UNSUPPORTED_LANGUAGE")
        self.language = language
        self.file_path = file_path
    
    def __str__(self) -> str:
        result = self.message
        if self.file_path:
            result += f" (文件: {self.file_path})"
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        return result


class ConfigError(FuckUCodeException):
    """
    配置错误
    
    配置文件加载或配置项验证失败时抛出。
    """
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        suggestion = "请检查配置文件格式和配置项的有效性"
        super().__init__(message, suggestion, "CONFIG_ERROR")
        self.config_key = config_key
        self.config_file = config_file
    
    def __str__(self) -> str:
        result = self.message
        if self.config_key:
            result = f"配置项 '{self.config_key}' 错误: {result}"
        if self.config_file:
            result += f" (配置文件: {self.config_file})"
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        return result


class ReportError(FuckUCodeException):
    """
    报告生成错误
    
    在生成分析报告时发生的错误。
    """
    
    def __init__(
        self, 
        message: str, 
        report_format: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message, suggestion, "REPORT_ERROR")
        self.report_format = report_format
    
    def __str__(self) -> str:
        result = self.message
        if self.report_format:
            result = f"生成 {self.report_format} 格式报告时发生错误: {result}"
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        return result


class MetricError(FuckUCodeException):
    """
    指标计算错误
    
    在计算质量指标时发生的错误。
    """
    
    def __init__(
        self, 
        message: str, 
        metric_name: str,
        file_path: Optional[str] = None
    ):
        suggestion = "请检查源代码是否存在语法错误或特殊字符"
        super().__init__(message, suggestion, "METRIC_ERROR")
        self.metric_name = metric_name
        self.file_path = file_path
    
    def __str__(self) -> str:
        result = f"指标 '{self.metric_name}' 计算错误: {self.message}"
        if self.file_path:
            result += f" (文件: {self.file_path})"
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        return result


class PermissionError(FuckUCodeException):
    """
    权限错误
    
    当没有足够权限访问文件或目录时抛出。
    """
    
    def __init__(self, file_path: str, operation: str = "访问"):
        message = f"权限不足，无法{operation}文件: {file_path}"
        suggestion = "请检查文件权限，或使用管理员权限运行"
        super().__init__(message, suggestion, "PERMISSION_ERROR")
        self.file_path = file_path
        self.operation = operation


class MemoryError(FuckUCodeException):
    """
    内存不足错误
    
    当处理大型项目时内存不足抛出。
    """
    
    def __init__(self, operation: str = "代码分析"):
        message = f"内存不足，无法完成{operation}"
        suggestion = "请尝试分析较小的目录，或增加系统内存，或启用内存优化模式"
        super().__init__(message, suggestion, "MEMORY_ERROR")
        self.operation = operation


class TimeoutError(FuckUCodeException):
    """
    超时错误
    
    当操作超时时抛出。
    """
    
    def __init__(self, operation: str, timeout: int):
        message = f"操作超时: {operation} (超时时间: {timeout}秒)"
        suggestion = "请尝试增加超时时间，或检查是否存在死循环"
        super().__init__(message, suggestion, "TIMEOUT_ERROR")
        self.operation = operation
        self.timeout = timeout


# 异常处理工具函数
def handle_file_error(file_path: str, operation: str = "访问") -> None:
    """
    处理文件相关错误的通用函数
    
    Args:
        file_path: 文件路径
        operation: 操作类型
    
    Raises:
        相应的异常类型
    """
    import os
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    
    if not os.access(file_path, os.R_OK):
        raise PermissionError(file_path, operation)


def validate_config(config_dict: dict, required_keys: list) -> None:
    """
    验证配置字典的完整性
    
    Args:
        config_dict: 配置字典
        required_keys: 必需的配置键列表
    
    Raises:
        ConfigError: 当配置不完整时
    """
    missing_keys = [key for key in required_keys if key not in config_dict]
    
    if missing_keys:
        message = f"缺少必需的配置项: {', '.join(missing_keys)}"
        raise ConfigError(message)