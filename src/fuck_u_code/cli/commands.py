"""
CLI命令定义

实现具体的CLI命令，包括analyze和version命令。
"""

import os
import sys
import click
from typing import List, Optional, Tuple

from .. import __version__
from ..analyzers.code_analyzer import CodeAnalyzer
from ..analyzers.models import AnalysisConfig
from ..reports.terminal_reporter import TerminalReporter
from ..reports.markdown_reporter import MarkdownReporter
from ..common.constants import DetailLevel
from ..common.exceptions import AnalysisError, FileNotFoundError
from .options import analysis_options, output_format_options, progress_option, language_option


@click.command()
@click.argument(
    'path',
    type=click.Path(exists=True),
    default='.',
    metavar='[PATH]'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='显示详细分析报告，包含具体问题和建议'
)
@click.option(
    '--summary', '-s', 
    is_flag=True,
    help='只显示总结信息，不显示详细内容'
)
@output_format_options
@analysis_options
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='输出报告到指定文件'
)
@progress_option
@language_option
@click.option(
    '--max-files',
    type=click.IntRange(1, 1000),
    help='限制分析的最大文件数'
)
@click.option(
    '--timeout',
    type=click.IntRange(10, 3600),
    default=300,
    help='分析超时时间（秒）'
)
@click.pass_context
def analyze(
    ctx,
    path: str,
    verbose: bool,
    summary: bool, 
    output_markdown: bool,
    output_json: bool,
    top: int,
    issues: int,
    exclude: Tuple[str, ...],
    include: Tuple[str, ...],
    output: Optional[str],
    silent: bool,
    lang: str,
    max_files: Optional[int],
    timeout: int
):
    """
    分析指定路径的代码质量
    
    PATH: 要分析的文件或目录路径 (默认为当前目录)
    
    这个工具会分析你的代码并给出质量评分，分数越高说明代码越"屎山"。
    我们使用七大维度来评估代码质量：循环复杂度、函数长度、注释覆盖率、
    错误处理、命名规范、代码重复度和代码结构。
    
    示例:
    
      \b
      # 分析当前目录
      fuck-u-code analyze
      
      # 分析指定目录，显示详细信息
      fuck-u-code analyze /path/to/project --verbose
      
      # 生成Markdown报告
      fuck-u-code analyze --markdown > report.md
      
      # 排除特定目录和文件
      fuck-u-code analyze --exclude "*/test/*" --exclude "*.min.js"
      
      # 只显示前3个问题最多的文件
      fuck-u-code analyze --top 3 --summary
    """
    # 参数验证
    if summary and verbose:
        raise click.UsageError("--summary 和 --verbose 不能同时使用")
    
    output_formats = [output_markdown, output_json]
    if sum(output_formats) > 1:
        raise click.UsageError("只能选择一种输出格式")
    
    # 确定输出格式
    if output_markdown:
        output_format = "markdown"
    elif output_json:
        output_format = "json"
    else:
        output_format = "terminal"
    
    # 构建分析配置
    detail_level = DetailLevel.SUMMARY if summary else (DetailLevel.VERBOSE if verbose else DetailLevel.NORMAL)
    
    config = AnalysisConfig(
        target_path=path,
        include_patterns=list(include) if include else [],
        exclude_patterns=list(exclude) if exclude else [],
        detail_level=detail_level,
        max_files=max_files,
        timeout=timeout,
        language=lang,
        parallel=True  # 默认启用并行处理
    )
    
    # 进度回调函数
    progress_callback = None
    if not silent and output_format == "terminal":
        def progress_callback(message: str, progress: float):
            # 简单的进度显示
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            click.echo(f"\r{message} [{bar}] {progress*100:.1f}%", nl=False, err=True)
            if progress >= 1.0:
                click.echo("", err=True)  # 换行
    
    try:
        # 执行分析
        if not silent:
            click.echo("🚀 开始代码质量分析...", err=True)
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(path, config, progress_callback)
        
        if not silent:
            click.echo("✅ 分析完成！", err=True)
        
        # 生成报告
        report_content = _generate_report(result, output_format, verbose, summary, top, issues)
        
        # 输出结果
        if output:
            _save_report(report_content, output, output_format)
            if not silent:
                click.echo(f"📄 报告已保存到: {output}", err=True)
        else:
            click.echo(report_content)
        
        # 根据代码质量确定退出码
        if result.overall_score > 80:
            sys.exit(2)  # 代码质量极差
        elif result.overall_score > 50:
            sys.exit(1)  # 代码质量较差
        else:
            sys.exit(0)  # 代码质量可接受
            
    except FileNotFoundError as e:
        raise click.ClickException(f"文件或目录不存在: {e.file_path}")
    except AnalysisError as e:
        raise click.ClickException(f"分析失败: {e}")
    except Exception as e:
        if ctx.obj.get('debug'):
            raise
        raise click.ClickException(f"分析过程发生错误: {e}")


@click.command()
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='显示详细版本信息，包括依赖库版本'
)
def version(verbose: bool):
    """
    显示版本信息
    
    显示fuck-u-code的版本号和相关信息。
    """
    click.echo(f"fuck-u-code version {__version__}")
    
    if verbose:
        click.echo(f"Python: {sys.version}")
        
        # 显示关键依赖版本
        dependencies = _get_dependency_versions()
        if dependencies:
            click.echo("\n依赖库版本:")
            for lib, ver in dependencies.items():
                click.echo(f"  {lib}: {ver}")


def _generate_report(
    result,
    output_format: str,
    verbose: bool,
    summary: bool,
    max_files: int,
    max_issues: int
) -> str:
    """
    生成报告内容
    
    Args:
        result: 分析结果
        output_format: 输出格式
        verbose: 是否详细模式
        summary: 是否摘要模式
        max_files: 最大文件数
        max_issues: 最大问题数
        
    Returns:
        str: 报告内容
    """
    if output_format == "markdown":
        reporter = MarkdownReporter(max_files=max_files, max_issues_per_file=max_issues)
        return reporter.generate(result)
    
    elif output_format == "json":
        import json
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    
    else:  # terminal
        reporter = TerminalReporter(max_files=max_files, max_issues_per_file=max_issues)
        return reporter.generate(result, verbose=verbose, summary=summary)


def _save_report(content: str, output_path: str, output_format: str) -> None:
    """
    保存报告到文件
    
    Args:
        content: 报告内容
        output_path: 输出路径
        output_format: 输出格式
    """
    try:
        # 确保目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except OSError as e:
        raise click.ClickException(f"无法保存报告: {e}")


def _get_dependency_versions() -> dict:
    """
    获取关键依赖库的版本信息
    
    Returns:
        dict: 依赖库版本字典
    """
    dependencies = {}
    
    try:
        import rich
        dependencies['rich'] = rich.__version__
    except (ImportError, AttributeError):
        dependencies['rich'] = "未安装"
    
    try:
        import click
        dependencies['click'] = click.__version__
    except (ImportError, AttributeError):
        dependencies['click'] = "未安装"
    
    try:
        import yaml
        dependencies['pyyaml'] = yaml.__version__
    except (ImportError, AttributeError):
        dependencies['pyyaml'] = "未安装"
    
    return dependencies