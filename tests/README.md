# 测试目录

本目录包含项目的测试文件。

## 🧪 当前测试文件

### IMAP 测试
- **test_outlook_imap.py** - Outlook IMAP 连接测试
- **test_qq_email.py** - QQ 邮箱连接测试

## 📝 测试说明

### 运行测试
```bash
# 测试 Outlook IMAP
python tests/test_outlook_imap.py

# 测试 QQ 邮箱
python tests/test_qq_email.py
```

### 环境要求
- 确保已配置 `.env` 文件
- 根据测试类型配置相应的邮箱凭据

## 🗂️ 归档测试

过时或已被替代的测试文件存放在 `../archived/tests/` 目录中：
- `check_mailbox.py` - 早期邮箱检查脚本
- `diagnose_auth.py` - 早期认证诊断脚本
- `test_outlook_read.py` - 早期 Outlook 读取测试
- `test_outlook_send.py` - 早期 Outlook 发送测试

## 📦 Workflow-Tools 测试

`workflow-tools` 包的测试文件在 `../workflow-tools/tests/` 目录中。

