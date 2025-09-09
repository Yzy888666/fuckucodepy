"""
文件工具模块

提供文件和目录操作的工具函数，包括文件搜索、路径处理、模式匹配等。
"""

import os
import fnmatch
import stat
from pathlib import Path
from typing import List, Optional, Iterator, Callable, Tuple
from dataclasses import dataclass

from .constants import DEFAULT_EXCLUDE_PATTERNS
from .exceptions import FileNotFoundError, PermissionError


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    name: str
    size: int
    modified_time: float
    is_directory: bool
    is_text_file: bool


class FileUtils:
    """
    文件操作工具类
    
    提供文件搜索、路径处理、模式匹配等功能。
    """
    
    def __init__(self):
        self._default_excludes = DEFAULT_EXCLUDE_PATTERNS
        
        # 二进制文件扩展名
        self._binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.a', '.lib', '.obj', '.o',
            '.bin', '.dat', '.db', '.sqlite', '.sqlite3',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.class', '.jar', '.war', '.ear',
            '.pyc', '.pyo', '.pyd',
        }
    
    def find_source_files(
        self,
        root_path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Iterator[str]:
        """
        搜索源代码文件
        
        Args:
            root_path: 根目录路径
            include_patterns: 包含模式列表
            exclude_patterns: 排除模式列表
            progress_callback: 进度回调函数
            
        Yields:
            str: 找到的源文件路径
            
        Raises:
            FileNotFoundError: 根目录不存在
            PermissionError: 权限不足
        """
        if not os.path.exists(root_path):
            raise FileNotFoundError(root_path)
        
        if not os.access(root_path, os.R_OK):
            raise PermissionError(root_path, "访问")
        
        # 合并排除模式
        all_excludes = (exclude_patterns or []) + self._default_excludes
        
        # 如果是单个文件
        if os.path.isfile(root_path):
            if self._should_include_file(root_path, include_patterns, all_excludes):
                yield root_path
            return
        
        # 遍历目录
        for root, dirs, files in os.walk(root_path):
            # 过滤目录，修改dirs列表会影响后续遍历
            dirs[:] = [d for d in dirs if not self._should_exclude_dir(
                os.path.join(root, d), all_excludes
            )]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if progress_callback:
                    progress_callback(file_path)
                
                if self._should_include_file(file_path, include_patterns, all_excludes):
                    yield file_path
    
    def _should_include_file(
        self,
        file_path: str,
        include_patterns: Optional[List[str]],
        exclude_patterns: List[str]
    ) -> bool:
        """
        判断文件是否应该包含在结果中
        
        Args:
            file_path: 文件路径
            include_patterns: 包含模式
            exclude_patterns: 排除模式
            
        Returns:
            bool: 是否应该包含
        """
        # 检查是否为文本文件
        if not self.is_text_file(file_path):
            return False
        
        # 标准化路径
        normalized_path = os.path.normpath(file_path)
        
        # 检查排除模式
        if self._matches_patterns(normalized_path, exclude_patterns):
            return False
        
        # 检查包含模式
        if include_patterns:
            return self._matches_patterns(normalized_path, include_patterns)
        
        return True
    
    def _should_exclude_dir(self, dir_path: str, exclude_patterns: List[str]) -> bool:
        """
        判断目录是否应该排除
        
        Args:
            dir_path: 目录路径
            exclude_patterns: 排除模式
            
        Returns:
            bool: 是否应该排除
        """
        normalized_path = os.path.normpath(dir_path)
        return self._matches_patterns(normalized_path, exclude_patterns)
    
    def _matches_patterns(self, path: str, patterns: List[str]) -> bool:
        """
        检查路径是否匹配任一模式
        
        Args:
            path: 文件或目录路径
            patterns: 模式列表
            
        Returns:
            bool: 是否匹配
        """
        for pattern in patterns:
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
        return False
    
    def is_text_file(self, file_path: str) -> bool:
        """
        判断文件是否为文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为文本文件
        """
        try:
            # 检查文件扩展名
            _, ext = os.path.splitext(file_path)
            if ext.lower() in self._binary_extensions:
                return False
            
            # 检查文件大小（跳过过大的文件）
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return False
            
            # 检查文件内容（采样检查）
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)  # 读取前8KB
                if b'\0' in chunk:  # 包含空字节，可能是二进制文件
                    return False
                
                # 检查文本字符比例
                text_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13])
                if len(chunk) > 0 and text_chars / len(chunk) < 0.7:
                    return False
            
            return True
            
        except (OSError, UnicodeDecodeError, PermissionError):
            return False
    
    def get_file_info(self, file_path: str) -> FileInfo:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            FileInfo: 文件信息对象
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        
        stat_result = os.stat(file_path)
        
        return FileInfo(
            path=file_path,
            name=os.path.basename(file_path),
            size=stat_result.st_size,
            modified_time=stat_result.st_mtime,
            is_directory=stat.S_ISDIR(stat_result.st_mode),
            is_text_file=self.is_text_file(file_path) if not stat.S_ISDIR(stat_result.st_mode) else False
        )
    
    def read_file_content(self, file_path: str) -> str:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件内容
            
        Raises:
            FileNotFoundError: 文件不存在
            PermissionError: 权限不足
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(file_path, "读取")
        
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用errors='ignore'
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
        except OSError as e:
            raise PermissionError(file_path, "读取") from e
    
    def normalize_path(self, path: str) -> str:
        """
        标准化路径
        
        Args:
            path: 原始路径
            
        Returns:
            str: 标准化后的路径
        """
        return os.path.normpath(os.path.abspath(path))
    
    def get_relative_path(self, file_path: str, base_path: str) -> str:
        """
        获取相对路径
        
        Args:
            file_path: 文件路径
            base_path: 基础路径
            
        Returns:
            str: 相对路径
        """
        try:
            return os.path.relpath(file_path, base_path)
        except ValueError:
            # 在Windows上，不同盘符的路径无法计算相对路径
            return file_path
    
    def count_lines(self, content: str) -> Tuple[int, int]:
        """
        统计代码行数
        
        Args:
            content: 文件内容
            
        Returns:
            Tuple[int, int]: (总行数, 非空行数)
        """
        lines = content.splitlines()
        total_lines = len(lines)
        non_empty_lines = sum(1 for line in lines if line.strip())
        
        return total_lines, non_empty_lines
    
    def extract_imports(self, content: str, language: str) -> List[str]:
        """
        提取导入语句
        
        Args:
            content: 文件内容
            language: 编程语言
            
        Returns:
            List[str]: 导入语句列表
        """
        import re
        
        imports = []
        lines = content.splitlines()
        
        if language == 'python':
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
        elif language in ['javascript', 'typescript']:
            for line in lines:
                line = line.strip()
                # import ... from ...
                import_match = re.match(r'import\s+.*\s+from\s+["\']([^"\']+)["\']', line)
                if import_match:
                    imports.append(line)
                # require(...)
                require_match = re.match(r'.*require\s*\(\s*["\']([^"\']+)["\']\s*\)', line)
                if require_match:
                    imports.append(line)
        elif language == 'java':
            for line in lines:
                line = line.strip()
                if line.startswith('import '):
                    imports.append(line)
        
        return imports
    
    def add_binary_extension(self, extension: str) -> None:
        """
        添加二进制文件扩展名
        
        Args:
            extension: 文件扩展名（包含点号）
        """
        self._binary_extensions.add(extension.lower())
    
    def remove_binary_extension(self, extension: str) -> None:
        """
        移除二进制文件扩展名
        
        Args:
            extension: 文件扩展名（包含点号）
        """
        self._binary_extensions.discard(extension.lower())