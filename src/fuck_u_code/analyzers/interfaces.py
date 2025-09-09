"""
分析器接口定义

定义代码分析器的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from .models import AnalysisResult, AnalysisConfig


class Analyzer(ABC):
    """
    代码分析器抽象接口
    
    所有代码分析器都应该实现这个接口。
    """
    
    @abstractmethod
    def analyze(
        self, 
        path: str, 
        config: Optional[AnalysisConfig] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> AnalysisResult:
        """
        分析指定路径的代码
        
        Args:
            path: 文件或目录路径
            config: 分析配置
            progress_callback: 进度回调函数 (message, progress)
            
        Returns:
            AnalysisResult: 分析结果
        """
        pass
    
    @abstractmethod
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            AnalysisResult: 分析结果
        """
        pass
    
    def analyze_with_excludes(
        self,
        path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> AnalysisResult:
        """
        使用包含/排除模式分析代码
        
        Args:
            path: 文件或目录路径
            include_patterns: 包含模式列表
            exclude_patterns: 排除模式列表
            progress_callback: 进度回调函数
            
        Returns:
            AnalysisResult: 分析结果
        """
        config = AnalysisConfig(
            target_path=path,
            include_patterns=include_patterns or [],
            exclude_patterns=exclude_patterns or []
        )
        return self.analyze(path, config, progress_callback)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        返回分析器名称
        
        Returns:
            str: 分析器名称
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """
        返回分析器版本
        
        Returns:
            str: 版本号
        """
        pass