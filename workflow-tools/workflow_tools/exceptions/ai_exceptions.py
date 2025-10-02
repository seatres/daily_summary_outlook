"""
AI相关异常定义
"""


class AIClientError(Exception):
    """AI客户端基础异常"""
    pass


class GeminiAPIError(AIClientError):
    """Gemini API异常"""
    pass


class OpenAIAPIError(AIClientError):
    """OpenAI API异常"""
    pass


class AnthropicAPIError(AIClientError):
    """Anthropic API异常"""
    pass