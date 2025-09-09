# CLI接口开发指南

## 模块概述

CLI接口是用户与应用程序交互的主要入口，需要提供直观、易用、功能完整的命令行界面。基于Click框架实现，支持丰富的命令选项和用户友好的帮助信息。

## 核心设计原理

### CLI架构设计

```
┌─────────────────────────────────────────┐
│              main.py                    │
│           (应用入口点)                   │
└─────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────┐
│            commands.py                  │
│         (命令定义和处理)                 │
└─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│AnalyzeCmd   │ │ConfigCmd    │ │VersionCmd  │
│(分析命令)   │ │(配置命令)   │ │(版本信息)  │
└─────────────┘ └─────────────┘ └─────────────┘
                        │
┌─────────────────────────────────────────┐
│            options.py                   │
│         (选项定义和验证)                 │
└─────────────────────────────────────────┘
```

## 1. 主入口实现 (main.py)

### 1.1 应用程序入口

#### 功能说明
定义应用程序的主入口点，初始化CLI框架，设置全局配置。

#### 实现步骤

**步骤1**: 实现基础CLI结构
- 使用Click创建主命令组
- 设置应用程序元信息
- 配置全局选项和上下文

**步骤2**: 实现全局配置
- 版本信息显示
- 调试模式支持
- 日志级别控制
- 配置文件支持

**步骤3**: 实现错误处理
- 全局异常捕获
- 用户友好的错误信息
- 调试信息输出控制

#### 主程序结构
```python
import click
from .commands import analyze, config, version
from .exceptions import FuckUCodeError

@click.group()
@click.version_option(version="1.0.0", prog_name="fuck-u-code")
@click.option('--debug', is_flag=True, help='启用调试模式')
@click.option('--config', type=click.Path(), help='配置文件路径')
@click.pass_context
def cli(ctx, debug, config):
    """
    🔍 fuck-u-code - 代码质量分析工具
    
    一个专为挖掘"屎山代码"设计的工具，能无情揭露代码的丑陋真相。
    """
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['config'] = config

# 注册子命令
cli.add_command(analyze)
cli.add_command(config)
cli.add_command(version)

def main():
    """主入口函数"""
    try:
        cli()
    except FuckUCodeError as e:
        click.echo(f"❌ 错误: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n⏹️  操作已取消", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"💥 意外错误: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

#### 测试验证方法
- 测试命令行参数解析
- 验证版本信息显示
- 测试错误处理机制
- 验证配置文件加载

**测试命令**:
```bash
# 测试版本显示
python -m fuck_u_code --version

# 测试帮助信息
python -m fuck_u_code --help

# 测试错误处理
python -m fuck_u_code invalid-command
```

## 2. 命令定义 (commands.py)

### 2.1 分析命令实现

#### 功能说明
实现核心的代码分析命令，支持多种选项和配置。

#### 实现步骤

**步骤1**: 定义分析命令基础结构
- 路径参数处理
- 基本选项支持
- 输出格式控制

**步骤2**: 实现详细选项
- 详细度控制 (verbose, summary)
- 文件过滤选项 (exclude, include)
- 数量限制选项 (top, issues)
- 语言设置选项

**步骤3**: 实现高级功能
- 配置文件支持
- 输出重定向
- 并发控制
- 进度显示控制

#### 分析命令实现
```python
@click.command()
@click.argument('path', 
                type=click.Path(exists=True), 
                default='.', 
                metavar='[PATH]')
@click.option('--verbose', '-v', 
              is_flag=True, 
              help='显示详细分析报告')
@click.option('--summary', '-s', 
              is_flag=True, 
              help='只显示总结，不显示详情')
@click.option('--markdown', '-m', 
              is_flag=True, 
              help='输出Markdown格式报告')
@click.option('--json', 
              is_flag=True, 
              help='输出JSON格式报告')
@click.option('--top', '-t', 
              type=click.IntRange(1, 100), 
              default=5, 
              help='显示问题最多的前N个文件')
@click.option('--issues', '-i', 
              type=click.IntRange(1, 50), 
              default=5, 
              help='每个文件显示N个问题')
@click.option('--lang', '-l', 
              type=click.Choice(['zh-CN', 'en-US']), 
              default='zh-CN', 
              help='输出语言')
