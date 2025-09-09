# 项目架构与设计文档

## 总体架构设计

### 架构概览

Python版本的fuck-u-code将采用分层架构设计，主要包含以下几个层次：

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI层                                │
│  命令行接口、参数解析、用户交互                               │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                      应用层 (Application)                   │
│  分析流程控制、结果聚合、配置管理                             │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                      业务层 (Business)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │  解析器     │ │  指标系统   │ │  报告系统   │            │
│  │  (Parsers)  │ │  (Metrics)  │ │  (Reports)  │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    基础设施层 (Infrastructure)               │
│  文件操作、语言检测、工具函数、多语言支持                     │
└─────────────────────────────────────────────────────────────┘
```

### 核心设计原则

1. **单一职责原则**: 每个模块只负责一个特定功能
2. **开放封闭原则**: 对扩展开放，对修改封闭
3. **依赖注入**: 通过接口解耦，便于测试和扩展
4. **工厂模式**: 用于创建解析器和指标对象
5. **策略模式**: 不同语言的解析策略

## 目录结构设计

```
python-fuck-u-code/
├── src/
│   ├── fuck_u_code/
│   │   ├── __init__.py
│   │   ├── analyzers/              # 分析器模块
│   │   │   ├── __init__.py
│   │   │   ├── interfaces.py       # 分析器接口定义
│   │   │   ├── base_analyzer.py    # 基础分析器实现
│   │   │   └── code_analyzer.py    # 主要分析器实现
│   │   ├── parsers/                # 解析器模块
│   │   │   ├── __init__.py
│   │   │   ├── interfaces.py       # 解析器接口定义
│   │   │   ├── base_parser.py      # 基础解析器
│   │   │   ├── python_parser.py    # Python解析器
│   │   │   ├── javascript_parser.py # JavaScript解析器
│   │   │   ├── typescript_parser.py # TypeScript解析器
│   │   │   ├── java_parser.py      # Java解析器
│   │   │   ├── c_parser.py         # C/C++解析器
│   │   │   └── factory.py          # 解析器工厂
│   │   ├── metrics/                # 指标系统
│   │   │   ├── __init__.py
│   │   │   ├── interfaces.py       # 指标接口定义
│   │   │   ├── base_metric.py      # 基础指标类
│   │   │   ├── complexity.py       # 循环复杂度
│   │   │   ├── function_length.py  # 函数长度
│   │   │   ├── comment_ratio.py    # 注释覆盖率
│   │   │   ├── error_handling.py   # 错误处理
│   │   │   ├── naming_convention.py # 命名规范
│   │   │   ├── code_duplication.py # 代码重复度
│   │   │   ├── structure_analysis.py # 代码结构
│   │   │   └── factory.py          # 指标工厂
│   │   ├── reports/                # 报告系统
│   │   │   ├── __init__.py
│   │   │   ├── interfaces.py       # 报告接口定义
│   │   │   ├── terminal_reporter.py # 终端报告
│   │   │   ├── markdown_reporter.py # Markdown报告
│   │   │   └── quality_levels.py   # 质量等级定义
│   │   ├── i18n/                   # 国际化
│   │   │   ├── __init__.py
│   │   │   ├── translator.py       # 翻译器
│   │   │   ├── zh_cn.py           # 中文翻译
│   │   │   └── en_us.py           # 英文翻译
│   │   ├── common/                 # 公共工具
│   │   │   ├── __init__.py
│   │   │   ├── language_detector.py # 语言检测
│   │   │   ├── file_utils.py       # 文件工具
│   │   │   ├── constants.py        # 常量定义
│   │   │   └── exceptions.py       # 异常定义
│   │   └── cli/                    # CLI接口
│   │       ├── __init__.py
│   │       ├── main.py             # 主入口
│   │       ├── commands.py         # 命令定义
│   │       └── options.py          # 选项定义
├── tests/                          # 测试代码
│   ├── __init__.py
│   ├── test_analyzers/
│   ├── test_parsers/
│   ├── test_metrics/
│   ├── test_reports/
│   ├── test_common/
│   └── fixtures/                   # 测试数据
├── docs/                           # 文档
├── requirements.txt                # 运行依赖
├── requirements-dev.txt            # 开发依赖
├── setup.py                        # 安装脚本
├── pyproject.toml                  # 项目配置
├── README.md                       # 项目说明
└── .gitignore                      # Git忽略文件
```

## 核心接口设计

### 1. 分析器接口 (analyzers/interfaces.py)

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from .models import AnalysisResult

class Analyzer(ABC):
    """代码分析器抽象接口"""
    
    @abstractmethod
    def analyze(self, path: str) -> AnalysisResult:
        """分析指定路径的代码"""
        
    @abstractmethod
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """分析单个文件"""
        
    @abstractmethod
    def analyze_with_excludes(
        self, 
        path: str, 
        include_patterns: Optional[List[str]], 
        exclude_patterns: Optional[List[str]]
    ) -> AnalysisResult:
        """使用包含/排除模式分析目录"""
```

