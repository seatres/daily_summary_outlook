"""
邮件相关异常定义
"""


class EmailClientError(Exception):
    """邮件客户端基础异常"""
    pass


class OutlookAPIError(EmailClientError):
    """Outlook API异常"""
    pass


class SMTPError(EmailClientError):
    """SMTP发送异常"""
    pass


class EmailAuthError(EmailClientError):
    """邮件认证异常"""
    pass


class EmailConnectionError(EmailClientError):
    """邮件连接异常"""
    pass

