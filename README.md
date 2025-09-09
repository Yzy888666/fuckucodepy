# fuck-u-code Python版本重新实现

## 项目简介

fuck-u-code是一个代码质量分析工具的Python重新实现版本，原项目使用Go语言开发。该工具专门分析代码质量，通过七大维度评估代码并生成幽默风格的质量报告。

**⚠️ 注意：这是一个技术项目，项目名称具有幽默性质，请理性看待。**

## 🌟 核心功能

- **🔍 多语言代码分析**: 支持Python、JavaScript/TypeScript、Java、C/C++等（当前版本主要支持Python）
- **📊 七大评估维度**: 
  - 循环复杂度分析
  - 函数长度检查
  - 注释覆盖率评估  
  - 错误处理分析
  - 命名规范检查
  - 代码重复度检测
  - 代码结构分析
- **🎯 质量评分系统**: 0-100分制，分数越高表示代码质量越差
- **📋 多格式报告**: 彩色终端输出、Markdown格式报告
- **⚙️ 灵活配置**: 支持文件排除、语言选择、详细/摘要模式等

## 🏆 质量等级

从优秀到糟糕，我们定义了11个质量等级：

| 分数范围 | 等级 | 表情 | 描述 |
|---------|------|------|------|
| 0-5 | 🌱 清新可人 | 🌱 | 代码写得很棒，继续保持！ |
| 5-15 | 🌸 偶有异味 | 🌸 | 代码整体不错，有小瑕疵 |
| 15-25 | 😐 微臭青年 | 😐 | 代码需要一些改进 |
| 25-40 | 😷 屎气扑鼻 | 😷 | 代码质量堪忧，需要重构 |
| 40-55 | 💩 中度屎山 | 💩 | 代码质量很差，必须重写 |
| 55-65 | 🤕 隐性毒瘤 | 🤕 | 代码已成灾难，请立即行动 |
| 65-75 | ☣️ 重度屎山 | ☣️ | 代码质量极差，需要彻底重构 |
| 75-85 | 🧟 代码化尸场 | 🧟 | 代码无法维护，建议重写 |
| 85-95 | ☢️ 核平级灾难 | ☢️ | 代码已成灾难，请放弃挣扎 |
| 95-100 | 🪦 祖传老屎 | 🪦 | 这代码已经无药可救了 |
| 100+ | 👑💩 终极屎王 | 👑💩 | 恭喜！你创造了传奇 |

## 🚀 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/fuck-u-code/fuck-u-code-python.git
cd fuck-u-code-python
pip install -e .

# 或者直接安装依赖进行测试
pip install click rich pyyaml
```

### 基础使用

```bash
# 分析当前目录
python -m fuck_u_code.cli.main analyze

# 分析指定目录，显示详细信息
python -m fuck_u_code.cli.main analyze /path/to/project --verbose

# 生成Markdown报告
python -m fuck_u_code.cli.main analyze --markdown > report.md

# 排除特定目录
python -m fuck_u_code.cli.main analyze --exclude "*/test/*" --exclude "*/node_modules/*"

# 只显示最严重的问题
python -m fuck_u_code.cli.main analyze --top 3 --summary
```

### 测试项目功能

```bash
# 运行简单测试脚本
python test_simple.py
```

## 📁 项目结构

```
src/fuck_u_code/
├── analyzers/          # 分析器模块
├── parsers/            # 解析器模块  
├── metrics/            # 指标系统
├── reports/            # 报告系统
├── cli/                # CLI接口
└── common/             # 公共工具
```

## 📊 分析示例

### 优秀代码示例
```
🔍 代码质量分析报告
总体评分: 8.3分 🌸 偶有异味
发现问题: 1个
```

### 问题代码示例
```
🔍 代码质量分析报告
总体评分: 32.2分 😷 屎气扑鼻
发现问题: 15个 (包含1个严重问题)
```

## 🛠️ 开发状态

当前版本: v1.0.0

### ✅ 已实现功能
- Python代码解析和分析
- 循环复杂度、函数长度、注释覆盖率三大核心指标
- 终端彩色输出和Markdown报告
- 完整的CLI命令行界面
- 并行文件处理
- 质量等级评定系统

### 🚧 开发中功能
- JavaScript/TypeScript解析器
- Java解析器
- C/C++解析器
- 错误处理分析指标
- 命名规范检查指标
- 代码重复度检测
- 代码结构分析
- HTML报告格式

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置
```bash
git clone https://github.com/fuck-u-code/fuck-u-code-python.git
cd fuck-u-code-python
pip install -r requirements-dev.txt
```

### 运行测试
```bash
# 运行简单功能测试
python test_simple.py

# 运行完整测试套件（需要安装pytest）
pytest tests/
```

## 📝 许可证

MIT License - 详见 [LICENSE](MIT) 文件

## 🙏 致谢

- 感谢原始Go版本的fuck-u-code项目提供灵感
- 感谢所有贡献者的支持

---

**⚠️ 免责声明**: 这是一个技术项目，项目名称具有幽默性质，请理性看待。本工具旨在帮助开发者提升代码质量，不涉及任何恶意内容。