@click.option('--exclude', '-e', 
              multiple=True, 
              help='排除文件/目录模式 (可多次使用)')
@click.option('--include', 
              multiple=True, 
              help='包含文件/目录模式 (可多次使用)')
@click.option('--skipindex', '-x', 
              is_flag=True, 
              help='跳过index.js/index.ts文件')
@click.option('--output', '-o', 
              type=click.Path(), 
              help='输出到文件')
@click.option('--silent', 
              is_flag=True, 
              help='静默模式，不显示进度')
@click.pass_context
def analyze(ctx, path, verbose, summary, markdown, json, top, issues, 
           lang, exclude, include, skipindex, output, silent):
    """
    分析指定路径的代码质量
    
    PATH: 要分析的文件或目录路径 (默认为当前目录)
    
    示例:
      fuck-u-code analyze                    # 分析当前目录
      fuck-u-code analyze /path/to/project   # 分析指定目录
      fuck-u-code analyze --verbose          # 详细模式
      fuck-u-code analyze --markdown > report.md  # 输出到文件
    """
    # 参数验证
    if summary and verbose:
        raise click.UsageError("--summary 和 --verbose 不能同时使用")
    
    if sum([markdown, json]) > 1:
        raise click.UsageError("只能选择一种输出格式")
    
    # 构建配置
    config = AnalysisConfig(
        path=path,
        verbose=verbose,
        summary=summary,
        output_format=determine_output_format(markdown, json),
        top_files=top,
        max_issues=issues,
        language=lang,
        exclude_patterns=list(exclude),
        include_patterns=list(include),
        skip_index=skipindex,
        output_file=output,
        silent=silent
    )
    
    # 执行分析
    try:
        analyzer = create_analyzer(config)
        result = analyzer.analyze(config.path)
        
        # 生成报告
        reporter = create_reporter(config)
        report_content = reporter.generate(result, config)
        
        # 输出结果
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report_content)
            click.echo(f"📄 报告已保存到: {output}")
        else:
            click.echo(report_content)
            
    except AnalysisError as e:
        raise click.ClickException(f"分析失败: {e}")
```

#### 测试验证方法
- 测试各种参数组合
- 验证文件路径处理
- 测试错误情况处理
- 验证输出格式正确性

**测试命令示例**:
```bash
# 基础分析
python -m fuck_u_code analyze

# 详细模式
python -m fuck_u_code analyze --verbose

# Markdown输出
python -m fuck_u_code analyze --markdown

# 排除特定目录
python -m fuck_u_code analyze --exclude "*/test/*"

# 限制显示文件数
python -m fuck_u_code analyze --top 3
```

### 2.2 配置命令实现

#### 功能说明
提供配置管理功能，包括查看、设置、重置配置。

#### 实现步骤

**步骤1**: 实现配置查看
- 显示当前配置
- 配置来源信息
- 配置文件位置

**步骤2**: 实现配置设置
- 键值对设置
- 配置验证
- 配置持久化

**步骤3**: 实现配置管理
- 配置重置
- 配置导入导出
- 配置模板生成

#### 配置命令实现
```python
@click.group()
def config():
    """配置管理命令"""
    pass

@config.command()
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), 
              default='table', help='输出格式')
