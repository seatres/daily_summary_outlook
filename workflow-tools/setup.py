"""
workflow-tools: 可重用的API工具包
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys
import importlib.util


class PostInstallCommand(install):
    """安装后执行依赖验证"""
    def run(self):
        install.run(self)
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """验证关键依赖的安装"""
        # 定义模块与其功能的映射
        dependency_map = {
            'email': [
                ('msal', 'Microsoft身份认证'),
                ('requests', 'HTTP请求')
            ],
            'ai': [
                ('google.generativeai', 'Gemini AI')
            ],
            'notes': [
                ('notion_client', 'Notion API')
            ],
            'storage': [
                ('boto3', 'AWS S3/Cloudflare R2')
            ],
            'scheduler': [
                ('apscheduler', '任务调度')
            ]
        }
        
        # 检查已安装的可选依赖
        print("\n=== 依赖边界检查 ===")
        for feature, modules in dependency_map.items():
            for module_name, description in modules:
                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    print(f"⚠️  [{feature}] 缺少: {module_name} ({description})")
                    print(f"   提示: pip install workflow-tools[{feature}]")
                else:
                    print(f"✓  [{feature}] 已安装: {module_name}")
        
        print("===================\n")


class PostDevelopCommand(develop):
    """开发模式安装后执行依赖验证"""
    def run(self):
        develop.run(self)
        PostInstallCommand._validate_dependencies(self)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="workflow-tools",
    version="0.1.1",
    author="Research Team",
    author_email="research@example.com",
    description="可重用的API访问工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typing-extensions>=4.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        'ai': ['google-generativeai>=0.3.0'],
        'notes': ['notion-client>=2.0.0'],
        'storage': ['boto3>=1.26.0', 'botocore>=1.29.0'],
        'email': ['msal>=1.20.0', 'requests>=2.28.0'],
        'scheduler': ['APScheduler>=3.10.0', 'pytz>=2023.3'],
        'utils': ['ratelimit>=2.2.0'],
        'dev': ['pytest>=7.0.0', 'pytest-mock>=3.0.0'],
        'all': [
            'google-generativeai>=0.3.0',
            'notion-client>=2.0.0',
            'boto3>=1.26.0',
            'botocore>=1.29.0',
            'msal>=1.20.0',
            'requests>=2.28.0',
            'APScheduler>=3.10.0',
            'pytz>=2023.3',
            'ratelimit>=2.2.0'
        ]
    },
)