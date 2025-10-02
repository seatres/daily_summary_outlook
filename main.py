"""
每日总结邮件自动化工作流主程序

功能：
1. 每晚10点（东八区）从Outlook读取最近24小时内的"每日总结"邮件
2. 使用Gemini 2.5 Pro进行分析和总结
3. 将结果发送到指定邮箱
"""

import sys
import signal
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import List

# 添加workflow-tools到Python路径
sys.path.insert(0, str(Path(__file__).parent / "workflow-tools"))

from workflow_tools.email.outlook import OutlookClient
from workflow_tools.ai_models.gemini import GeminiClient
from workflow_tools.scheduler import APSchedulerClient
from workflow_tools.utils.config_manager import ConfigManager

import config


class DailySummaryWorkflow:
    """每日总结工作流"""

    def __init__(self):
        """初始化工作流"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # 初始化客户端
        self.email_client = None
        self.ai_client = None
        self.scheduler = None

        self.logger.info("=" * 80)
        self.logger.info("每日总结工作流启动")
        self.logger.info("=" * 80)

    def setup_logging(self):
        """配置日志系统"""
        # 创建日志处理器
        handlers = []

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)

        # 文件处理器
        log_file = config.LOG_DIR / f"workflow_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.LOG_FILE_MAX_BYTES,
            backupCount=config.LOG_FILE_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        file_formatter = logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

        # 配置根日志记录器
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            handlers=handlers
        )

    def initialize_clients(self):
        """初始化所有客户端"""
        try:
            self.logger.info("正在初始化客户端...")

            # 初始化邮件客户端
            self.email_client = OutlookClient(
                email_address=config.OUTLOOK_EMAIL,
                client_id=config.OUTLOOK_CLIENT_ID,
                client_secret=config.OUTLOOK_CLIENT_SECRET,
                tenant_id=config.OUTLOOK_TENANT_ID,
                smtp_password=config.OUTLOOK_SMTP_PASSWORD
            )
            self.logger.info("✓ 邮件客户端初始化成功")

            # 初始化AI客户端
            self.ai_client = GeminiClient(
                api_key=config.GEMINI_API_KEY,
                model_name=config.GEMINI_MODEL_NAME
            )
            self.logger.info("✓ AI客户端初始化成功")

            # 初始化调度器
            self.scheduler = APSchedulerClient(timezone=config.TIMEZONE)
            self.logger.info("✓ 调度器初始化成功")

            return True

        except Exception as e:
            self.logger.error(f"✗ 客户端初始化失败: {str(e)}")
            return False

    def process_daily_summary(self):
        """处理每日总结的主要逻辑"""
        self.logger.info("=" * 80)
        self.logger.info(f"开始执行每日总结任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)

        try:
            # 1. 读取邮件
            self.logger.info("步骤 1/4: 读取邮件...")
            emails = self._fetch_emails()

            if not emails:
                self.logger.info("未找到符合条件的邮件，本次任务结束")
                self._save_history(success=True, email_count=0, summary="无邮件")
                return

            self.logger.info(f"成功读取 {len(emails)} 封邮件")

            # 2. 整理邮件内容
            self.logger.info("步骤 2/4: 整理邮件内容...")
            email_contents = self._organize_emails(emails)

            # 3. AI分析
            self.logger.info("步骤 3/4: 使用Gemini AI进行分析...")
            analysis_result = self._analyze_with_ai(email_contents)

            if not analysis_result:
                self.logger.error("AI分析失败，本次任务结束")
                self._save_history(success=False, email_count=len(emails), error="AI分析失败")
                return

            # 4. 发送结果
            self.logger.info("步骤 4/4: 发送分析结果...")
            success = self._send_summary_email(analysis_result)

            if success:
                self.logger.info("✓ 每日总结任务完成！")
                self._save_history(
                    success=True,
                    email_count=len(emails),
                    summary=analysis_result,
                    emails=emails
                )
            else:
                self.logger.error("✗ 发送邮件失败")
                self._save_history(
                    success=False,
                    email_count=len(emails),
                    error="发送邮件失败"
                )

        except Exception as e:
            self.logger.error(f"处理每日总结时发生错误: {str(e)}", exc_info=True)
            self._save_history(success=False, error=str(e))

        finally:
            self.logger.info("=" * 80)

    def _fetch_emails(self) -> List:
        """
        获取符合条件的邮件

        Returns:
            邮件列表
        """
        max_retries = config.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                # 连接到Outlook
                self.email_client.connect()

                # 计算时间范围（最近24小时）
                since_date = datetime.now() - timedelta(hours=config.EMAIL_SEARCH_HOURS)

                # 获取邮件
                result = self.email_client.fetch_emails(
                    subject=config.EMAIL_FILTER_SUBJECT,
                    sender=config.EMAIL_FILTER_SENDER,
                    since_date=since_date
                )

                if result.success:
                    return result.messages
                else:
                    self.logger.error(f"获取邮件失败: {result.error}")
                    if attempt < max_retries - 1:
                        self.logger.info(f"将在{config.RETRY_DELAY}秒后重试...")
                        import time
                        time.sleep(config.RETRY_DELAY)
                    continue

            except Exception as e:
                self.logger.error(f"获取邮件时发生异常: {str(e)}")
                if attempt < max_retries - 1:
                    self.logger.info(f"将在{config.RETRY_DELAY}秒后重试...")
                    import time
                    time.sleep(config.RETRY_DELAY)
                continue

        self.logger.error(f"获取邮件失败（已重试{max_retries}次）")
        return []

    def _organize_emails(self, emails: List) -> str:
        """
        整理邮件内容（按时间顺序）

        Args:
            emails: 邮件列表

        Returns:
            整理后的内容字符串
        """
        # 按接收时间排序（从早到晚）
        sorted_emails = sorted(emails, key=lambda x: x.received_time)

        # 格式化邮件内容
        organized_content = []
        for i, email in enumerate(sorted_emails, 1):
            content = f"""
{'=' * 60}
邮件 {i}/{len(sorted_emails)}
时间: {email.received_time.strftime('%Y-%m-%d %H:%M:%S')}
发件人: {email.sender}
主题: {email.subject}
{'=' * 60}

