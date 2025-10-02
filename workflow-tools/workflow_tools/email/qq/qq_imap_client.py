"""
QQ邮箱IMAP客户端实现
继承通用IMAP客户端，提供QQ邮箱的预配置
"""

from typing import Optional
from ..base.generic_imap_client import GenericIMAPClient


class QQIMAPClient(GenericIMAPClient):
    """
    QQ邮箱IMAP客户端
    
    预配置了QQ邮箱的服务器地址和端口
    
    使用说明：
    1. 登录QQ邮箱网页版
    2. 进入"设置" -> "账户"
    3. 开启"IMAP/SMTP服务"或"POP3/SMTP服务"
    4. 生成授权码（不是QQ密码！）
    5. 使用授权码作为password参数
    
    示例：
        client = QQIMAPClient(
            email_address="your_email@qq.com",
            password="your_authorization_code"
        )
        client.connect()
        emails = client.fetch_emails(subject="每日总结")
    """
    
    # QQ邮箱IMAP配置
    DEFAULT_IMAP_SERVER = "imap.qq.com"
    DEFAULT_IMAP_PORT = 993
    
    # QQ邮箱SMTP配置
    DEFAULT_SMTP_SERVER = "smtp.qq.com"
    DEFAULT_SMTP_PORT = 587  # 使用STARTTLS
    DEFAULT_SMTP_SSL_PORT = 465  # 使用SSL
    
    def __init__(
        self,
        email_address: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl_for_smtp: bool = False
    ):
        """
        初始化QQ邮箱客户端

        Args:
            email_address: QQ邮箱地址（如: xxxxx@qq.com）
            password: QQ邮箱授权码（不是QQ密码！）
            use_ssl_for_smtp: SMTP是否使用SSL（True=465端口，False=587端口）
        """
        # 根据SSL配置选择端口
        smtp_port = self.DEFAULT_SMTP_SSL_PORT if use_ssl_for_smtp else self.DEFAULT_SMTP_PORT
        
        # 调用父类初始化
        super().__init__(
            email_address=email_address,
            password=password,
            imap_server=self.DEFAULT_IMAP_SERVER,
            imap_port=self.DEFAULT_IMAP_PORT,
            smtp_server=self.DEFAULT_SMTP_SERVER,
            smtp_port=smtp_port,
            use_ssl_for_smtp=use_ssl_for_smtp
        )