def show(format):
    """显示当前配置"""
    config_manager = ConfigManager()
    current_config = config_manager.load()
    
    if format == 'table':
        display_config_table(current_config)
    elif format == 'json':
        click.echo(json.dumps(current_config.to_dict(), indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(current_config.to_dict()))

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """设置配置项"""
    config_manager = ConfigManager()
    try:
        config_manager.set(key, value)
        click.echo(f"✅ 配置已更新: {key} = {value}")
    except ConfigError as e:
        raise click.ClickException(f"配置设置失败: {e}")

@config.command()
@click.confirmation_option(prompt="确定要重置所有配置吗？")
def reset():
    """重置配置为默认值"""
    config_manager = ConfigManager()
    config_manager.reset()
    click.echo("✅ 配置已重置为默认值")
```

### 2.3 版本命令实现

#### 实现步骤

**步骤1**: 基础版本信息
- 应用版本号
- 构建信息
- Python版本

**步骤2**: 详细版本信息
- 依赖库版本
- 系统信息
- 功能特性支持

```python
@click.command()
@click.option('--verbose', '-v', is_flag=True, help='显示详细版本信息')
def version(verbose):
    """显示版本信息"""
    click.echo(f"fuck-u-code version {__version__}")
    
    if verbose:
        click.echo(f"Python: {sys.version}")
        click.echo(f"Platform: {platform.platform()}")
        click.echo("\n依赖库:")
        for lib, ver in get_dependency_versions().items():
            click.echo(f"  {lib}: {ver}")
```

## 3. 选项定义 (options.py)

### 3.1 通用选项定义

#### 功能说明
定义可重用的命令行选项，确保一致性和可维护性。

#### 实现步骤

**步骤1**: 定义选项装饰器
- 通用选项装饰器
- 选项组合装饰器
- 参数验证装饰器

**步骤2**: 实现选项验证
- 类型检查
- 范围检查
- 依赖关系检查

**步骤3**: 实现选项处理
- 默认值处理
- 环境变量支持
- 配置文件集成

#### 通用选项实现
```python
from functools import update_wrapper

def verbose_option(f):
    """详细输出选项"""
    def callback(ctx, param, value):
        ctx.ensure_object(dict)
        ctx.obj['verbose'] = value
        return value
    
    return click.option('--verbose', '-v',
                       is_flag=True,
                       expose_value=False,
                       callback=callback,
                       help='显示详细信息')(f)

def output_format_options(f):
    """输出格式选项组"""
    f = click.option('--markdown', '-m', 'output_markdown',
                    is_flag=True, help='输出Markdown格式')(f)
    f = click.option('--json', 'output_json',
                    is_flag=True, help='输出JSON格式')(f)
    return f

def analysis_options(f):
    """分析相关选项组"""
    f = click.option('--top', '-t',
                    type=click.IntRange(1, 100),
                    default=5,
                    help='显示前N个问题文件')(f)
    f = click.option('--issues', '-i',
                    type=click.IntRange(1, 50),
                    default=5,
                    help='每文件显示N个问题')(f)
    f = click.option('--exclude', '-e',
                    multiple=True,
                    help='排除模式 (可多次使用)')(f)
    return f
```

### 3.2 参数验证

#### 实现步骤

**步骤1**: 实现自定义验证器
- 路径存在性检查
- 文件类型验证
- 格式兼容性检查

**步骤2**: 实现交互式验证
- 危险操作确认
- 缺失参数提示
- 智能默认值建议

```python
class PathType(click.Path):
    """增强的路径类型，支持更多验证"""
    
    def convert(self, value, param, ctx):
        path = super().convert(value, param, ctx)
        
        # 检查是否为空目录
        if os.path.isdir(path) and not os.listdir(path):
            self.fail(f"目录 '{path}' 为空", param, ctx)
        
        return path

def validate_output_format(ctx, param, value):
    """验证输出格式选项的一致性"""
    formats = [name for name, val in value.items() if val]
    
    if len(formats) > 1:
        raise click.BadParameter(f"只能选择一种输出格式，当前选择了: {', '.join(formats)}")
    
    return value

def validate_analysis_config(ctx, param, value):
    """验证分析配置的合理性"""
    if value.get('summary') and value.get('verbose'):
        raise click.BadParameter("--summary 和 --verbose 不能同时使用")
    
    return value
```

## 4. 配置管理

### 4.1 配置文件支持

#### 功能说明
支持YAML和JSON格式的配置文件，提供配置层次化管理。

#### 实现步骤

**步骤1**: 实现配置文件读取
- YAML格式支持
- JSON格式支持
- 配置文件发现机制

**步骤2**: 实现配置合并
- 默认配置
- 用户配置文件
- 命令行参数
- 环境变量

**步骤3**: 实现配置验证
- 配置项类型检查
- 必需配置检查
- 配置兼容性验证

#### 配置管理实现
```python
class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_paths = [
            os.path.expanduser('~/.fuck-u-code.yml'),
            os.path.expanduser('~/.fuck-u-code.yaml'),
            os.path.expanduser('~/.config/fuck-u-code/config.yml'),
            '.fuck-u-code.yml',
            'pyproject.toml'  # 支持在pyproject.toml中配置
        ]
    
    def load(self) -> AppConfig:
        """加载配置"""
        config = AppConfig()  # 默认配置
        
        # 查找并加载配置文件
        for path in self.config_paths:
            if os.path.exists(path):
                file_config = self._load_config_file(path)
                config = config.merge(file_config)
                break
        
        # 应用环境变量
        env_config = self._load_from_env()
        config = config.merge(env_config)
        
        return config
    
    def _load_config_file(self, path: str) -> AppConfig:
        """从文件加载配置"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.toml'):
                    data = toml.load(f).get('tool', {}).get('fuck-u-code', {})
                else:
                    data = yaml.safe_load(f)
            
            return AppConfig.from_dict(data)
        except Exception as e:
            raise ConfigError(f"配置文件 {path} 加载失败: {e}")
```

### 4.2 环境变量支持

```python
def _load_from_env(self) -> AppConfig:
    """从环境变量加载配置"""
    config = AppConfig()
    
    # 定义环境变量映射
    env_mappings = {
        'FUCK_U_CODE_LANG': 'language',
        'FUCK_U_CODE_OUTPUT_FORMAT': 'output_format',
        'FUCK_U_CODE_VERBOSE': 'verbose',
        'FUCK_U_CODE_SILENT': 'silent'
    }
    
    for env_var, config_key in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            setattr(config, config_key, self._convert_env_value(value, config_key))
    
    return config
```

## 5. 帮助系统

### 5.1 智能帮助

#### 实现步骤

**步骤1**: 实现上下文相关帮助
- 命令特定帮助
- 选项详细说明
- 使用示例

**步骤2**: 实现交互式帮助
- 命令建议
- 错误修正建议
- 快速入门指南

```python
def add_examples_to_help(command):
    """为命令添加使用示例"""
    examples = {
        'analyze': [
            'fuck-u-code analyze                    # 分析当前目录',
            'fuck-u-code analyze /path/to/project   # 分析指定目录',
            'fuck-u-code analyze --verbose          # 详细模式',
            'fuck-u-code analyze --markdown > report.md  # 输出Markdown'
        ]
    }
    
    if command.name in examples:
        command.help += f"\n\n示例:\n"
        for example in examples[command.name]:
            command.help += f"  {example}\n"
    
    return command

@click.command()
@click.pass_context
def tutorial(ctx):
    """显示快速入门教程"""
    tutorial_text = """
🎯 快速入门教程

1. 分析当前项目:
   $ fuck-u-code analyze

2. 查看详细报告:
   $ fuck-u-code analyze --verbose

3. 生成Markdown报告:
   $ fuck-u-code analyze --markdown > report.md

4. 排除特定目录:
   $ fuck-u-code analyze --exclude "*/test/*" --exclude "*/vendor/*"

5. 只看最严重的问题:
   $ fuck-u-code analyze --top 3 --summary

💡 更多帮助: fuck-u-code --help
"""
    click.echo(tutorial_text)
```

## 6. 实现优先级

### 第一阶段：基础CLI
1. 实现主入口和基础结构
2. 实现analyze命令核心功能
3. 实现基础选项和参数处理
4. 创建基础测试

### 第二阶段：完善功能
1. 实现config命令
2. 实现version命令
3. 添加配置文件支持
4. 完善错误处理

### 第三阶段：用户体验
1. 改进帮助系统
2. 添加自动补全
3. 实现交互式模式
4. 性能优化

## 7. 用户体验优化

### 7.1 命令补全

#### 实现bash/zsh补全
```python
def setup_completion():
    """设置shell补全"""
    completion_script = """
# fuck-u-code completion
_fuck_u_code_completion() {
    local IFS=$'\\n'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \\
                   COMP_CWORD=$COMP_CWORD \\
                   _FUCK_U_CODE_COMPLETE=complete $1 ) )
    return 0
}