### 2. 解析器接口 (parsers/interfaces.py)

```python
from abc import ABC, abstractmethod
from typing import List
from ..common.constants import LanguageType
from .models import ParseResult

class Parser(ABC):
    """代码解析器抽象接口"""
    
    @abstractmethod
    def parse(self, file_path: str, content: bytes) -> ParseResult:
        """解析代码内容"""
        
    @abstractmethod
    def supported_languages(self) -> List[LanguageType]:
        """返回支持的语言类型"""
```

### 3. 指标接口 (metrics/interfaces.py)

```python
from abc import ABC, abstractmethod
from typing import List
from ..common.constants import LanguageType
from ..parsers.models import ParseResult
from .models import MetricResult

class Metric(ABC):
    """代码质量指标抽象接口"""
    
    @abstractmethod
    def name(self) -> str:
        """返回指标名称"""
        
    @abstractmethod
    def description(self) -> str:
        """返回指标描述"""
        
    @abstractmethod
    def weight(self) -> float:
        """返回指标权重"""
        
    @abstractmethod
    def analyze(self, parse_result: ParseResult) -> MetricResult:
        """分析代码并返回结果"""
        
    @abstractmethod
    def supported_languages(self) -> List[LanguageType]:
        """返回支持的语言类型"""
```

## 数据模型设计

### 核心数据模型

1. **分析结果模型** (analyzers/models.py)
2. **解析结果模型** (parsers/models.py)  
3. **指标结果模型** (metrics/models.py)
4. **函数信息模型** (parsers/models.py)

### 常量定义 (common/constants.py)

- 支持的编程语言枚举
- 质量评级常量
- 默认配置参数
- 文件扩展名映射

## 技术选型

### 核心依赖库

1. **Click**: CLI框架，用于命令行接口
2. **Rich**: 终端彩色输出和格式化
3. **ast**: Python内置AST解析
4. **esprima**: JavaScript解析 (通过PyExecJS)
5. **javalang**: Java代码解析
6. **pycparser**: C代码解析
7. **typing_extensions**: 类型注解扩展

### 开发依赖

1. **pytest**: 单元测试框架
2. **pytest-cov**: 测试覆盖率
3. **black**: 代码格式化
4. **flake8**: 代码检查
5. **mypy**: 静态类型检查
6. **isort**: 导入排序

### 可选依赖

1. **tree-sitter**: 更强大的多语言解析 (高级功能)
2. **pyyaml**: YAML配置文件支持
3. **toml**: TOML配置文件支持

## 设计模式应用

### 1. 工厂模式
- **解析器工厂**: 根据文件类型创建相应解析器
- **指标工厂**: 创建所有质量指标实例
- **报告器工厂**: 根据输出格式创建报告器

### 2. 策略模式
- **解析策略**: 不同语言的解析实现
- **指标策略**: 不同指标的计算方法
- **报告策略**: 不同格式的报告生成

### 3. 观察者模式
- **进度通知**: 分析进度的实时反馈
- **事件处理**: 分析过程中的事件通知

### 4. 模板方法模式
- **基础分析器**: 定义分析流程骨架
- **基础指标**: 定义指标计算模板

## 扩展性设计

### 1. 新语言支持
通过实现Parser接口，可以轻松添加新语言支持：
- 创建新的解析器类
- 在工厂中注册新解析器
- 添加语言常量定义

### 2. 新指标支持
通过实现Metric接口，可以添加新的质量指标：
- 创建新的指标类
- 在工厂中注册新指标
- 添加相应的翻译文本

### 3. 新报告格式
通过实现Reporter接口，可以支持新的输出格式：
- 创建新的报告器类
- 在工厂中注册新报告器
- 添加相应的CLI选项

## 性能考虑

### 1. 并发处理
- 使用threading或asyncio实现文件并发分析
- 控制并发数量避免资源过载

### 2. 内存优化
- 流式处理大文件
- 及时释放不需要的AST节点

### 3. 缓存机制
- 解析结果缓存 (可选)
- 文件修改时间检查

## 错误处理策略

### 1. 分层异常处理
- 业务异常：分析失败、解析错误等
- 系统异常：文件不存在、权限不足等
- 用户异常：参数错误、配置错误等

### 2. 容错机制
- 单个文件解析失败不影响整体分析
- 提供详细的错误信息和建议
- 优雅降级处理

## 测试策略

### 1. 单元测试
每个模块都要有对应的单元测试，确保功能正确性

### 2. 集成测试
测试模块间的协作，验证整体流程

### 3. 端到端测试
测试完整的分析流程，从输入到输出

### 4. 性能测试
测试大文件和大项目的分析性能

下一步将详细说明各个模块的具体实现方法。