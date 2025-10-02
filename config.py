"""
配置文件
"""

import os
from pathlib import Path

# ===== 基础配置 =====
# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 日志目录
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 历史记录目录
HISTORY_DIR = PROJECT_ROOT / "history"
HISTORY_DIR.mkdir(exist_ok=True)


# ===== 邮件配置 =====
# Outlook邮箱地址
OUTLOOK_EMAIL = os.getenv("OUTLOOK_EMAIL", "")

# Microsoft Graph API配置（用于读取邮件）
OUTLOOK_CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID", "")
OUTLOOK_CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET", "")
OUTLOOK_TENANT_ID = os.getenv("OUTLOOK_TENANT_ID", "")

# SMTP配置（用于发送邮件）
OUTLOOK_SMTP_PASSWORD = os.getenv("OUTLOOK_SMTP_PASSWORD", "")

# 邮件筛选条件
EMAIL_FILTER_SUBJECT = "每日总结"  # 主题完全匹配
EMAIL_FILTER_SENDER = os.getenv("EMAIL_FILTER_SENDER", "")  # 发件人严格匹配
EMAIL_SEARCH_HOURS = 24  # 搜索最近24小时的邮件


# ===== AI配置 =====
# Gemini API配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = "gemini-2.5-pro"  # 使用Gemini 2.5 Pro模型
GEMINI_TEMPERATURE = 1.0

# AI分析提示词
AI_ANALYSIS_PROMPT = """你是一位专业的日记分析专家。请分析以下每日总结内容：

{email_contents}

请按照以下要求进行分析：

1. **完整列出记录**：将所有内容按照时间顺序完整地列出来，不要遗漏任何细节。

2. **深度分析**：作为日记分析专家，请提供有洞见的总结与分析，包括：
   - 主要活动和事件的总结
   - 情绪和心理状态的观察
   - 工作/学习进展的评估
   - 值得关注的模式或趋势
   - 建设性的建议和反思

请用清晰、有条理的方式组织你的分析。"""


# ===== 调度器配置 =====
# 时区设置（东八区）
TIMEZONE = "Asia/Shanghai"

# 定时执行时间（每晚10点）
SCHEDULE_HOUR = 22
SCHEDULE_MINUTE = 0


# ===== 日志配置 =====
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件配置
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 5  # 保留5个备份


# ===== 历史记录配置 =====
# 是否保存历史记录
SAVE_HISTORY = os.getenv("SAVE_HISTORY", "true").lower() == "true"

# 历史记录详细程度: minimal, normal, detailed
# - minimal: 只保存基本信息（时间、邮件数量、是否成功）
# - normal: 保存邮件标题和分析结果摘要
# - detailed: 保存完整的邮件内容和分析结果
HISTORY_LEVEL = os.getenv("HISTORY_LEVEL", "detailed")


# ===== 错误处理配置 =====
# 重试次数
MAX_RETRIES = 3

# 重试间隔（秒）
RETRY_DELAY = 5


# ===== 发送邮件配置 =====
# 收件人（总结结果发送到这个邮箱）
SUMMARY_RECIPIENT = os.getenv("SUMMARY_RECIPIENT", "")

# 邮件主题模板
EMAIL_SUBJECT_TEMPLATE = "每日总结汇总 - {date}"