complete -F _fuck_u_code_completion -o default fuck-u-code
    """
    return completion_script
```

### 7.2 进度显示

#### 实现友好的进度反馈
```python
def show_analysis_progress(files_count: int, silent: bool = False):
    """显示分析进度"""
    if silent:
        return
    
    with click.progressbar(length=files_count,
                          label='🔍 分析代码',
                          show_eta=True,
                          show_percent=True) as bar:
        for i in range(files_count):
            time.sleep(0.01)  # 模拟处理时间
            bar.update(1)
```

## 8. 错误处理和用户反馈

### 8.1 友好的错误信息

```python
class UserFriendlyError(Exception):
    """用户友好的错误基类"""
    
    def __init__(self, message: str, suggestion: str = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)

def handle_common_errors(func):
    """通用错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise UserFriendlyError(
                f"文件或目录不存在: {e.filename}",
                "请检查路径是否正确，或使用绝对路径"
            )
        except PermissionError as e:
            raise UserFriendlyError(
                f"权限不足: {e.filename}",
                "请检查文件权限，或使用管理员权限运行"
            )
        except MemoryError:
            raise UserFriendlyError(
                "内存不足，无法处理大型项目",
                "请尝试分析较小的目录，或增加系统内存"
            )
    
    return wrapper
```

## 9. 测试策略

### 9.1 CLI测试框架

#### 使用Click Testing进行测试
```python
from click.testing import CliRunner

