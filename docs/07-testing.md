# 测试策略和验证指南

## 测试策略概览

本指南提供Python版本fuck-u-code项目的完整测试策略，确保代码质量和功能正确性。

## 1. 测试框架选择

### 1.1 核心测试工具
- **pytest**: 主要测试框架
- **pytest-cov**: 测试覆盖率
- **pytest-mock**: Mock功能
- **pytest-asyncio**: 异步测试(如需要)

### 1.2 测试环境配置
```python
# requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
coverage>=7.0.0
tox>=4.0.0
```

## 2. 测试目录结构

```
tests/
├── conftest.py              # pytest配置和fixtures
├── test_analyzers/          # 分析器测试
│   ├── test_base_analyzer.py
│   └── test_code_analyzer.py
├── test_parsers/            # 解析器测试
│   ├── test_python_parser.py
│   ├── test_javascript_parser.py
│   └── test_factory.py
├── test_metrics/            # 指标测试
│   ├── test_complexity.py
│   ├── test_comment_ratio.py
│   └── test_factory.py
├── test_reports/            # 报告测试
│   ├── test_terminal_reporter.py
│   └── test_markdown_reporter.py
├── test_cli/                # CLI测试
│   ├── test_commands.py
│   └── test_options.py
├── test_common/             # 公共模块测试
│   ├── test_language_detector.py
│   └── test_file_utils.py
├── fixtures/                # 测试数据
│   ├── sample_projects/
│   └── expected_results/
└── integration/             # 集成测试
    └── test_end_to_end.py
```

## 3. 单元测试策略

### 3.1 解析器测试
```python
# test_parsers/test_python_parser.py
import pytest
from fuck_u_code.parsers import PythonParser

class TestPythonParser:
    def setup_method(self):
        self.parser = PythonParser()
    
    def test_parse_simple_function(self):
        code = """
def hello_world():
    print("Hello, World!")
    return True
"""
        result = self.parser.parse("test.py", code.encode())
        
        assert len(result.functions) == 1
        func = result.functions[0]
        assert func.name == "hello_world"
        assert func.parameters == 0
        assert func.complexity == 1
    
    def test_parse_complex_function(self):
        code = """
def complex_function(a, b, c):
    if a > 0:
        for i in range(b):
            if i % 2 == 0:
                try:
                    result = c / i
                except ZeroDivisionError:
                    continue
    return result
"""
        result = self.parser.parse("test.py", code.encode())
        func = result.functions[0]
        assert func.complexity > 5  # 具体值需要根据算法确定
```

### 3.2 指标测试
```python
# test_metrics/test_complexity.py
import pytest
from fuck_u_code.metrics import ComplexityMetric

class TestComplexityMetric:
    def setup_method(self):
        self.metric = ComplexityMetric()
    
    def test_simple_function_complexity(self):
        # 使用mock parse result
        mock_result = create_mock_parse_result([
            Function("simple", 1, 3, 1, 0)
        ])
        
        result = self.metric.analyze(mock_result)
        assert result.score < 0.5  # 简单函数应该得分较低
        assert len(result.issues) == 0
    
    def test_complex_function_complexity(self):
        mock_result = create_mock_parse_result([
            Function("complex", 1, 20, 15, 5)
        ])
        
        result = self.metric.analyze(mock_result)
        assert result.score > 0.7  # 复杂函数应该得分较高
        assert len(result.issues) > 0
```

### 3.3 CLI测试
```python
# test_cli/test_commands.py
from click.testing import CliRunner
from fuck_u_code.cli.main import cli

class TestCLICommands:
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_analyze_command_basic(self):
        with self.runner.isolated_filesystem():
            # 创建测试文件
            with open('test.py', 'w') as f:
                f.write('def hello(): pass')
            
            result = self.runner.invoke(cli, ['analyze', '.'])
            assert result.exit_code == 0
            assert '分析结果' in result.output
    
    def test_analyze_command_verbose(self):
        with self.runner.isolated_filesystem():
            create_test_project()
            
            result = self.runner.invoke(cli, ['analyze', '.', '--verbose'])
            assert result.exit_code == 0
            assert '详细' in result.output or 'verbose' in result.output.lower()
```

## 4. 集成测试策略

### 4.1 端到端测试
```python
# integration/test_end_to_end.py
class TestEndToEnd:
    def test_complete_analysis_workflow(self, tmp_path):
        # 创建测试项目
        project_dir = create_realistic_test_project(tmp_path)
        
        # 执行完整分析
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(str(project_dir))
        
        # 验证结果
        assert result.total_files > 0
        assert result.code_quality_score >= 0
        assert len(result.metrics) == 7  # 七大指标
        
        # 验证报告生成
        reporter = TerminalReporter()
        report = reporter.generate(result)
        assert len(report) > 0
```

