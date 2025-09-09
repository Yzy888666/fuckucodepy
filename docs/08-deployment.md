# 部署和打包指南

## 概述

本指南提供Python版本fuck-u-code项目的完整部署和打包策略，包括开发环境配置、打包发布、容器化部署等。

## 1. 项目配置文件

### 1.1 setup.py配置
```python
# setup.py
from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements
def read_requirements(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="fuck-u-code",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="代码质量分析工具 - Python版本",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fuck-u-code-python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "test": ["pytest>=7.0", "pytest-cov>=4.0"],
    },
    entry_points={
        "console_scripts": [
            "fuck-u-code=fuck_u_code.cli.main:main",
            "fuc=fuck_u_code.cli.main:main",  # 简短别名
        ],
    },
    include_package_data=True,
    package_data={
        "fuck_u_code": ["i18n/*.json", "templates/*.md"],
    },
)
```

### 1.2 pyproject.toml配置
```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fuck-u-code"
version = "1.0.0"
description = "代码质量分析工具 - Python版本"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "click>=8.0.0",
    "rich>=12.0.0",
    "pyyaml>=6.0",
    "esprima>=4.0.1",
    "javalang>=0.13.0",
    "pycparser>=2.20",
]
requires-python = ">=3.8"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=0.991",
    "isort>=5.10.0",
]

[project.scripts]
fuck-u-code = "fuck_u_code.cli.main:main"
fuc = "fuck_u_code.cli.main:main"

[project.urls]
Homepage = "https://github.com/yourusername/fuck-u-code-python"
Repository = "https://github.com/yourusername/fuck-u-code-python"
Documentation = "https://fuck-u-code-python.readthedocs.io"
"Bug Tracker" = "https://github.com/yourusername/fuck-u-code-python/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
fuck_u_code = ["i18n/*.json", "templates/*.md"]

# 工具配置
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
```

### 1.3 requirements文件
```txt
# requirements.txt
click>=8.0.0
rich>=12.0.0
pyyaml>=6.0
esprima>=4.0.1
javalang>=0.13.0
pycparser>=2.20
typing-extensions>=4.0.0

# requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991
isort>=5.10.0
pre-commit>=2.20.0
tox>=4.0.0
wheel>=0.37.0
twine>=4.0.0
```

## 2. 版本管理

### 2.1 版本号策略
使用语义化版本控制 (Semantic Versioning):
- 主版本号: 不兼容的API修改
- 次版本号: 向下兼容的功能新增
- 修订版本号: 向下兼容的问题修正

### 2.2 版本管理脚本
```python
# scripts/version_manager.py
import re
import sys
from pathlib import Path

def update_version(new_version: str):
    """更新所有文件中的版本号"""
    files_to_update = [
        "src/fuck_u_code/__init__.py",
        "setup.py",
        "pyproject.toml",
        "docs/conf.py"
    ]
    
    version_pattern = r'version\s*=\s*["\']([^"\']+)["\']'
    
    for file_path in files_to_update:
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = re.sub(version_pattern, f'version = "{new_version}"', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    print(f"版本号已更新为: {new_version}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python version_manager.py <new_version>")
        sys.exit(1)
    
    update_version(sys.argv[1])
```

## 3. 构建和打包

### 3.1 本地构建
```bash
# 清理之前的构建
rm -rf build/ dist/ *.egg-info/

# 安装构建工具
pip install --upgrade build wheel twine

# 构建分发包
python -m build

# 检查构建结果
twine check dist/*
```

### 3.2 自动化构建脚本
```bash
#!/bin/bash
# scripts/build.sh

set -e

echo "🏗️  开始构建 fuck-u-code..."

# 清理
echo "🧹 清理之前的构建..."
rm -rf build/ dist/ *.egg-info/

# 检查代码质量
echo "🔍 检查代码质量..."
black --check src tests
flake8 src tests
mypy src

# 运行测试
echo "🧪 运行测试..."
pytest tests/ --cov=fuck_u_code --cov-report=term-missing

# 构建
echo "📦 构建分发包..."
python -m build

# 验证
echo "✅ 验证构建结果..."
twine check dist/*

echo "🎉 构建完成！"
ls -la dist/
```