def test_analyze_command():
    """测试analyze命令"""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        # 创建测试文件
        with open('test.py', 'w') as f:
            f.write('def hello(): print("world")')
        
        # 测试基础分析
        result = runner.invoke(analyze, ['.'])
        assert result.exit_code == 0
        assert '分析结果' in result.output
        
        # 测试verbose模式
        result = runner.invoke(analyze, ['.', '--verbose'])
        assert result.exit_code == 0
        assert len(result.output) > 100  # verbose应该输出更多内容

def test_invalid_arguments():
    """测试无效参数处理"""
    runner = CliRunner()
    
    # 测试不存在的路径
    result = runner.invoke(analyze, ['/nonexistent/path'])
    assert result.exit_code != 0
    assert '不存在' in result.output
    
    # 测试冲突的选项
    result = runner.invoke(analyze, ['.', '--summary', '--verbose'])
    assert result.exit_code != 0
    assert '不能同时使用' in result.output
```

### 9.2 集成测试

```python
def test_end_to_end_analysis():
    """端到端测试"""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        # 创建复杂的测试项目结构
        create_test_project()
        
        # 测试完整分析流程
        result = runner.invoke(analyze, ['.', '--markdown'])
        
        assert result.exit_code == 0
        assert '# 代码质量分析报告' in result.output
        assert '## 总体评估' in result.output
        assert '## 质量指标详情' in result.output
```

## 10. 性能优化

### 10.1 命令启动优化

```python
# 延迟导入重型库
def lazy_import_analyzer():
    """延迟导入分析器"""
    from ..analyzers import CodeAnalyzer
    return CodeAnalyzer

# 缓存常用配置
@lru_cache(maxsize=1)
def get_default_config():
    """获取默认配置(缓存)"""
    return ConfigManager().load()
```

### 10.2 大项目处理优化

```python
def optimize_for_large_projects(file_count: int):
    """大项目优化"""
    if file_count > 1000:
        # 启用进度条
        # 增加并发数
        # 启用内存优化模式
        return {
            'show_progress': True,
            'concurrent_workers': min(8, os.cpu_count()),
            'memory_optimize': True
        }
    return {}
```

## 11. 验证检查清单

完成CLI接口开发后，请验证以下功能：

### 基础功能验证
- [ ] 主命令能正常启动和显示帮助
- [ ] analyze命令能分析代码并输出结果
- [ ] 所有命令行选项都能正确解析
- [ ] 错误处理友好且有用

### 用户体验验证
- [ ] 帮助信息清晰易懂
- [ ] 进度显示及时准确
- [ ] 错误信息有具体建议
- [ ] 输出格式美观一致

### 兼容性验证
- [ ] 在不同操作系统上运行正常
- [ ] 支持不同版本的Python
- [ ] 配置文件正确加载
- [ ] 环境变量支持有效

### 性能验证
- [ ] 命令启动速度快
- [ ] 大项目处理性能可接受
- [ ] 内存使用控制合理
- [ ] 并发处理稳定

完成CLI接口后，可以继续实现测试策略和验证指南。