# IMAP快速开始指南 ⚡

5分钟内配置好你的个人Outlook账户!

---

## 📝 准备工作

你需要:
- ✅ 一个个人Outlook账户(`@outlook.com`, `@hotmail.com`等)
- ✅ 能够接收手机验证码

---

## 🚀 3步完成配置

### 步骤1: 生成应用专用密码 (3分钟)

1. 访问: https://account.microsoft.com/security
2. 登录你的Outlook账号
3. 找到 **"双重验证"** → 如果未启用,点击启用
4. 找到 **"应用密码"** → 点击 **"创建新密码"**
5. 输入名称: `Daily Summary`
6. **复制生成的16位密码** (只会显示一次!)

### 步骤2: 配置.env文件 (1分钟)

编辑 `.env` 文件(如果没有,从 `env.example` 复制一个):

```bash
# 必需配置
OUTLOOK_EMAIL=你的邮箱@outlook.com
EMAIL_CLIENT_TYPE=imap
OUTLOOK_IMAP_PASSWORD=刚才复制的16位密码
OUTLOOK_SMTP_PASSWORD=刚才复制的16位密码
EMAIL_FILTER_SENDER=发送每日总结的邮箱
GEMINI_API_KEY=你的Gemini_API_Key
SUMMARY_RECIPIENT=接收结果的邮箱
```

### 步骤3: 测试配置 (1分钟)

```bash
python test_outlook_imap.py
```

看到 ✓ 就表示成功!

---

## ✅ 完整示例

### .env文件示例

```bash
OUTLOOK_EMAIL=seatre83@outlook.com
EMAIL_CLIENT_TYPE=imap
OUTLOOK_IMAP_PASSWORD=abcd1234efgh5678
OUTLOOK_SMTP_PASSWORD=abcd1234efgh5678
EMAIL_FILTER_SENDER=daily@example.com
GEMINI_API_KEY=AIzaSy...
SUMMARY_RECIPIENT=seatre83@outlook.com
LOG_LEVEL=INFO
SAVE_HISTORY=true
HISTORY_LEVEL=detailed
```

---

## 🎯 运行程序

测试通过后,运行主程序:

```bash
python main.py
```

程序将在后台运行,每晚10点自动处理邮件。

---

## ❓ 遇到问题?

### 问题: 认证失败

**解决**: 检查应用专用密码是否正确复制

### 问题: 找不到"应用密码"

**解决**: 先启用双重验证,刷新页面

### 问题: 无法获取邮件

**解决**: 确认邮箱中有邮件,检查筛选条件

---

## 📚 更多帮助

- 详细配置: `IMAP配置指南.md`
- 项目文档: `README.md`
- 故障排除: `IMAP配置指南.md` → "故障排除"章节

---

## 🎉 完成!

5分钟配置完成,开始享受自动化! 🚀

