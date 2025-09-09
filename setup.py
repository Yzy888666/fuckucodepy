"""
fuck-u-code Python版本安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements
def read_requirements(filename):
    """读取依赖文件"""
    if not os.path.exists(filename):
        return []
    
    with open(filename, "r", encoding="utf-8") as f:
        return [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="fuck-u-code",
    version="1.0.0",
    author="fuck-u-code Team",
    author_email="team@fuck-u-code.com",
    description="代码质量分析工具 - Python版本",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fuck-u-code/fuck-u-code-python",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console",
        "Natural Language :: Chinese (Simplified)",
    ],
    keywords=[
        "code-quality", "static-analysis", "code-review", 
        "technical-debt", "refactoring", "complexity-analysis",
        "代码质量", "静态分析", "代码审查"
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "test": [
            "pytest>=7.0", 
            "pytest-cov>=4.0",
            "pytest-mock>=3.10.0"
        ],
    },
    entry_points={
        "console_scripts": [
            "fuck-u-code=fuck_u_code.cli.main:main",
            "fuc=fuck_u_code.cli.main:main",  # 简短别名
        ],
    },
    include_package_data=True,
    package_data={
        "fuck_u_code": [
            "i18n/*.json", 
            "templates/*.md",
            "data/*.yaml"
        ],
    },
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/fuck-u-code/fuck-u-code-python/issues",
        "Source": "https://github.com/fuck-u-code/fuck-u-code-python",
        "Documentation": "https://fuck-u-code-python.readthedocs.io",
        "Changelog": "https://github.com/fuck-u-code/fuck-u-code-python/blob/main/CHANGELOG.md",
    },
)