### 3.3 GitHub Actions自动构建
```yaml
# .github/workflows/build.yml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [published]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: flake8 src tests
    
    - name: Type check with mypy
      run: mypy src
    
    - name: Test with pytest
      run: pytest tests/ --cov=fuck_u_code --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: distributions
        path: dist/

  publish:
    if: github.event_name == 'release'
    needs: build
    runs-on: ubuntu-latest
    
    steps:
    - name: Download artifacts
      uses: actions/download-artifact@v3
      with:
        name: distributions
        path: dist/
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## 4. 容器化部署

### 4.1 Dockerfile
```dockerfile
# Dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY src/ ./src/
COPY setup.py .
COPY pyproject.toml .
COPY README.md .

# 安装应用
RUN pip install -e .

# 创建非root用户
RUN useradd -m -u 1000 codeuser
USER codeuser

# 设置入口点
ENTRYPOINT ["fuck-u-code"]
CMD ["--help"]
```

### 4.2 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  fuck-u-code:
    build: .
    image: fuck-u-code:latest
    volumes:
      - ./code-to-analyze:/code:ro
      - ./reports:/reports
    environment:
      - FUCK_U_CODE_LANG=zh-CN
    command: analyze /code --markdown --output /reports/report.md

  # 开发环境
  dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - ./code-samples:/code
    environment:
      - PYTHONPATH=/app/src
    command: bash
```

### 4.3 多阶段构建优化
```dockerfile
# Dockerfile.optimized
# 构建阶段
FROM python:3.10-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.10-slim

# 复制已安装的包
COPY --from=builder /root/.local /root/.local

# 复制应用
WORKDIR /app
COPY src/ ./src/
COPY setup.py .
COPY pyproject.toml .
COPY README.md .

# 安装应用
RUN pip install --no-deps -e .

# 创建用户
RUN useradd -m codeuser
USER codeuser

# 更新PATH
ENV PATH=/root/.local/bin:$PATH

ENTRYPOINT ["fuck-u-code"]
CMD ["--help"]
```

## 5. 发布流程

### 5.1 PyPI发布
```bash
# 1. 准备发布
python scripts/version_manager.py 1.0.0
git add .
git commit -m "Bump version to 1.0.0"
git tag v1.0.0

# 2. 构建
./scripts/build.sh

# 3. 测试发布到TestPyPI
twine upload --repository testpypi dist/*

# 4. 测试安装
pip install --index-url https://test.pypi.org/simple/ fuck-u-code

# 5. 正式发布
twine upload dist/*

# 6. 推送标签
git push origin v1.0.0
```

### 5.2 GitHub Release
```bash
# 使用GitHub CLI创建release
gh release create v1.0.0 \
    --title "v1.0.0 - Initial Release" \
    --notes "首个正式版本发布" \
    dist/*
```

### 5.3 发布检查清单
- [ ] 版本号已更新
- [ ] CHANGELOG已更新
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 构建无错误
- [ ] 在TestPyPI测试成功
- [ ] README示例可用
- [ ] 依赖版本锁定

## 6. 安装验证

### 6.1 安装测试脚本
```python
# scripts/test_installation.py
import subprocess
import sys
import tempfile
import os

def test_pip_install():
    """测试pip安装"""
    try:
        # 在临时环境中测试安装
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "fuck-u-code"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 安装失败: {result.stderr}")
            return False
        
        # 测试命令是否可用
        result = subprocess.run([
            "fuck-u-code", "--version"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败: {result.stderr}")
            return False
        
        print(f"✅ 安装成功: {result.stdout.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False

def test_basic_functionality():
    """测试基础功能"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("def hello(): print('world')")
        
        # 测试分析
        result = subprocess.run([
            "fuck-u-code", "analyze", temp_dir
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 分析失败: {result.stderr}")
            return False
        
        if "分析结果" not in result.stdout and "analysis" not in result.stdout.lower():
            print(f"❌ 输出不符合预期: {result.stdout}")
            return False
        
        print("✅ 基础功能测试通过")
        return True

if __name__ == "__main__":
    print("🧪 开始安装测试...")
    
    if not test_pip_install():
        sys.exit(1)
    
    if not test_basic_functionality():
        sys.exit(1)
    
    print("🎉 所有测试通过！")
```

