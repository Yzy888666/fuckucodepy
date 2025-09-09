"""
CLI接口模块

提供命令行交互界面，是用户与应用程序交互的主要入口。
"""

from .main import main, cli
from .commands import analyze, version
from .options import analysis_options, output_format_options

__all__ = [
    "main",
    "cli", 
    "analyze",
    "version",
    "analysis_options",
    "output_format_options",
]