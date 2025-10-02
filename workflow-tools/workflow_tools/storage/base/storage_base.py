"""
存储客户端基类定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, Union


@dataclass
class StorageResult:
    """存储操作结果基类"""
    success: bool = True
    file_url: Optional[str] = None
    file_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class StorageClientBase(ABC):
    """存储客户端抽象基类"""

    def __init__(self, **kwargs):
        """
        初始化存储客户端

        Args:
            **kwargs: 存储配置参数
        """
        pass

    @abstractmethod
    def upload_file(
        self,
        file_path: Union[str, Path],
        object_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> StorageResult:
        """
        上传文件

        Args:
            file_path: 本地文件路径
            object_name: 远程对象名称，如果为None则使用文件名
            metadata: 文件元数据

        Returns:
            上传结果
        """
        pass

    @abstractmethod
    def download_file(
        self,
        object_name: str,
        local_path: Union[str, Path]
    ) -> StorageResult:
        """
        下载文件

        Args:
            object_name: 远程对象名称
            local_path: 本地保存路径

        Returns:
            下载结果
        """
        pass

    @abstractmethod
    def delete_file(self, object_name: str) -> StorageResult:
        """
        删除文件

        Args:
            object_name: 远程对象名称

        Returns:
            删除结果
        """
        pass

    @abstractmethod
    def get_file_url(self, object_name: str) -> str:
        """
        获取文件访问URL

        Args:
            object_name: 远程对象名称

        Returns:
            文件访问URL
        """
        pass

    @abstractmethod
    def list_files(self, prefix: Optional[str] = None) -> StorageResult:
        """
        列出文件

        Args:
            prefix: 文件名前缀过滤

        Returns:
            文件列表结果
        """
        pass