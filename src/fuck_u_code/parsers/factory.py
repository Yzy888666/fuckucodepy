"""
解析器工厂

根据文件类型和语言自动创建相应的解析器。
"""

from typing import Dict, Optional, Type, List
from ..common.constants import LanguageType
from ..common.language_detector import LanguageDetector
from ..common.exceptions import UnsupportedLanguageError
from .interfaces import Parser
from .python_parser import PythonParser


class ParserFactory:
    """
    解析器工厂类
    
    根据语言类型创建相应的解析器实例。
    """
    
    def __init__(self):
        self._parsers: Dict[LanguageType, Type[Parser]] = {}
        self._instances: Dict[LanguageType, Parser] = {}
        self._language_detector = LanguageDetector()
        
        # 注册内置解析器
        self._register_builtin_parsers()
    
    def _register_builtin_parsers(self) -> None:
        """注册内置解析器"""
        self.register_parser(LanguageType.PYTHON, PythonParser)
        
        # TODO: 注册其他语言解析器
        # self.register_parser(LanguageType.JAVASCRIPT, JavaScriptParser)
        # self.register_parser(LanguageType.TYPESCRIPT, TypeScriptParser)
        # self.register_parser(LanguageType.JAVA, JavaParser)
        # self.register_parser(LanguageType.C, CParser)
        # self.register_parser(LanguageType.CPP, CppParser)
    
    def register_parser(self, language: LanguageType, parser_class: Type[Parser]) -> None:
        """
        注册解析器
        
        Args:
            language: 语言类型
            parser_class: 解析器类
        """
        self._parsers[language] = parser_class
    
    def create_parser(self, language: LanguageType) -> Parser:
        """
        创建解析器实例
        
        Args:
            language: 语言类型
            
        Returns:
            Parser: 解析器实例
            
        Raises:
            UnsupportedLanguageError: 不支持的语言类型
        """
        if language not in self._parsers:
            raise UnsupportedLanguageError(language.value)
        
        # 使用单例模式，避免重复创建
        if language not in self._instances:
            parser_class = self._parsers[language]
            self._instances[language] = parser_class()
        
        return self._instances[language]
    
    def create_parser_for_file(self, file_path: str) -> Parser:
        """
        为指定文件创建解析器
        
        Args:
            file_path: 文件路径
            
        Returns:
            Parser: 解析器实例
            
        Raises:
            UnsupportedLanguageError: 不支持的文件类型
        """
        language = self._language_detector.detect_language(file_path)
        
        if language == LanguageType.UNSUPPORTED:
            raise UnsupportedLanguageError("未知", file_path)
        
        return self.create_parser(language)
    
    def is_supported_language(self, language: LanguageType) -> bool:
        """
        检查是否支持指定语言
        
        Args:
            language: 语言类型
            
        Returns:
            bool: 是否支持
        """
        return language in self._parsers
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        检查是否支持指定文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持
        """
        try:
            language = self._language_detector.detect_language(file_path)
            return self.is_supported_language(language)
        except UnsupportedLanguageError:
            return False
    
    def get_supported_languages(self) -> List[LanguageType]:
        """
        获取支持的语言列表
        
        Returns:
            list[LanguageType]: 支持的语言列表
        """
        return list(self._parsers.keys())
    
    def get_parser_info(self, language: LanguageType) -> Optional[str]:
        """
        获取解析器信息
        
        Args:
            language: 语言类型
            
        Returns:
            Optional[str]: 解析器名称，如果不支持则返回None
        """
        if language in self._parsers:
            parser = self.create_parser(language)
            return parser.name
        return None
    
    def clear_cache(self) -> None:
        """清理解析器实例缓存"""
        self._instances.clear()


# 全局工厂实例
_parser_factory = ParserFactory()


def get_parser_factory() -> ParserFactory:
    """
    获取全局解析器工厂实例
    
    Returns:
        ParserFactory: 工厂实例
    """
    return _parser_factory


def create_parser(language: LanguageType) -> Parser:
    """
    创建解析器的便捷函数
    
    Args:
        language: 语言类型
        
    Returns:
        Parser: 解析器实例
    """
    return _parser_factory.create_parser(language)


def create_parser_for_file(file_path: str) -> Parser:
    """
    为文件创建解析器的便捷函数
    
    Args:
        file_path: 文件路径
        
    Returns:
        Parser: 解析器实例
    """
    return _parser_factory.create_parser_for_file(file_path)