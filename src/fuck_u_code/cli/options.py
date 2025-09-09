"""
通用CLI选项定义

定义可重用的命令行选项，确保一致性和可维护性。
"""

import click
from functools import update_wrapper
from typing import Callable


def analysis_options(f: Callable) -> Callable:
    """
    分析相关选项组装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        Callable: 装饰后的函数
    """
    # 按逆序添加选项，因为装饰器是从下往上执行的
    f = click.option(
        '--exclude', '-e',
        multiple=True,
        help='排除文件/目录模式 (可多次使用)，支持通配符'
    )(f)
    
    f = click.option(
        '--include',
        multiple=True, 
        help='包含文件/目录模式 (可多次使用)，支持通配符'
    )(f)
    
    f = click.option(
        '--issues', '-i',
        type=click.IntRange(1, 50),
        default=5,
        help='每个文件显示的最大问题数 (1-50)'
    )(f)
    
    f = click.option(
        '--top', '-t',
        type=click.IntRange(1, 100),
        default=5,
        help='显示问题最多的前N个文件 (1-100)'
    )(f)
    
    return f


def output_format_options(f: Callable) -> Callable:
    """
    输出格式选项组装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        Callable: 装饰后的函数
    """
    f = click.option(
        '--json',
        'output_json',
        is_flag=True,
        help='输出JSON格式报告'
    )(f)
    
    f = click.option(
        '--markdown', '-m',
        'output_markdown', 
        is_flag=True,
        help='输出Markdown格式报告'
    )(f)
    
    return f


def verbose_option(f: Callable) -> Callable:
    """
    详细输出选项装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        Callable: 装饰后的函数
    """
    def callback(ctx, param, value):
        ctx.ensure_object(dict)
        ctx.obj['verbose'] = value
        return value
    
    return click.option(
        '--verbose', '-v',
        is_flag=True,
        expose_value=False,
        callback=callback,
        help='显示详细分析信息'
    )(f)


def progress_option(f: Callable) -> Callable:
    """
    进度显示选项装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        Callable: 装饰后的函数
    """
    return click.option(
        '--silent',
        is_flag=True,
        help='静默模式，不显示进度信息'
    )(f)


def language_option(f: Callable) -> Callable:
    """
    语言选择选项装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        Callable: 装饰后的函数
    """
    return click.option(
        '--lang', '-l',
        type=click.Choice(['zh-CN', 'en-US']),
        default='zh-CN',
        help='界面语言'
    )(f)