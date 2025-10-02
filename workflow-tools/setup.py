"""
workflow-tools: 可重用的API工具包
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="workflow-tools",
    version="0.1.0",
    author="Research Team",
    author_email="research@example.com",
    description="可重用的API访问工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
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