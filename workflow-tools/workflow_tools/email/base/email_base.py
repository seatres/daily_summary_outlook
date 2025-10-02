"""
邮件客户端基类定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class EmailMessage:
    """邮件消息数据类"""
    subject: str
    sender: str
    recipients: List[str]
    body: str
    received_time: datetime
    message_id: Optional[str] = None
    has_attachments: bool = False
    is_read: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        return f"Email from {self.sender}: {self.subject} ({self.received_time})"


@dataclass
class EmailResult:
    """邮件操作结果"""
    success: bool = True
    messages: List[EmailMessage] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmailClientBase(ABC):
    """邮件客户端抽象基类"""

    def __init__(self):
        """初始化邮件客户端"""
        pass

    @abstractmethod
    def connect(self) -> bool:
        """
        连接到邮件服务器

        Returns:
            是否连接成功
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开与邮件服务器的连接"""
        pass

    @abstractmethod
    def fetch_emails(
        self,
        subject: Optional[str] = None,
        sender: Optional[str] = None,
        since_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> EmailResult:
        """
        获取邮件列表

        Args:
            subject: 邮件主题过滤（完全匹配）
            sender: 发件人过滤（完全匹配）
            since_date: 起始时间过滤
            limit: 最大返回数量

        Returns:
            邮件结果
        """
        pass

    @abstractmethod
    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        发送邮件

        Args:
            to: 收件人列表
            subject: 邮件主题
            body: 邮件正文
            cc: 抄送列表
            bcc: 密送列表

        Returns:
            是否发送成功
        """
        pass


