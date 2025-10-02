"""
异常定义模块
"""

from .ai_exceptions import AIClientError, GeminiAPIError, OpenAIAPIError
from .notes_exceptions import NotesClientError, NotionAPIError
from .storage_exceptions import StorageClientError, R2StorageError, S3StorageError
from .email_exceptions import EmailClientError, OutlookAPIError, SMTPError, EmailAuthError, EmailConnectionError

__all__ = [
    "AIClientError",
    "GeminiAPIError",
    "OpenAIAPIError",
    "NotesClientError",
    "NotionAPIError",
    "StorageClientError",
    "R2StorageError",
    "S3StorageError",
    "EmailClientError",
    "OutlookAPIError",
    "SMTPError",
    "EmailAuthError",
    "EmailConnectionError"
]