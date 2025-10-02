"""
Outlook IMAP邮件客户端实现
使用IMAP协议读取邮件,使用SMTP协议发送邮件
适用于个人Microsoft账户(如: @outlook.com, @hotmail.com)
"""

import logging
import smtplib
import imaplib
import email
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import Optional, List
import time

from ..base.email_base import EmailClientBase, EmailResult, EmailMessage
from ...exceptions.email_exceptions import (
    SMTPError,
    EmailAuthError,
    EmailConnectionError
)
from ...utils.config_manager import ConfigManager


class OutlookIMAPClient(EmailClientBase):
    """
    Outlook IMAP邮件客户端
    
    读取邮件: 使用IMAP协议
    发送邮件: 使用SMTP协议
    
    适用于个人Microsoft账户(outlook.com, hotmail.com等)
    """

    # IMAP配置
    IMAP_SERVER = "outlook.office365.com"
    IMAP_PORT = 993
    
    # SMTP配置
    SMTP_SERVER = "smtp-mail.outlook.com"
    SMTP_PORT = 587

    def __init__(
        self,
        email_address: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        初始化Outlook IMAP客户端

        Args:
            email_address: 邮箱地址
            password: IMAP/SMTP应用专用密码(不是账号密码!)
        """
        super().__init__()

        # 获取配置
        self.email_address = email_address or ConfigManager.get_required_env('OUTLOOK_EMAIL')
        self.password = password or ConfigManager.get_required_env('OUTLOOK_IMAP_PASSWORD')

        # IMAP连接
        self.imap_conn = None

        # 日志配置
        self.logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        """
        连接到Outlook IMAP服务器

        Returns:
            是否连接成功
        """
        try:
            # 连接IMAP服务器
            self.logger.info("正在连接到IMAP服务器...")
            self.imap_conn = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
            
            # 登录
            self.logger.info("正在登录...")
            self.imap_conn.login(self.email_address, self.password)
            
            self.logger.info("成功连接到Outlook IMAP")
            return True

        except imaplib.IMAP4.error as e:
            error_msg = f"IMAP认证失败: {str(e)}"
            self.logger.error(error_msg)
            raise EmailAuthError(error_msg) from e
        except Exception as e:
            error_msg = f"连接IMAP服务器失败: {str(e)}"
            self.logger.error(error_msg)
            raise EmailConnectionError(error_msg) from e

    def disconnect(self) -> None:
        """断开IMAP连接"""
        if self.imap_conn:
            try:
                self.imap_conn.close()
                self.imap_conn.logout()
                self.logger.info("已断开IMAP连接")
            except Exception as e:
                self.logger.warning("断开连接时发生错误: %s", str(e))
            finally:
                self.imap_conn = None

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
            subject: 邮件主题过滤(完全匹配)
            sender: 发件人过滤(完全匹配)
            since_date: 起始时间过滤
            limit: 最大返回数量

        Returns:
            邮件结果
        """
        if not self.imap_conn:
            self.connect()

        try:
            # 选择收件箱
            self.imap_conn.select('INBOX')

            # 构建IMAP搜索条件
            search_criteria = []
            
            if since_date:
                # IMAP日期格式: DD-Mon-YYYY (如: 01-Jan-2024)
                date_str = since_date.strftime('%d-%b-%Y')
                search_criteria.append(f'SINCE {date_str}')
            
            if sender:
                # IMAP格式需要用引号包裹
                search_criteria.append(f'FROM "{sender}"')
            
            if subject:
                # IMAP格式需要用引号包裹
                search_criteria.append(f'SUBJECT "{subject}"')

            # 执行搜索
            if search_criteria:
                search_string = ' '.join(search_criteria)
            else:
                search_string = 'ALL'
            
            self.logger.debug("IMAP搜索条件: %s", search_string)
            
            # 搜索邮件
            status, messages = self.imap_conn.search(None, search_string)
            
            if status != 'OK':
                error_msg = f"IMAP搜索失败: {status}"
                self.logger.error(error_msg)
                return EmailResult(success=False, error=error_msg)

            # 获取邮件ID列表
            message_ids = messages[0].split()
            
            # 如果有limit,只获取最新的N封
            if limit and len(message_ids) > limit:
                message_ids = message_ids[-limit:]
            
            # 反转列表,使最新的邮件在前
            message_ids = list(reversed(message_ids))
            
            self.logger.info("找到 %d 封符合条件的邮件", len(message_ids))

            # 获取邮件详情
            email_messages = []
            for msg_id in message_ids:
                try:
                    # 获取邮件
                    status, msg_data = self.imap_conn.fetch(msg_id, '(RFC822)')
                    
                    if status != 'OK':
                        self.logger.warning("获取邮件 %s 失败", msg_id)
                        continue
                    
                    # 解析邮件
                    raw_email = msg_data[0][1]
                    email_msg = email.message_from_bytes(raw_email)
                    
                    # 提取邮件信息
                    parsed_msg = self._parse_email(email_msg, msg_id.decode())
                    
                    if parsed_msg:
                        email_messages.append(parsed_msg)
                    
                except Exception as e:
                    self.logger.warning("解析邮件 %s 失败: %s", msg_id, str(e))
                    continue

            return EmailResult(
                success=True,
                messages=email_messages,
                metadata={"total_count": len(email_messages)}
            )

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
            body: 邮件正文(纯文本)
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
                    server.login(self.email_address, self.password)

                    # 发送邮件
                    recipients = to + (cc or []) + (bcc or [])
                    server.send_message(msg, to_addrs=recipients)

                self.logger.info("成功发送邮件到 %s", ', '.join(to))
                return True

            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"SMTP认证失败: {str(e)}"
                self.logger.error(error_msg)
                raise EmailAuthError(error_msg) from e

            except smtplib.SMTPException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning("SMTP发送失败,%d秒后重试: %s", wait_time, str(e))
                    time.sleep(wait_time)
                else:
                    error_msg = f"SMTP发送失败(已重试{max_retries}次): {str(e)}"
                    self.logger.error(error_msg)
                    raise SMTPError(error_msg) from e

            except Exception as e:
                error_msg = f"发送邮件时发生未知错误: {str(e)}"
                self.logger.error(error_msg)
                raise SMTPError(error_msg) from e

        return False

    def _parse_email(self, email_msg: email.message.Message, message_id: str) -> Optional[EmailMessage]:
        """
        解析IMAP邮件

        Args:
            email_msg: 原始邮件对象
            message_id: 邮件ID

        Returns:
            解析后的邮件消息
        """
        try:
            # 解析主题
            subject = self._decode_header(email_msg.get('Subject', ''))
            
            # 解析发件人
            from_header = email_msg.get('From', '')
            sender = self._extract_email_address(from_header)
            
            # 解析收件人
            to_header = email_msg.get('To', '')
            recipients = [self._extract_email_address(to_header)]
            
            # 解析日期
            date_str = email_msg.get('Date', '')
            received_time = self._parse_date(date_str)
            
            # 解析邮件正文
            body = self._get_email_body(email_msg)
            
            # 检查是否有附件
            has_attachments = any(part.get_content_disposition() == 'attachment' 
                                 for part in email_msg.walk())

            return EmailMessage(
                subject=subject,
                sender=sender,
                recipients=recipients,
                body=body,
                received_time=received_time,
                message_id=message_id,
                has_attachments=has_attachments,
                is_read=False  # IMAP不容易判断是否已读,默认为False
            )

        except Exception as e:
            self.logger.warning("解析邮件失败: %s", str(e))
            return None

    @staticmethod
    def _decode_header(header: str) -> str:
        """
        解码邮件头

        Args:
            header: 邮件头字符串

        Returns:
            解码后的字符串
        """
        if not header:
            return ""
        
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                if encoding:
                    try:
                        decoded_parts.append(part.decode(encoding))
                    except (UnicodeDecodeError, LookupError):
                        decoded_parts.append(part.decode('utf-8', errors='ignore'))
                else:
                    decoded_parts.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded_parts.append(str(part))
        
        return ''.join(decoded_parts)

    @staticmethod
    def _extract_email_address(header: str) -> str:
        """
        从邮件头中提取邮箱地址

        Args:
            header: 邮件头(如: "Name <email@example.com>")

        Returns:
            邮箱地址
        """
        if '<' in header and '>' in header:
            start = header.index('<') + 1
            end = header.index('>')
            return header[start:end]
        return header.strip()

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """
        解析邮件日期

        Args:
            date_str: 日期字符串

        Returns:
            datetime对象
        """
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            # 如果解析失败,返回当前时间
            return datetime.now(timezone.utc)

    def _get_email_body(self, email_msg: email.message.Message) -> str:
        """
        获取邮件正文

        Args:
            email_msg: 邮件对象

        Returns:
            邮件正文文本
        """
        body = ""
        
        if email_msg.is_multipart():
            # 多部分邮件,查找文本部分
            for part in email_msg.walk():
                content_type = part.get_content_type()
                content_disposition = part.get_content_disposition()
                
                # 跳过附件
                if content_disposition == 'attachment':
                    continue
                
                # 优先获取纯文本
                if content_type == 'text/plain':
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        break
                    except Exception as e:
                        self.logger.warning("解析文本正文失败: %s", str(e))
                
                # 如果没有纯文本,获取HTML(可选)
                elif content_type == 'text/html' and not body:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        html_body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        # 简单移除HTML标签
                        import re
                        body = re.sub(r'<[^>]+>', '', html_body)
                    except Exception as e:
                        self.logger.warning("解析HTML正文失败: %s", str(e))
        else:
            # 单部分邮件
            try:
                charset = email_msg.get_content_charset() or 'utf-8'
                body = email_msg.get_payload(decode=True).decode(charset, errors='ignore')
            except Exception as e:
                self.logger.warning("解析邮件正文失败: %s", str(e))
        
        return body.strip()

