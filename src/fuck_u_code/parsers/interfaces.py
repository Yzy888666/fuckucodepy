"""
解析器接口定义

定义代码解析器的抽象接口和基础实现。
"""

from abc import ABC, abstractmethod
from typing import List, Union, Tuple
from ..common.constants import LanguageType
from .models import ParseResult


class Parser(ABC):
    """
    代码解析器抽象接口
    
    所有语言解析器都应该实现这个接口。
    """
    
    @abstractmethod
    def parse(self, file_path: str, content: Union[str, bytes]) -> ParseResult:
        """
        解析代码内容
        
        Args:
            file_path: 文件路径（用于错误报告）
            content: 文件内容
            
        Returns:
            ParseResult: 解析结果
            
        Raises:
            ParseError: 解析失败时抛出
        """
        pass
    
    @abstractmethod
    def supported_languages(self) -> List[LanguageType]:
        """
        返回支持的语言类型列表
        
        Returns:
            List[LanguageType]: 支持的语言类型
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        返回解析器名称
        
        Returns:
            str: 解析器名称
        """
        pass
    
    def can_parse(self, language: LanguageType) -> bool:
        """
        检查是否支持指定语言
        
        Args:
            language: 语言类型
            
        Returns:
            bool: 是否支持
        """
        return language in self.supported_languages()
    
    def validate_content(self, content: Union[str, bytes]) -> str:
        """
        验证和转换内容格式
        
        Args:
            content: 原始内容
            
        Returns:
            str: 转换后的字符串内容
        """
        if isinstance(content, bytes):
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
            for encoding in encodings:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            # 如果都失败，使用utf-8并忽略错误
            return content.decode('utf-8', errors='ignore')
        
        return content


class BaseParser(Parser):
    """
    基础解析器实现
    
    提供所有解析器的通用功能。
    """
    
    def __init__(self, name: str):
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    def count_lines(self, content: str) -> Tuple[int, int]:
        """
        统计代码行数
        
        Args:
            content: 文件内容
            
        Returns:
            tuple[int, int]: (总行数, 非空行数)
        """
        lines = content.splitlines()
        total_lines = len(lines)
        non_empty_lines = sum(1 for line in lines if line.strip())
        return total_lines, non_empty_lines
    
    def extract_docstring(self, node) -> str:
        """
        提取文档字符串
        
        Args:
            node: AST节点
            
        Returns:
            str: 文档字符串，如果没有则返回空字符串
        """
        # 这个方法需要在具体的解析器中实现
        return ""
    
    def calculate_basic_complexity(self, node) -> int:
        """
        计算基础循环复杂度
        
        Args:
            node: AST节点
            
        Returns:
            int: 复杂度值
        """
        # 这个方法需要在具体的解析器中实现
        return 1
    
    def detect_encoding(self, content: bytes) -> str:
        """
        检测文件编码
        
        Args:
            content: 文件二进制内容
            
        Returns:
            str: 检测到的编码
        """
        # 简单的编码检测
        try:
            content.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            pass
        
        try:
            content.decode('gbk')
            return 'gbk'
        except UnicodeDecodeError:
            pass
        
        return 'latin1'  # 默认编码
    
    def clean_code_content(self, content: str) -> str:
        """
        清理代码内容
        
        Args:
            content: 原始内容
            
        Returns:
            str: 清理后的内容
        """
        # 移除BOM标记
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # 统一换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        return content