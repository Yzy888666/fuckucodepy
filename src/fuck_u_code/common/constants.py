"""
常量定义模块

定义项目中使用的各种常量，包括支持的编程语言、质量等级、默认配置等。
"""

from enum import Enum
from typing import Dict, List


class LanguageType(Enum):
    """支持的编程语言类型"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    UNSUPPORTED = "unsupported"


class QualityLevel(Enum):
    """代码质量等级"""
    EXCELLENT = "excellent"      # 清新可人
    GOOD = "good"               # 偶有异味
    AVERAGE = "average"         # 微臭青年
    POOR = "poor"              # 屎气扑鼻
    BAD = "bad"                # 中度屎山
    TERRIBLE = "terrible"       # 隐性毒瘤
    HORRIBLE = "horrible"       # 重度屎山
    DISASTER = "disaster"       # 代码化尸场
    NUCLEAR = "nuclear"         # 核平级灾难
    LEGENDARY = "legendary"     # 祖传老屎
    ULTIMATE = "ultimate"       # 终极屎王


class ReportFormat(Enum):
    """报告输出格式"""
    TERMINAL = "terminal"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


class DetailLevel(Enum):
    """详细程度级别"""
    SUMMARY = "summary"
    NORMAL = "normal"
    VERBOSE = "verbose"


# 文件扩展名到语言类型的映射
FILE_EXTENSIONS = {
    # Python
    '.py': LanguageType.PYTHON,
    '.pyw': LanguageType.PYTHON,
    '.pyi': LanguageType.PYTHON,
    
    # JavaScript
    '.js': LanguageType.JAVASCRIPT,
    '.jsx': LanguageType.JAVASCRIPT,
    '.mjs': LanguageType.JAVASCRIPT,
    
    # TypeScript
    '.ts': LanguageType.TYPESCRIPT,
    '.tsx': LanguageType.TYPESCRIPT,
    
    # Java
    '.java': LanguageType.JAVA,
    
    # C/C++
    '.c': LanguageType.C,
    '.h': LanguageType.C,
    '.cpp': LanguageType.CPP,
    '.cxx': LanguageType.CPP,
    '.cc': LanguageType.CPP,
    '.hpp': LanguageType.CPP,
    '.hxx': LanguageType.CPP,
    
    # Go
    '.go': LanguageType.GO,
    
    # Rust
    '.rs': LanguageType.RUST,
}

# 默认排除的目录和文件模式
DEFAULT_EXCLUDE_PATTERNS = [
    "*/node_modules/*",
    "*/vendor/*",
    "*/.git/*",
    "*/.svn/*",
    "*/.hg/*",
    "*/venv/*",
    "*/env/*",
    "*/__pycache__/*",
    "*/build/*",
    "*/dist/*",
    "*/target/*",
    "*/bin/*",
    "*/obj/*",
    "*/.idea/*",
    "*/.vscode/*",
    "*/coverage/*",
    "*/htmlcov/*",
    "*/.pytest_cache/*",
    "*/.mypy_cache/*",
    "*/.tox/*",
    "*/test_*",
    "*/tests/*",
    "*_test.py",
    "*_test.js",
    "*Test.java",
]

# 质量等级阈值配置
QUALITY_THRESHOLDS = [
    (0, 5, QualityLevel.EXCELLENT),
    (5, 15, QualityLevel.GOOD),
    (15, 25, QualityLevel.AVERAGE),
    (25, 40, QualityLevel.POOR),
    (40, 55, QualityLevel.BAD),
    (55, 65, QualityLevel.TERRIBLE),
    (65, 75, QualityLevel.HORRIBLE),
    (75, 85, QualityLevel.DISASTER),
    (85, 95, QualityLevel.NUCLEAR),
    (95, 100, QualityLevel.LEGENDARY),
    (100, float('inf'), QualityLevel.ULTIMATE),
]

# 指标权重配置（默认值）
DEFAULT_METRIC_WEIGHTS = {
    "complexity": 0.30,         # 循环复杂度 30%
    "function_length": 0.20,    # 函数长度 20%
    "comment_ratio": 0.15,      # 注释覆盖率 15%
    "error_handling": 0.15,     # 错误处理 15%
    "naming_convention": 0.10,  # 命名规范 10%
    "code_duplication": 0.05,   # 代码重复度 5%
    "structure_analysis": 0.05, # 代码结构 5%
}

# 单行注释模式
SINGLE_LINE_COMMENT_PATTERNS = {
    LanguageType.PYTHON: ["#"],
    LanguageType.JAVASCRIPT: ["//"],
    LanguageType.TYPESCRIPT: ["//"],
    LanguageType.JAVA: ["//"],
    LanguageType.C: ["//"],
    LanguageType.CPP: ["//"],
    LanguageType.GO: ["//"],
    LanguageType.RUST: ["//"],
}

# 多行注释模式
MULTI_LINE_COMMENT_PATTERNS = {
    LanguageType.PYTHON: [('"""', '"""'), ("'''", "'''")],
    LanguageType.JAVASCRIPT: [("/*", "*/")],
    LanguageType.TYPESCRIPT: [("/*", "*/")],
    LanguageType.JAVA: [("/*", "*/")],
    LanguageType.C: [("/*", "*/")],
    LanguageType.CPP: [("/*", "*/")],
    LanguageType.GO: [("/*", "*/")],
    LanguageType.RUST: [("/*", "*/")],
}

# 函数长度阈值
FUNCTION_LENGTH_THRESHOLDS = {
    "excellent": 20,
    "good": 40,
    "average": 70,
    "poor": 120,
}

# 参数数量阈值
PARAMETER_COUNT_THRESHOLDS = {
    "excellent": 3,
    "good": 5,
    "average": 6,
    "poor": 8,
}

# 循环复杂度阈值
COMPLEXITY_THRESHOLDS = {
    "excellent": 5,
    "good": 10,
    "average": 15,
    "poor": 20,
}

# 注释覆盖率阈值
COMMENT_RATIO_THRESHOLDS = {
    "optimal_min": 0.15,  # 最佳注释率下限 15%
    "optimal_max": 0.25,  # 最佳注释率上限 25%
    "minimum": 0.10,      # 最低可接受注释率 10%
}

# 默认配置
DEFAULT_CONFIG = {
    "language": "zh-CN",
    "output_format": ReportFormat.TERMINAL,
    "detail_level": DetailLevel.NORMAL,
    "show_progress": True,
    "max_files_display": 10,
    "max_issues_per_file": 5,
    "metric_weights": DEFAULT_METRIC_WEIGHTS,
    "exclude_patterns": DEFAULT_EXCLUDE_PATTERNS,
    "include_patterns": [],
    "skip_index_files": True,
}

# 支持的语言列表
SUPPORTED_LANGUAGES = [
    LanguageType.PYTHON,
    LanguageType.JAVASCRIPT,
    LanguageType.TYPESCRIPT,
    LanguageType.JAVA,
    LanguageType.C,
    LanguageType.CPP,
]

# 版本信息
VERSION = "1.0.0"
USER_AGENT = f"fuck-u-code/{VERSION}"