"""
Python解析器

使用Python内置的ast模块解析Python源代码，提取函数、类、导入等信息。
"""

import ast
import time
from typing import List, Union, Optional, Any
from ..common.constants import LanguageType
from ..common.exceptions import ParseError
from .interfaces import BaseParser
from .models import ParseResult, Function, Class


class PythonParser(BaseParser):
    """
    Python代码解析器
    
    使用ast模块解析Python代码，提取详细的函数和类信息。
    """
    
    def __init__(self):
        super().__init__("PythonParser")
        
        # 复杂度计算的AST节点类型
        self._complexity_nodes = {
            ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler,
            ast.With, ast.Assert, ast.BoolOp, ast.comprehension
        }
    
    def supported_languages(self) -> List[LanguageType]:
        """返回支持的语言类型"""
        return [LanguageType.PYTHON]
    
    def parse(self, file_path: str, content: Union[str, bytes]) -> ParseResult:
        """
        解析Python代码
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            ParseResult: 解析结果
        """
        start_time = time.time()
        
        # 验证和清理内容
        content_str = self.validate_content(content)
        content_str = self.clean_code_content(content_str)
        
        # 创建解析结果对象
        result = ParseResult(
            file_path=file_path,
            language=LanguageType.PYTHON
        )
        
        try:
            # 解析AST
            tree = ast.parse(content_str, filename=file_path)
            result.ast_root = tree
            
            # 统计行数
            result.total_lines, _ = self.count_lines(content_str)
            result.comment_lines = self._count_comment_lines(content_str)
            result.code_lines = result.total_lines - result.comment_lines
            
            # 提取信息
            self._extract_imports(tree, result)
            self._extract_classes_and_functions(tree, result)
            
        except SyntaxError as e:
            error_msg = f"语法错误: {e.msg}"
            if e.lineno:
                error_msg += f" (第{e.lineno}行)"
            result.add_error(error_msg)
            raise ParseError(error_msg, file_path, e.lineno, "请检查Python语法是否正确")
        
        except Exception as e:
            error_msg = f"解析失败: {str(e)}"
            result.add_error(error_msg)
            # 不抛出异常，允许部分解析结果
        
        # 记录解析时间
        result.parse_time = time.time() - start_time
        
        return result
    
    def _extract_imports(self, tree: ast.AST, result: ParseResult) -> None:
        """
        提取导入语句
        
        Args:
            tree: AST根节点
            result: 解析结果对象
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_stmt = f"import {alias.name}"
                    if alias.asname:
                        import_stmt += f" as {alias.asname}"
                    result.import_statements.append(import_stmt)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                level = "." * (node.level or 0)
                
                if node.names[0].name == "*":
                    import_stmt = f"from {level}{module} import *"
                    result.import_statements.append(import_stmt)
                else:
                    for alias in node.names:
                        import_stmt = f"from {level}{module} import {alias.name}"
                        if alias.asname:
                            import_stmt += f" as {alias.asname}"
                        result.import_statements.append(import_stmt)
    
    def _extract_classes_and_functions(self, tree: ast.AST, result: ParseResult) -> None:
        """
        提取类和函数定义
        
        Args:
            tree: AST根节点
            result: 解析结果对象
        """
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                cls = self._parse_class(node)
                result.classes.append(cls)
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = self._parse_function(node)
                result.functions.append(func)
    
    def _parse_class(self, node: ast.ClassDef) -> Class:
        """
        解析类定义
        
        Args:
            node: 类AST节点
            
        Returns:
            Class: 类信息对象
        """
        # 提取基类
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(self._get_full_name(base))
        
        # 创建类对象
        cls = Class(
            name=node.name,
            start_line=node.lineno,
            end_line=self._get_end_line(node),
            base_classes=base_classes,
            docstring=self._extract_docstring(node),
            ast_node=node
        )
        
        # 提取方法
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._parse_function(item, class_name=node.name)
                cls.methods.append(method)
        
        return cls
    
    def _parse_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                       class_name: Optional[str] = None) -> Function:
        """
        解析函数定义
        
        Args:
            node: 函数AST节点
            class_name: 所属类名（如果是方法）
            
        Returns:
            Function: 函数信息对象
        """
        # 基本信息
        func = Function(
            name=node.name,
            start_line=node.lineno,
            end_line=self._get_end_line(node),
            parameters=len(node.args.args),
            docstring=self._extract_docstring(node),
            ast_node=node,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            class_name=class_name
        )
        
        # 计算复杂度
        func.complexity = self._calculate_complexity(node)
        
        # 提取装饰器
        func.decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        
        # 判断可见性
        func.visibility = self._determine_visibility(node.name, func.decorators, class_name)
        
        # 检查是否为生成器
        func.is_generator = self._is_generator(node)
        
        # 提取返回类型注解
        if node.returns:
            func.return_type = self._get_type_annotation(node.returns)
        
        return func
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        计算循环复杂度
        
        基础复杂度为1，每个分支路径+1
        
        Args:
            node: AST节点
            
        Returns:
            int: 复杂度值
        """
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                complexity += 1
                # elif增加复杂度
                complexity += len(child.orelse) if child.orelse and isinstance(child.orelse[0], ast.If) else 0
            
            elif isinstance(child, (ast.While, ast.For)):
                complexity += 1
            
            elif isinstance(child, ast.Try):
                # try-except块
                complexity += len(child.handlers)
                if child.orelse:  # else子句
                    complexity += 1
                if child.finalbody:  # finally子句  
                    complexity += 1
            
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            
            elif isinstance(child, ast.With):
                complexity += 1
            
            elif isinstance(child, ast.BoolOp):
                # and/or操作符
                complexity += len(child.values) - 1
            
            elif isinstance(child, ast.comprehension):
                # 列表推导式
                complexity += 1
                complexity += len(child.ifs)  # if条件
            
            elif isinstance(child, ast.Assert):
                complexity += 1
        
        return complexity
    
    def _extract_docstring(self, node: ast.AST) -> str:
        """
        提取文档字符串
        
        Args:
            node: AST节点
            
        Returns:
            str: 文档字符串
        """
        if (hasattr(node, 'body') and 
            node.body and 
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Str)):
            return node.body[0].value.s
        
        # Python 3.8+
        if (hasattr(node, 'body') and 
            node.body and 
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        
        return ""
    
    def _get_end_line(self, node: ast.AST) -> int:
        """
        获取节点结束行号
        
        Args:
            node: AST节点
            
        Returns:
            int: 结束行号
        """
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno
        
        # 递归查找最大行号
        max_line = node.lineno if hasattr(node, 'lineno') else 0
        
        for child in ast.iter_child_nodes(node):
            if hasattr(child, 'lineno'):
                child_end = self._get_end_line(child)
                max_line = max(max_line, child_end)
        
        return max_line
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """
        获取装饰器名称
        
        Args:
            decorator: 装饰器AST节点
            
        Returns:
            str: 装饰器名称
        """
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return self._get_full_name(decorator)
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        else:
            return str(decorator)
    
    def _get_full_name(self, node: ast.AST) -> str:
        """
        获取属性的完整名称
        
        Args:
            node: AST节点
            
        Returns:
            str: 完整名称
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_full_name(node.value)}.{node.attr}"
        else:
            return str(node)
    
    def _determine_visibility(self, name: str, decorators: List[str], class_name: Optional[str]) -> str:
        """
        判断函数/方法的可见性
        
        Args:
            name: 函数名
            decorators: 装饰器列表
            class_name: 所属类名
            
        Returns:
            str: 可见性级别
        """
        if name.startswith('__') and not name.endswith('__'):
            return "private"
        elif name.startswith('_'):
            return "protected" 
        else:
            return "public"
    
    def _is_generator(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> bool:
        """
        检查函数是否为生成器
        
        Args:
            node: 函数AST节点
            
        Returns:
            bool: 是否为生成器
        """
        for child in ast.walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                return True
        return False
    
    def _get_type_annotation(self, annotation: ast.AST) -> str:
        """
        获取类型注解字符串
        
        Args:
            annotation: 类型注解AST节点
            
        Returns:
            str: 类型注解字符串
        """
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            return self._get_full_name(annotation)
        else:
            return str(annotation)
    
    def _count_comment_lines(self, content: str) -> int:
        """
        统计注释行数
        
        Args:
            content: 文件内容
            
        Returns:
            int: 注释行数
        """
        comment_lines = 0
        in_multiline_string = False
        multiline_delimiter = None
        
        for line in content.splitlines():
            stripped = line.strip()
            
            # 跳过空行
            if not stripped:
                continue
            
            # 检查多行字符串
            if not in_multiline_string:
                # 检查是否开始多行字符串
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    multiline_delimiter = stripped[:3]
                    in_multiline_string = True
                    # 检查是否在同一行结束
                    if stripped.count(multiline_delimiter) >= 2:
                        in_multiline_string = False
                        # 如果这是文档字符串，计为注释
                        comment_lines += 1
                    else:
                        comment_lines += 1
                    continue
                
                # 单行注释
                if stripped.startswith('#'):
                    comment_lines += 1
                    continue
            
            else:
                # 在多行字符串中
                comment_lines += 1
                if multiline_delimiter in stripped:
                    in_multiline_string = False
                    multiline_delimiter = None
        
        return comment_lines