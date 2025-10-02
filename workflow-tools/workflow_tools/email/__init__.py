"""
邮件处理模块
"""

from .outlook import OutlookClient
from .base.generic_imap_client import GenericIMAPClient
from .qq import QQIMAPClient

__all__ = ["OutlookClient", "GenericIMAPClient", "QQIMAPClient"]


