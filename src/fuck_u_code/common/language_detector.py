"""
语言检测器模块

根据文件扩展名和内容特征检测编程语言类型。
"""

import os
import re
from typing import Optional
from .constants import LanguageType, FILE_EXTENSIONS
from .exceptions import UnsupportedLanguageError


class LanguageDetector:
    """
    编程语言检测器
    
    根据文件扩展名和内容特征自动检测编程语言类型。
    """
    
    def __init__(self):
        self._extension_map = FILE_EXTENSIONS
        
        # 特殊文件名模式
        self._special_patterns = {
            r'.*\.d\.ts$': LanguageType.TYPESCRIPT,  # TypeScript声明文件
            r'.*\.test\.js$': LanguageType.JAVASCRIPT,
            r'.*\.spec\.js$': LanguageType.JAVASCRIPT,
            r'.*\.test\.ts$': LanguageType.TYPESCRIPT,
            r'.*\.spec\.ts$': LanguageType.TYPESCRIPT,
            r'.*\.stories\.js$': LanguageType.JAVASCRIPT,
            r'.*\.stories\.ts$': LanguageType.TYPESCRIPT,
        }
        
        # 内容检测模式
        self._content_patterns = {
            LanguageType.TYPESCRIPT: [
                r'import\s+.*\s+from\s+["\'].*["\'];',
                r'interface\s+\w+\s*{',
                r'type\s+\w+\s*=',
                r':\s*(string|number|boolean|any)\s*[,;=)]',
            ],
            LanguageType.JAVASCRIPT: [
                r'function\s+\w+\s*\(',
                r'const\s+\w+\s*=\s*\(',
                r'require\s*\(\s*["\'].*["\']\s*\)',
                r'module\.exports\s*=',
            ],
            LanguageType.PYTHON: [
                r'def\s+\w+\s*\(',
                r'class\s+\w+.*:',
                r'import\s+\w+',
                r'from\s+\w+\s+import',
            ],
        }
    
    def detect_language(self, file_path: str) -> LanguageType:
        """
        检测文件的编程语言类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            LanguageType: 检测到的语言类型
            
        Raises:
            UnsupportedLanguageError: 不支持的语言类型
        """
        # 1. 基于特殊文件名模式检测
        for pattern, language in self._special_patterns.items():
            if re.match(pattern, file_path, re.IGNORECASE):
                return language
        
        # 2. 基于文件扩展名检测
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in self._extension_map:
            base_language = self._extension_map[ext]
            
            # 对于.js文件，尝试通过内容判断是否为TypeScript
            if base_language == LanguageType.JAVASCRIPT:
                content_language = self._detect_by_content(file_path)
                if content_language == LanguageType.TYPESCRIPT:
                    return LanguageType.TYPESCRIPT
            
            return base_language
        
        # 3. 基于内容检测
        content_language = self._detect_by_content(file_path)
        if content_language != LanguageType.UNSUPPORTED:
            return content_language
        
        # 4. 特殊文件名处理
        filename = os.path.basename(file_path).lower()
        if filename in ['makefile', 'dockerfile', 'rakefile']:
            return LanguageType.UNSUPPORTED
        
        return LanguageType.UNSUPPORTED
    
    def _detect_by_content(self, file_path: str) -> LanguageType:
        """
        基于文件内容检测语言类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            LanguageType: 检测到的语言类型
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 只读取前几行进行检测，提高性能
                content = ''
                for i, line in enumerate(f):
                    if i >= 50:  # 只检测前50行
                        break
                    content += line
                
                return self._analyze_content(content)
                
        except (OSError, UnicodeDecodeError):
            # 文件读取失败，返回不支持
            return LanguageType.UNSUPPORTED
    
    def _analyze_content(self, content: str) -> LanguageType:
        """
        分析文件内容确定语言类型
        
        Args:
            content: 文件内容
            
        Returns:
            LanguageType: 检测到的语言类型
        """
        scores = {}
        
        for language, patterns in self._content_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                score += len(matches)
            scores[language] = score
        
        # 返回得分最高的语言类型
        if scores:
            max_language = max(scores, key=scores.get)
            if scores[max_language] > 0:
                return max_language
        
        return LanguageType.UNSUPPORTED
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        检查文件是否为支持的代码文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否支持
        """
        try:
            language = self.detect_language(file_path)
            return language != LanguageType.UNSUPPORTED
        except UnsupportedLanguageError:
            return False
    
    def get_supported_extensions(self) -> list:
        """
        获取支持的文件扩展名列表
        
        Returns:
            list: 支持的扩展名列表
        """
        return list(self._extension_map.keys())
    
    def add_extension_mapping(self, extension: str, language: LanguageType) -> None:
        """
        添加自定义扩展名映射
        
        Args:
            extension: 文件扩展名（包含点号，如.py）
            language: 对应的语言类型
        """
        self._extension_map[extension.lower()] = language
    
    def add_content_pattern(self, language: LanguageType, pattern: str) -> None:
        """
        添加自定义内容检测模式
        
        Args:
            language: 语言类型
            pattern: 正则表达式模式
        """
        if language not in self._content_patterns:
            self._content_patterns[language] = []
        self._content_patterns[language].append(pattern)