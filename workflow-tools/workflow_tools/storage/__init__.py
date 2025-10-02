"""
存储服务模块
"""

from .base.storage_base import StorageClientBase, StorageResult
from .cloudflare_r2.r2_client import R2Client

__all__ = [
    "StorageClientBase",
    "StorageResult",
    "R2Client"
]