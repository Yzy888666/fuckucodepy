"""
CLI主入口

定义应用程序的主入口点，初始化CLI框架，设置全局配置。
"""

import sys
import click
from typing import Optional

from .. import __version__
from ..common.exceptions import FuckUCodeException
from .commands import analyze, version


@click.group()
@click.version_option(version=__version__, prog_name="fuck-u-code")
@click.option('--debug', is_flag=True, help='启用调试模式')
@click.option('--config', type=click.Path(exists=True), help='配置文件路径')
@click.pass_context
def cli(ctx, debug: bool, config: Optional[str]):
    """
    🔍 fuck-u-code - 代码质量分析工具
    
    一个专为挖掘"屎山代码"设计的工具，能无情揭露代码的丑陋真相。
    通过七大维度评估代码质量，生成幽默风格的分析报告。
    
    支持的语言: Python, JavaScript, TypeScript, Java, C/C++
    
    示例:
      fuck-u-code analyze                    # 分析当前目录
      fuck-u-code analyze /path/to/project   # 分析指定目录  
      fuck-u-code analyze --verbose          # 详细模式
      fuck-u-code analyze --markdown > report.md  # 生成Markdown报告
    """
    # 确保上下文对象存在
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['config'] = config
    
    if debug:
        click.echo("🐛 调试模式已启用", err=True)


# 注册子命令
cli.add_command(analyze)
cli.add_command(version)


def main():
    """
    主入口函数
    
    处理全局异常和用户中断。
    """
    try:
        cli()
    except FuckUCodeException as e:
        click.echo(f"❌ 错误: {e}", err=True)
        if hasattr(e, 'suggestion') and e.suggestion:
            click.echo(f"💡 建议: {e.suggestion}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n⏹️  操作已取消", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"💥 意外错误: {e}", err=True)
        click.echo("请使用 --debug 选项获取详细错误信息", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()