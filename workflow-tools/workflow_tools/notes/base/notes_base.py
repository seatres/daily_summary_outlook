"""
笔记客户端基类定义
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class NotesResult:
    """笔记操作结果基类"""
    success: bool = True
    page_id: Optional[str] = None
    page_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class NotesClientBase(ABC):
    """笔记客户端抽象基类"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化笔记客户端

        Args:
            token: 访问令牌，如果为None则从环境变量获取
        """
        if token is None:
            token = os.getenv("NOTES_TOKEN")
        self.token = token

    @abstractmethod
    def create_page(
        self,
        title: str,
        content: str,
        pdf_url: Optional[str] = None,
        database_id: Optional[str] = None
    ) -> NotesResult:
        """
        创建页面

        Args:
            title: 页面标题
            content: 页面内容
            pdf_url: PDF文件链接
            database_id: 数据库ID

        Returns:
            创建结果
        """
        raise NotImplementedError()

    @abstractmethod
    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> NotesResult:
        """
        更新页面

        Args:
            page_id: 页面ID
            title: 新标题
            content: 新内容

        Returns:
            更新结果
        """
        raise NotImplementedError()

    @abstractmethod
    def get_page(self, page_id: str) -> NotesResult:
        """
        获取页面

        Args:
            page_id: 页面ID

        Returns:
            页面信息
        """
        raise NotImplementedError()