## 7. 部署环境配置

### 7.1 生产环境要求
- Python 3.8+
- 2GB+ 内存
- 1GB+ 磁盘空间
- 支持UTF-8编码

### 7.2 系统依赖安装
```bash
# Ubuntu/Debian
apt-get update
apt-get install -y python3 python3-pip git

# CentOS/RHEL
yum install -y python3 python3-pip git

# macOS
brew install python3 git

# Windows (PowerShell)
# 安装Python和Git from官网
```

### 7.3 环境配置脚本
```bash
#!/bin/bash
# scripts/setup_environment.sh

set -e

echo "🚀 配置fuck-u-code环境..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "📍 Python版本: $python_version"

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
python3 -m venv fuck-u-code-env
source fuck-u-code-env/bin/activate

# 升级pip
pip install --upgrade pip

# 安装fuck-u-code
echo "📦 安装fuck-u-code..."
pip install fuck-u-code

# 验证安装
echo "✅ 验证安装..."
fuck-u-code --version

echo "🎉 环境配置完成！"
echo "使用方法: source fuck-u-code-env/bin/activate && fuck-u-code --help"
```

## 8. 监控和维护

### 8.1 使用统计收集
```python
# src/fuck_u_code/telemetry.py (可选)
import hashlib
import platform
import json
from pathlib import Path

class TelemetryCollector:
    """使用统计收集器（匿名）"""
    
    def __init__(self, enable_telemetry=True):
        self.enable_telemetry = enable_telemetry
        self.stats_file = Path.home() / ".fuck-u-code" / "stats.json"
    
    def record_usage(self, command, language, file_count, duration):
        """记录使用统计"""
        if not self.enable_telemetry:
            return
        
        # 创建匿名统计数据
        stats = {
            "command": command,
            "language": language,
            "file_count_range": self._get_range(file_count),
            "duration_range": self._get_range(duration),
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "timestamp": int(time.time())
        }
        
        self._save_stats(stats)
    
    def _get_range(self, value):
        """将数值转换为范围，保护隐私"""
        if value < 10:
            return "0-10"
        elif value < 100:
            return "10-100"
        elif value < 1000:
            return "100-1000"
        else:
            return "1000+"
```

### 8.2 版本更新检查
```python
# src/fuck_u_code/update_checker.py
import requests
import json
from packaging import version

def check_for_updates(current_version):
    """检查是否有新版本"""
    try:
        response = requests.get(
            "https://pypi.org/pypi/fuck-u-code/json",
            timeout=5
        )
        data = response.json()
        latest_version = data["info"]["version"]
        
        if version.parse(latest_version) > version.parse(current_version):
            return {
                "has_update": True,
                "latest_version": latest_version,
                "release_notes": data["info"]["description"]
            }
        
        return {"has_update": False}
        
    except Exception:
        return {"has_update": False, "error": "检查更新失败"}
```

## 9. 验证检查清单

### 9.1 打包验证
- [ ] setup.py配置正确
- [ ] pyproject.toml配置完整
- [ ] requirements文件完整
- [ ] 版本号一致性

### 9.2 构建验证
- [ ] 本地构建成功
- [ ] 分发包完整
- [ ] 依赖解析正确
- [ ] 入口点可执行

### 9.3 发布验证
- [ ] TestPyPI发布成功
- [ ] 安装测试通过
- [ ] 基础功能验证
- [ ] 多平台兼容性

### 9.4 部署验证
- [ ] 容器构建成功
- [ ] 生产环境部署正常
- [ ] 性能指标符合预期
- [ ] 监控系统工作正常

完成所有文档后，项目的Python重新实现指南就完整了！