"""
Outlook邮件客户端实现
使用Microsoft Graph API进行安全的邮件读取
使用SMTP进行邮件发送
"""

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import time

try:
    from msal import ConfidentialClientApplication
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from ..base.email_base import EmailClientBase, EmailResult, EmailMessage
from ...exceptions.email_exceptions import (
    OutlookAPIError,
    SMTPError,
    EmailAuthError,
    EmailConnectionError
)
from ...utils.config_manager import ConfigManager


class OutlookClient(EmailClientBase):
    """
    Outlook邮件客户端
    
    读取邮件: 使用Microsoft Graph API (OAuth认证，最安全)
    发送邮件: 使用SMTP协议
    """

    # Microsoft Graph API 端点
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    AUTHORITY = "https://login.microsoftonline.com/{tenant_id}"
    SCOPE = ["https://graph.microsoft.com/.default"]

    # SMTP配置
    SMTP_SERVER = "smtp-mail.outlook.com"
    SMTP_PORT = 587

    def __init__(
        self,
        email_address: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
        smtp_password: Optional[str] = None
    ):
        """
        初始化Outlook客户端

        Args:
            email_address: 邮箱地址
            client_id: Azure应用客户端ID (用于Graph API读取)
            client_secret: Azure应用客户端密钥 (用于Graph API读取)
            tenant_id: Azure租户ID (用于Graph API读取)
            smtp_password: SMTP应用专用密码 (用于发送邮件)
        """
        super().__init__()

        # 检查依赖
        if not MSAL_AVAILABLE:
            raise ImportError("请安装msal: pip install msal")
        if not REQUESTS_AVAILABLE:
            raise ImportError("请安装requests: pip install requests")

        # 获取配置
        self.email_address = email_address or ConfigManager.get_required_env('OUTLOOK_EMAIL')
        self.client_id = client_id or ConfigManager.get_required_env('OUTLOOK_CLIENT_ID')
        self.client_secret = client_secret or ConfigManager.get_required_env('OUTLOOK_CLIENT_SECRET')
        self.tenant_id = tenant_id or ConfigManager.get_required_env('OUTLOOK_TENANT_ID')
        self.smtp_password = smtp_password or ConfigManager.get_required_env('OUTLOOK_SMTP_PASSWORD')

        # Graph API认证
        self.app = None
        self.access_token = None

        # 日志配置
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        连接到Outlook (获取访问令牌)

        Returns:
            是否连接成功
        """
        try:
            # 创建MSAL应用
            authority = self.AUTHORITY.format(tenant_id=self.tenant_id)
            self.app = ConfidentialClientApplication(
                self.client_id,
                authority=authority,
                client_credential=self.client_secret
            )

            # 获取访问令牌
            result = self.app.acquire_token_for_client(scopes=self.SCOPE)

            if "access_token" in result:
                self.access_token = result["access_token"]
                self.logger.info("成功连接到Outlook Graph API")
                return True
            else:
                error_msg = result.get("error_description", "未知错误")
                self.logger.error(f"获取访问令牌失败: {error_msg}")
                raise EmailAuthError(f"认证失败: {error_msg}")

        except Exception as e:
            self.logger.error(f"连接Outlook失败: {str(e)}")
            raise EmailConnectionError(f"连接失败: {str(e)}")

    def disconnect(self) -> None:
        """断开连接（清除令牌）"""
        self.access_token = None
        self.app = None
        self.logger.info("已断开Outlook连接")

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
        if not self.access_token:
            self.connect()

        try:
            # 构建Graph API查询
            url = f"{self.GRAPH_API_ENDPOINT}/users/{self.email_address}/messages"

            # 构建过滤条件
            filters = []
            if subject:
                filters.append(f"subject eq '{subject}'")
            if sender:
                filters.append(f"from/emailAddress/address eq '{sender}'")
            if since_date:
                # 转换为UTC时间并格式化为ISO 8601
                utc_date = since_date.astimezone(timezone.utc)
                date_str = utc_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                filters.append(f"receivedDateTime ge {date_str}")

            # 构建查询参数
            params = {
                "$orderby": "receivedDateTime desc",
                "$select": "subject,from,toRecipients,body,receivedDateTime,id,hasAttachments,isRead"
            }

            if filters:
                params["$filter"] = " and ".join(filters)

            if limit:
                params["$top"] = limit

            # 发送请求
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                messages = self._parse_messages(data.get("value", []))
                
                self.logger.info(f"成功获取 {len(messages)} 封邮件")
                
                return EmailResult(
                    success=True,
                    messages=messages,
                    metadata={"total_count": len(messages)}
                )
            else:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return EmailResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"获取邮件失败: {str(e)}"
            self.logger.error(error_msg)
            return EmailResult(success=False, error=error_msg)

    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        使用SMTP发送邮件

        Args:
            to: 收件人列表
            subject: 邮件主题
            body: 邮件正文（纯文本）
            cc: 抄送列表
            bcc: 密送列表

        Returns:
            是否发送成功
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 创建邮件
                msg = MIMEMultipart()
                msg['From'] = self.email_address
                msg['To'] = ', '.join(to)
                msg['Subject'] = subject

                if cc:
                    msg['Cc'] = ', '.join(cc)

                # 添加正文
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                # 连接SMTP服务器
                with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT, timeout=30) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    
                    # 登录
                    server.login(self.email_address, self.smtp_password)

                    # 发送邮件
                    recipients = to + (cc or []) + (bcc or [])
                    server.send_message(msg, to_addrs=recipients)

                self.logger.info(f"成功发送邮件到 {', '.join(to)}")
                return True

            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"SMTP认证失败: {str(e)}"
                self.logger.error(error_msg)
                raise EmailAuthError(error_msg)

            except smtplib.SMTPException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"SMTP发送失败，{wait_time}秒后重试: {str(e)}")
                    time.sleep(wait_time)
                else:
                    error_msg = f"SMTP发送失败（已重试{max_retries}次）: {str(e)}"
                    self.logger.error(error_msg)
                    raise SMTPError(error_msg)

            except Exception as e:
                error_msg = f"发送邮件时发生未知错误: {str(e)}"
                self.logger.error(error_msg)
                raise SMTPError(error_msg)

        return False

    def _parse_messages(self, raw_messages: List[dict]) -> List[EmailMessage]:
        """
        解析Graph API返回的邮件数据

        Args:
            raw_messages: 原始邮件数据

        Returns:
            解析后的邮件消息列表
        """
        messages = []

        for raw_msg in raw_messages:
            try:
                # 解析发件人
                sender = raw_msg.get("from", {}).get("emailAddress", {}).get("address", "")

                # 解析收件人
                recipients = [
                    recipient.get("emailAddress", {}).get("address", "")
                    for recipient in raw_msg.get("toRecipients", [])
                ]

                # 解析接收时间
                received_time_str = raw_msg.get("receivedDateTime", "")
                received_time = datetime.fromisoformat(received_time_str.replace('Z', '+00:00'))

                # 解析邮件正文（获取纯文本内容）
                body_data = raw_msg.get("body", {})
                body = body_data.get("content", "")

                # 创建EmailMessage对象
                message = EmailMessage(
                    subject=raw_msg.get("subject", ""),
                    sender=sender,
                    recipients=recipients,
                    body=body,
                    received_time=received_time,
                    message_id=raw_msg.get("id"),
                    has_attachments=raw_msg.get("hasAttachments", False),
                    is_read=raw_msg.get("isRead", False)
                )

                messages.append(message)

            except Exception as e:
                self.logger.warning(f"解析邮件失败: {str(e)}")
                continue

        return messages


