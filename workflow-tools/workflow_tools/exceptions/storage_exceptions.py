"""
存储相关异常定义
"""


class StorageClientError(Exception):
    """存储客户端基础异常"""
    pass


class R2StorageError(StorageClientError):
    """Cloudflare R2存储异常"""
    pass


class S3StorageError(StorageClientError):
    """AWS S3存储异常"""
    pass


class LocalStorageError(StorageClientError):
    """本地存储异常"""
    pass