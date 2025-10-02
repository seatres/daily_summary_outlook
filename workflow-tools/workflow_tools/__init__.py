"""
workflow-tools: 可重用的API工具包

提供标准化的API访问接口，支持AI模型、笔记工具、存储服务、邮件处理、调度器等。
"""

__version__ = "0.1.0"
__author__ = "Research Team"

# 导出主要模块
from . import ai_models
from . import notes
from . import storage
from . import email
from . import scheduler
from . import utils
from . import exceptions

__all__ = [
    "ai_models",
    "notes",
    "storage",
    "email",
    "scheduler",
    "utils",
    "exceptions"
]