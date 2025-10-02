# 切换到 QQ 邮箱使用指南

## 🎉 完成情况

✅ 已成功创建通用 IMAP 客户端，支持 QQ 邮箱及其他邮箱服务商！

## 📦 新增功能

### 1. 通用 IMAP 客户端 (`GenericIMAPClient`)
- 位置：`workflow-tools/workflow_tools/email/base/generic_imap_client.py`
- 功能：支持任何提供 IMAP/SMTP 服务的邮箱
- 特点：完全可配置的服务器地址和端口

### 2. QQ 邮箱客户端 (`QQIMAPClient`)
- 位置：`workflow-tools/workflow_tools/email/qq/qq_imap_client.py`
- 功能：专为 QQ 邮箱优化，预配置了服务器地址
- 特点：开箱即用，只需提供邮箱和授权码

## 🔧 如何切换到 QQ 邮箱

### 方式一：使用 QQ 邮箱客户端（推荐）

**第一步：获取 QQ 邮箱授权码**

1. 登录 QQ 邮箱网页版：https://mail.qq.com
2. 进入"设置" → "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"IMAP/SMTP服务"
5. 按照提示发送短信，获取**授权码**（16位）
6. 复制并保存授权码

**第二步：配置环境变量**

编辑 `.env` 文件（如果没有，请复制 `env.example`）：

```bash
# 设置邮件客户端类型为 QQ 邮箱
EMAIL_CLIENT_TYPE=qq

# 设置您的 QQ 邮箱地址
EMAIL_ADDRESS=你的QQ号@qq.com

# 设置授权码（不是 QQ 密码！）
EMAIL_PASSWORD=你的16位授权码

# 设置邮件筛选发件人
EMAIL_FILTER_SENDER=发送每日总结的邮箱地址

# 设置总结结果接收邮箱
SUMMARY_RECIPIENT=接收总结的邮箱地址

# Gemini API Key（用于 AI 分析）
GEMINI_API_KEY=你的Gemini_API_Key
```

**第三步：测试配置**

```bash
python check_mailbox.py
```

### 方式二：使用通用 IMAP 客户端

如果您想使用其他邮箱（如 163、Gmail 等）：

```bash
# 设置为通用 IMAP 客户端
EMAIL_CLIENT_TYPE=generic

# 邮箱地址
EMAIL_ADDRESS=your_email@example.com

# 邮箱密码或授权码
EMAIL_PASSWORD=your_password_or_auth_code

# IMAP 服务器配置
IMAP_SERVER=imap.example.com
IMAP_PORT=993

# SMTP 服务器配置
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USE_SSL=false  # true=465端口SSL, false=587端口STARTTLS
```

## 📊 支持的邮箱类型对比

| 客户端类型 | 适用邮箱 | 配置复杂度 | 功能 |
|-----------|---------|-----------|------|
| `qq` | QQ邮箱 | ⭐ 简单 | IMAP读取 + SMTP发送 |
| `imap` | Outlook个人 | ⭐⭐ 中等 | IMAP读取 + SMTP发送 |
| `graph` | Outlook组织 | ⭐⭐⭐ 复杂 | Graph API读取 + SMTP发送 |
| `generic` | 任意邮箱 | ⭐⭐ 中等 | IMAP读取 + SMTP发送 |

## 🔍 常见邮箱服务器配置

### QQ 邮箱（推荐使用 `EMAIL_CLIENT_TYPE=qq`）
- IMAP: `imap.qq.com:993`
- SMTP: `smtp.qq.com:587` 或 `smtp.qq.com:465`
- 授权方式：授权码（需在邮箱设置中生成）

### 163 邮箱
```bash
EMAIL_CLIENT_TYPE=generic
IMAP_SERVER=imap.163.com
IMAP_PORT=993
SMTP_SERVER=smtp.163.com
SMTP_PORT=465
SMTP_USE_SSL=true
```

### 126 邮箱
```bash
EMAIL_CLIENT_TYPE=generic
IMAP_SERVER=imap.126.com
IMAP_PORT=993
SMTP_SERVER=smtp.126.com
SMTP_PORT=465
SMTP_USE_SSL=true
```

### Gmail
```bash
EMAIL_CLIENT_TYPE=generic
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_SSL=false
```

## ⚠️ 重要注意事项

### 1. 授权码 vs 密码
- **QQ 邮箱**：必须使用授权码，不能使用 QQ 密码
- **163/126 邮箱**：需要使用客户端授权密码
- **Gmail**：需要使用应用专用密码（开启两步验证后）

### 2. 安全建议
- ✅ 使用 `.env` 文件存储敏感信息
- ✅ 将 `.env` 添加到 `.gitignore`
- ❌ 不要在代码中硬编码密码
- ❌ 不要将 `.env` 文件提交到 Git

### 3. 防火墙配置
确保防火墙允许以下端口：
- **IMAP**：993（SSL）
- **SMTP**：587（STARTTLS）或 465（SSL）

## 🧪 测试检查清单

使用 QQ 邮箱前，请确认：

- [ ] 已在 QQ 邮箱设置中开启 IMAP/SMTP 服务
- [ ] 已生成并复制授权码
- [ ] 已在 `.env` 中正确配置 `EMAIL_CLIENT_TYPE=qq`
- [ ] 已设置 `EMAIL_ADDRESS` 为您的 QQ 邮箱
- [ ] 已设置 `EMAIL_PASSWORD` 为授权码（不是密码）
- [ ] 已设置 `EMAIL_FILTER_SENDER` 和 `SUMMARY_RECIPIENT`
- [ ] 运行 `python check_mailbox.py` 测试通过

## 🚀 启动程序

配置完成后，运行主程序：

```bash
python main.py
```

程序将：
1. 初始化 QQ 邮箱客户端
2. 每晚 22:00 自动执行
3. 读取最近 24 小时的"每日总结"邮件
4. 使用 Gemini AI 进行分析
5. 将分析结果发送到指定邮箱

## 📚 相关文档

- [QQ邮箱配置指南.md](./QQ邮箱配置指南.md) - 详细的 QQ 邮箱配置步骤
- [env.example](./env.example) - 环境变量配置模板
- [README.md](./README.md) - 项目总体说明

## 🆘 故障排除

### 问题 1：535 Authentication failed
**原因**：使用了 QQ 密码而不是授权码
**解决**：重新生成授权码并使用

### 问题 2：连接超时
**原因**：网络问题或防火墙阻止
**解决**：检查网络，确保端口 993 和 587 可访问

### 问题 3：找不到邮件
**原因**：筛选条件不匹配
**解决**：检查 `EMAIL_FILTER_SUBJECT` 和 `EMAIL_FILTER_SENDER` 配置

查看详细日志：
```bash
tail -f logs/workflow_*.log
```

## 💡 代码示例

### 在 Python 代码中直接使用 QQ 邮箱客户端

```python
from workflow_tools.email import QQIMAPClient

# 创建客户端
client = QQIMAPClient(
    email_address="your_email@qq.com",
    password="your_authorization_code"
)

# 连接
client.connect()

# 读取邮件
from datetime import datetime, timedelta, timezone
since_date = datetime.now(timezone.utc) - timedelta(hours=24)

result = client.fetch_emails(
    subject="每日总结",
    sender="sender@example.com",
    since_date=since_date
)

# 发送邮件
client.send_email(
    to=["recipient@example.com"],
    subject="测试邮件",
    body="这是一封测试邮件"
)
```

---

**祝您使用愉快！**🎊

如有问题，请查阅 `QQ邮箱配置指南.md` 或查看程序日志。