### 4.2 跨语言测试
```python
def test_multi_language_project():
    """测试包含多种语言的项目"""
    project_files = {
        'main.py': python_code_sample,
        'script.js': javascript_code_sample,
        'App.java': java_code_sample,
        'utils.cpp': cpp_code_sample
    }
    
    with create_temp_project(project_files) as project_dir:
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(project_dir)
        
        # 验证每种语言都被正确识别和分析
        languages_found = {f.language for f in result.files_analyzed}
        expected_languages = {LanguageType.PYTHON, LanguageType.JAVASCRIPT, 
                            LanguageType.JAVA, LanguageType.CPP}
        assert languages_found.intersection(expected_languages)
```

## 5. 性能测试

### 5.1 大项目测试
```python
def test_large_project_performance(benchmark):
    """测试大项目分析性能"""
    large_project = create_large_test_project(files_count=1000)
    
    def analyze_large_project():
        analyzer = CodeAnalyzer()
        return analyzer.analyze(large_project)
    
    result = benchmark(analyze_large_project)
    assert result.total_files == 1000
    # 基准测试会自动记录性能数据
```

### 5.2 内存使用测试
```python
def test_memory_usage():
    """测试内存使用情况"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 分析大项目
    large_project = create_large_test_project(files_count=500)
    analyzer = CodeAnalyzer()
    result = analyzer.analyze(large_project)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 内存增长应该在合理范围内（如100MB以内）
    assert memory_increase < 100 * 1024 * 1024
```

## 6. 测试数据管理

### 6.1 Fixtures设计
```python
# conftest.py
import pytest

@pytest.fixture
def sample_python_code():
    return """
def calculate_score(values, weights=None):
    if not values:
        return 0.0
    
    if weights is None:
        weights = [1.0] * len(values)
    
    total = 0
    weight_sum = 0
    
    for i, value in enumerate(values):
        if i < len(weights):
            total += value * weights[i]
            weight_sum += weights[i]
    
    return total / weight_sum if weight_sum > 0 else 0.0
"""

@pytest.fixture
def complex_javascript_code():
    return """
function processData(data, options = {}) {
    const results = [];
    
    for (const item of data) {
        if (item.type === 'user') {
            const user = processUser(item);
            if (user.isValid) {
                results.push(user);
            }
        } else if (item.type === 'product') {
            const product = processProduct(item);
            if (product.price > 0 && product.inStock) {
                results.push(product);
            }
        }
    }
    
    return results.sort((a, b) => a.priority - b.priority);
}
"""

@pytest.fixture
def temp_project_factory():
    """创建临时测试项目的工厂函数"""
    def _create_project(files_dict, project_name="test_project"):
        import tempfile
        import os
        
        project_dir = tempfile.mkdtemp(prefix=project_name)
        
        for file_path, content in files_dict.items():
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return project_dir
    
    return _create_project
```

### 6.2 测试数据样本
```python
# fixtures/sample_data.py
EXPECTED_ANALYSIS_RESULTS = {
    'simple_function.py': {
        'complexity_score': 0.3,
        'function_count': 1,
        'issues_count': 0
    },
    'complex_function.py': {
        'complexity_score': 0.8,
        'function_count': 1,
        'issues_count': 2
    }
}

SAMPLE_PROJECTS = {
    'clean_project': {
        'main.py': clean_python_code,
        'utils.py': clean_utility_code,
        'README.md': "# Clean Project"
    },
    'messy_project': {
        'main.py': messy_python_code,
        'utils.py': messy_utility_code,
        'legacy.py': legacy_code_sample
    }
}
```

## 7. 持续集成测试

### 7.1 GitHub Actions配置
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=fuck_u_code --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### 7.2 Tox配置
```ini
# tox.ini
[tox]
envlist = py38,py39,py310,py311,flake8,mypy

[testenv]
deps = 
    pytest
    pytest-cov
    pytest-mock
commands = pytest {posargs}

[testenv:flake8]
deps = flake8
commands = flake8 src tests

[testenv:mypy]
deps = mypy
commands = mypy src

[testenv:coverage]
deps = 
    pytest
    pytest-cov
commands = 
    pytest --cov=fuck_u_code --cov-report=html --cov-report=term
```

## 8. 验证检查清单

### 8.1 单元测试验证
- [ ] 所有公共方法都有对应测试
- [ ] 测试覆盖率达到90%以上
- [ ] 边界情况和异常情况有测试
- [ ] Mock使用得当，测试独立

### 8.2 集成测试验证
- [ ] 端到端流程测试通过
- [ ] 多语言项目分析正确
- [ ] CLI命令集成测试通过
- [ ] 配置文件加载测试正确

### 8.3 性能测试验证
- [ ] 大项目分析性能可接受
- [ ] 内存使用控制在合理范围
- [ ] 并发处理稳定可靠
- [ ] 响应时间符合预期

### 8.4 质量保证验证
- [ ] 代码风格检查通过
- [ ] 类型检查无错误
- [ ] 安全扫描无高危问题
- [ ] 文档测试通过

完成测试策略后，可以继续实现部署和打包指南。