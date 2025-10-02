"""
AI模型模块
"""

from .base.ai_client_base import AIClientBase, AIResult
from .gemini.gemini_client import GeminiClient

__all__ = [
    "AIClientBase",
    "AIResult",
    "GeminiClient"
]