{email.body}

"""
            organized_content.append(content)

        return "\n".join(organized_content)

    def _analyze_with_ai(self, email_contents: str) -> str:
        """
        使用AI分析邮件内容

        Args:
            email_contents: 邮件内容

        Returns:
            分析结果
        """
        max_retries = config.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                # 构建提示词
                prompt = config.AI_ANALYSIS_PROMPT.format(email_contents=email_contents)

                # 调用Gemini AI
                result = self.ai_client.generate_content(prompt)

                if result.success:
                    return result.content
                else:
                    self.logger.error(f"AI分析失败: {result.error}")
                    if attempt < max_retries - 1:
                        self.logger.info(f"将在{config.RETRY_DELAY}秒后重试...")
                        import time
                        time.sleep(config.RETRY_DELAY)
                    continue

            except Exception as e:
                self.logger.error(f"AI分析时发生异常: {str(e)}")
                if attempt < max_retries - 1:
                    self.logger.info(f"将在{config.RETRY_DELAY}秒后重试...")
                    import time
                    time.sleep(config.RETRY_DELAY)
                continue

        self.logger.error(f"AI分析失败（已重试{max_retries}次）")
        return ""

    def _send_summary_email(self, summary: str) -> bool:
        """
        发送总结邮件

        Args:
            summary: 总结内容

        Returns:
            是否发送成功
        """
        max_retries = config.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                # 构建邮件主题
                today = datetime.now().strftime('%Y-%m-%d')
                subject = config.EMAIL_SUBJECT_TEMPLATE.format(date=today)

                # 发送邮件
                success = self.email_client.send_email(
                    to=[config.SUMMARY_RECIPIENT],
                    subject=subject,
                    body=summary
                )

                if success:
                    return True
                else:
                    if attempt < max_retries - 1:
                        self.logger.info(f"将在{config.RETRY_DELAY}秒后重试...")
                        import time
                        time.sleep(config.RETRY_DELAY)
                    continue

            except Exception as e:
                self.logger.error(f"发送邮件时发生异常: {str(e)}")
                if attempt < max_retries - 1:
                    self.logger.info(f"将在{config.RETRY_DELAY}秒后重试...")
                    import time
                    time.sleep(config.RETRY_DELAY)
                continue

        self.logger.error(f"发送邮件失败（已重试{max_retries}次）")
        return False

    def _save_history(self, success: bool, email_count: int = 0, summary: str = "", 
                     emails: List = None, error: str = ""):
        """
        保存历史记录

        Args:
            success: 是否成功
            email_count: 邮件数量
            summary: 总结内容
            emails: 邮件列表
            error: 错误信息
        """
        if not config.SAVE_HISTORY:
            return

        try:
            timestamp = datetime.now()
            history_file = config.HISTORY_DIR / f"history_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

            history_data = {
                "timestamp": timestamp.isoformat(),
                "success": success,
                "email_count": email_count
            }

            # 根据历史记录级别保存不同详细程度的信息
            if config.HISTORY_LEVEL == "minimal":
                # 只保存基本信息
                if error:
                    history_data["error"] = error

            elif config.HISTORY_LEVEL == "normal":
                # 保存邮件标题和分析结果摘要
                if emails:
                    history_data["email_subjects"] = [email.subject for email in emails]
                if summary:
                    history_data["summary_preview"] = summary[:500] + "..." if len(summary) > 500 else summary
                if error:
                    history_data["error"] = error

            elif config.HISTORY_LEVEL == "detailed":
                # 保存完整信息
                if emails:
                    history_data["emails"] = [
                        {
                            "subject": email.subject,
                            "sender": email.sender,
                            "received_time": email.received_time.isoformat(),
                            "body": email.body
                        }
                        for email in emails
                    ]
                if summary:
                    history_data["summary"] = summary
                if error:
                    history_data["error"] = error

            # 保存到文件
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"历史记录已保存: {history_file}")

        except Exception as e:
            self.logger.error(f"保存历史记录失败: {str(e)}")

    def setup_schedule(self):
        """设置定时任务"""
        try:
            self.logger.info(f"正在设置定时任务: 每天 {config.SCHEDULE_HOUR}:{config.SCHEDULE_MINUTE:02d} (时区: {config.TIMEZONE})")

            self.scheduler.add_job(
                func=self.process_daily_summary,
                trigger='cron',
                hour=config.SCHEDULE_HOUR,
                minute=config.SCHEDULE_MINUTE,
                job_id='daily_summary_job'
            )

            self.logger.info("✓ 定时任务设置成功")

        except Exception as e:
            self.logger.error(f"✗ 设置定时任务失败: {str(e)}")
            raise

    def run(self):
        """运行工作流"""
        try:
            # 初始化客户端
            if not self.initialize_clients():
                self.logger.error("客户端初始化失败，程序退出")
                sys.exit(1)

            # 设置定时任务
            self.setup_schedule()

            # 启动调度器
            self.scheduler.start()
            self.logger.info("调度器已启动，等待任务执行...")
            self.logger.info(f"下次执行时间: 每天 {config.SCHEDULE_HOUR}:{config.SCHEDULE_MINUTE:02d} ({config.TIMEZONE})")

            # 保持程序运行
            import time
            while True:
                time.sleep(1)

        except (KeyboardInterrupt, SystemExit):
            self.logger.info("收到退出信号，正在关闭...")
            if self.scheduler:
                self.scheduler.shutdown()
            self.logger.info("程序已退出")
            sys.exit(0)

        except Exception as e:
            self.logger.error(f"程序运行时发生错误: {str(e)}", exc_info=True)
            if self.scheduler:
                self.scheduler.shutdown()
            sys.exit(1)


def main():
    """主函数"""
    import logging.handlers

    # 创建并运行工作流
    workflow = DailySummaryWorkflow()
    workflow.run()


if __name__ == "__main__":
    main()


