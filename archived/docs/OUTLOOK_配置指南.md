# Outlook 邮箱访问权限配置指南

本指南将帮助你完成Outlook邮箱的访问权限配置,包括读取邮件和发送邮件的所有必要步骤。

## 📋 目录

1. [配置概览](#配置概览)
2. [步骤1: Azure应用注册 (读取邮件)](#步骤1-azure应用注册-读取邮件)
3. [步骤2: SMTP应用密码 (发送邮件)](#步骤2-smtp应用密码-发送邮件)
4. [步骤3: 环境变量配置](#步骤3-环境变量配置)
5. [步骤4: 测试配置](#步骤4-测试配置)
6. [常见问题](#常见问题)

---

## 配置概览

本系统需要配置两种认证方式:

| 功能 | 认证方式 | 需要配置的信息 |
|------|---------|---------------|
| **读取邮件** | Microsoft Graph API (OAuth 2.0) | `OUTLOOK_CLIENT_ID`<br>`OUTLOOK_CLIENT_SECRET`<br>`OUTLOOK_TENANT_ID` |
| **发送邮件** | SMTP (应用专用密码) | `OUTLOOK_SMTP_PASSWORD` |
| **通用** | 邮箱地址 | `OUTLOOK_EMAIL` |

---

## 步骤1: Azure应用注册 (读取邮件)

### 1.1 访问Azure Portal

1. 打开浏览器,访问 [Azure Portal](https://portal.azure.com/)
2. 使用你的Microsoft账户登录

### 1.2 创建应用注册

1. 在左侧菜单中找到 **"Azure Active Directory"** (或搜索"Azure AD")
2. 点击左侧菜单的 **"应用注册"** (App registrations)
3. 点击顶部的 **"+ 新注册"** (New registration)

### 1.3 填写应用信息

在注册页面填写以下信息:

- **名称**: `DailySummaryApp` (可自定义任何名称)
- **支持的账户类型**: 选择 **"仅此组织目录中的账户"** (Single tenant)
- **重定向URI**: 留空 (因为我们使用的是应用程序权限,不需要用户交互)

点击 **"注册"** 按钮完成创建。

### 1.4 记录应用程序ID和租户ID

注册完成后,你会看到应用的概述页面:

1. 找到 **"应用程序(客户端) ID"** (Application/Client ID)
   - 复制这个值 → 这是你的 `OUTLOOK_CLIENT_ID`
   
2. 找到 **"目录(租户) ID"** (Directory/Tenant ID)
   - 复制这个值 → 这是你的 `OUTLOOK_TENANT_ID`

### 1.5 创建客户端密钥

1. 在左侧菜单中点击 **"证书和密码"** (Certificates & secrets)
2. 点击 **"+ 新客户端密码"** (New client secret)
3. 填写描述: `DailySummarySecret`
4. 选择过期时间: 推荐选择 **"24个月"**
5. 点击 **"添加"**
6. **重要**: 立即复制显示的密钥值 (它只会显示一次!)
   - 这个值 → 这是你的 `OUTLOOK_CLIENT_SECRET`

### 1.6 配置API权限

1. 在左侧菜单中点击 **"API权限"** (API permissions)
2. 点击 **"+ 添加权限"** (Add a permission)
3. 选择 **"Microsoft Graph"**
4. 选择 **"应用程序权限"** (Application permissions) - 不是委托权限!
5. 搜索并添加以下权限:
   - ✅ **必需**: `Mail.Read` - "Read mail in all mailboxes" (读取所有邮箱的邮件)
   - ✅ **可选**: `Mail.ReadWrite` - "Read and write mail in all mailboxes" (如果需要标记已读等功能)
   
   **注意**: 
   - 不是 `Mail.Read.All`,而是 `Mail.Read`
   - 权限列表中显示的就是这两个名称
6. 点击 **"添加权限"**
7. **重要**: 点击 **"为[你的组织]授予管理员同意"** (Grant admin consent)
   - 这一步需要管理员权限
   - 确认授予同意

### 1.7 验证权限配置

确认 **"API权限"** 页面显示:

```
权限名称               类型        状态
Mail.Read             应用程序     ✓ 已授予管理员同意
```

**重要说明**:
- 权限名称就是 `Mail.Read` (不带 `.All` 后缀)
- 在Azure门户搜索框输入 "mail" 就能找到
- 完整描述是 "Read mail in all mailboxes"

---

## 步骤2: SMTP应用密码 (发送邮件)

### 2.1 访问Microsoft账户安全设置

1. 打开浏览器,访问 [Microsoft账户安全](https://account.microsoft.com/security)
2. 登录你的Microsoft账户

### 2.2 启用双重验证 (如果未启用)

**注意**: 应用密码功能需要先启用双重验证

1. 找到 **"高级安全选项"**
2. 如果双重验证未启用:
   - 点击 **"双重验证"** 下的 **"启用"**
   - 按照提示完成设置 (通常需要手机验证)

### 2.3 创建应用专用密码

1. 在安全页面找到 **"应用密码"** (App passwords)
2. 点击 **"创建新的应用密码"** (Create a new app password)
3. 系统会生成一个16位的密码 (格式类似: `abcd efgh ijkl mnop`)
4. **重要**: 立即复制这个密码 (它只会显示一次!)
   - 这个值 → 这是你的 `OUTLOOK_SMTP_PASSWORD`
   - 注意: 使用时**去掉空格**,或者**保留空格**都可以

### 2.4 为密码命名

- 给这个密码起个名字: `DailySummaryApp`
- 这样以后可以识别和管理

---

## 步骤3: 环境变量配置

### 3.1 创建.env文件

在项目根目录下,复制示例文件:

```bash
cp env.example .env
```

### 3.2 编辑.env文件

打开`.env`文件,填入你刚才获取的所有信息:

```bash
# ===== Outlook邮箱配置 =====
# 你的Outlook邮箱地址
OUTLOOK_EMAIL=your_email@outlook.com

# Microsoft Graph API配置 (从Azure Portal获取)
OUTLOOK_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
OUTLOOK_CLIENT_SECRET=your_client_secret_value_here
OUTLOOK_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# SMTP应用专用密码 (从Microsoft账户安全设置获取)
OUTLOOK_SMTP_PASSWORD=abcdefghijklmnop

# 邮件筛选发件人 (用于筛选每日总结邮件)
EMAIL_FILTER_SENDER=sender@example.com

# ===== Gemini AI配置 =====
GEMINI_API_KEY=your_gemini_api_key_here

# ===== 总结结果接收邮箱 =====
SUMMARY_RECIPIENT=recipient@example.com

# ===== 日志配置 =====
LOG_LEVEL=INFO

# ===== 历史记录配置 =====
SAVE_HISTORY=true
HISTORY_LEVEL=detailed
```

### 3.3 配置说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `OUTLOOK_EMAIL` | 你的Outlook邮箱地址 | `john@outlook.com` |
| `OUTLOOK_CLIENT_ID` | Azure应用的客户端ID | `12345678-1234-...` |
| `OUTLOOK_CLIENT_SECRET` | Azure应用的客户端密钥 | `abc123XYZ...` |
| `OUTLOOK_TENANT_ID` | Azure租户ID | `87654321-4321-...` |
| `OUTLOOK_SMTP_PASSWORD` | SMTP应用专用密码 | `abcdefghijklmnop` |
| `EMAIL_FILTER_SENDER` | 要筛选的发件人邮箱 | `daily@example.com` |
| `SUMMARY_RECIPIENT` | 接收分析结果的邮箱 | `john@outlook.com` |

---

## 步骤4: 测试配置

### 4.1 安装依赖

```bash
# 安装workflow-tools
cd workflow-tools
pip install -e .[all]
cd ..

# 安装主程序依赖
pip install -r requirements.txt
```

### 4.2 运行验证脚本

你可以使用项目提供的验证工具:

```bash
cd workflow-tools
python validate_config.py
```

这个脚本会自动检查:
- ✅ 环境变量是否配置完整
- ✅ Microsoft Graph API连接是否正常
- ✅ 邮件读取权限是否可用
- ✅ SMTP邮件发送是否可用

### 4.3 手动测试读取邮件

创建一个测试脚本 `test_outlook_read.py`:

```python
#!/usr/bin/env python3
"""测试Outlook邮件读取"""

import os
from dotenv import load_dotenv
from workflow_tools.email.outlook import OutlookClient

# 加载环境变量
load_dotenv()

# 创建客户端
client = OutlookClient()

# 连接
print("正在连接到Outlook...")
client.connect()
print("✓ 连接成功!")

# 获取最近5封邮件
print("\n正在获取邮件...")
result = client.fetch_emails(limit=5)

if result.success:
    print(f"✓ 成功获取 {len(result.messages)} 封邮件")
    for msg in result.messages:
        print(f"  - {msg.subject} (from {msg.sender})")
else:
    print(f"✗ 获取邮件失败: {result.error}")

# 断开连接
client.disconnect()
```

运行测试:

```bash
python test_outlook_read.py
```

### 4.4 手动测试发送邮件

创建一个测试脚本 `test_outlook_send.py`:

```python
#!/usr/bin/env python3
"""测试Outlook邮件发送"""

import os
from dotenv import load_dotenv
from workflow_tools.email.outlook import OutlookClient

# 加载环境变量
load_dotenv()

# 创建客户端
client = OutlookClient()

# 发送测试邮件
print("正在发送测试邮件...")
recipient = os.getenv("OUTLOOK_EMAIL")  # 发送给自己
success = client.send_email(
    to=[recipient],
    subject="Outlook配置测试",
    body="这是一封测试邮件,如果你收到了,说明SMTP配置成功!"
)

if success:
    print(f"✓ 邮件发送成功! 请检查 {recipient} 的收件箱")
else:
    print("✗ 邮件发送失败")
```

运行测试:

```bash
python test_outlook_send.py
```

### 4.5 运行完整工作流

如果以上测试都通过,可以测试完整的工作流:

```bash
python main.py
```

程序会启动定时任务,在每晚10点自动执行。如果想立即测试一次,可以修改`main.py`:

```python
if __name__ == "__main__":
    workflow = DailySummaryWorkflow()
    workflow.initialize_clients()
    workflow.process_daily_summary()  # 直接执行一次
```

---

## 常见问题

### ❓ Q1: 无法创建Azure应用注册

**A**: 可能原因:
- 你的账户没有管理员权限
- 你的组织禁止了应用注册

**解决方案**:
- 联系你的IT管理员
- 或使用个人Microsoft账户创建应用

---

### ❓ Q2: 无法授予管理员同意

**A**: **"授予管理员同意"** 按钮需要全局管理员权限。

**解决方案**:
1. 如果是公司账户,联系IT管理员帮助授予
2. 如果是个人账户:
   - 进入 [Azure Portal](https://portal.azure.com/)
   - 确认你是该租户的所有者

---

### ❓ Q3: 找不到"应用密码"选项

**A**: 可能原因:
- 双重验证未启用
- 你的组织禁用了应用密码功能

**解决方案**:
1. 先启用双重验证
2. 如果仍找不到,可能需要联系管理员

---

### ❓ Q4: SMTP认证失败

**A**: 可能原因:
- 应用密码不正确
- 应用密码中有空格

**解决方案**:
1. 重新生成应用密码
2. 确保密码中没有多余的空格或换行
3. 验证邮箱地址正确

---

### ❓ Q5: Graph API返回401未授权

**A**: 可能原因:
- Client ID、Secret或Tenant ID不正确
- API权限未授予管理员同意
- 密钥已过期

**解决方案**:
1. 检查Azure Portal中的凭据
2. 确认API权限已授予同意
3. 重新生成客户端密钥

---

### ❓ Q6: Graph API返回403禁止访问

**A**: 可能原因:
- 缺少必要的API权限
- 权限类型错误(应该是"应用程序权限"而不是"委托权限")

**解决方案**:
1. 检查是否添加了`Mail.Read`权限
2. 确认使用的是**应用程序权限**
3. 确认已授予管理员同意

---

### ❓ Q7: 收不到测试邮件

**A**: 可能原因:
- 邮件被归类到垃圾邮件
- SMTP服务器被防火墙阻止
- 收件人地址错误

**解决方案**:
1. 检查垃圾邮件文件夹
2. 检查网络防火墙设置
3. 验证收件人地址正确

---

### ❓ Q8: 定时任务不执行

**A**: 可能原因:
- 程序未在后台运行
- 时区配置错误
- 调度器配置错误

**解决方案**:
1. 确认`python main.py`正在运行
2. 检查`config.py`中的`TIMEZONE`设置
3. 查看`logs/`目录中的日志文件

---

## 🔒 安全建议

1. **永远不要提交.env文件到Git**
   - `.env`文件已在`.gitignore`中
   - 确保不要意外提交敏感信息

2. **定期轮换密钥**
   - Azure客户端密钥可以设置过期时间
   - SMTP应用密码可以随时撤销和重建

3. **使用最小权限原则**
   - 只授予必要的API权限
   - 不需要额外的Graph API权限

4. **备份配置信息**
   - 安全地保存你的配置信息
   - 使用密码管理器

---

## 📚 相关资源

- [Microsoft Graph API文档](https://docs.microsoft.com/en-us/graph/overview)
- [Azure应用注册指南](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Outlook SMTP设置](https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353)
- [Microsoft应用密码](https://support.microsoft.com/en-us/account-billing/using-app-passwords-with-apps-that-don-t-support-two-step-verification-5896ed9b-4263-e681-128a-a6f2979a7944)

---

## ✅ 配置检查清单

完成配置后,使用此清单确认:

- [ ] Azure应用已注册
- [ ] 已记录Client ID、Secret和Tenant ID
- [ ] API权限`Mail.Read`已添加并授予管理员同意
- [ ] 双重验证已启用
- [ ] SMTP应用密码已创建
- [ ] `.env`文件已创建并填写所有必需变量
- [ ] 依赖包已安装
- [ ] 测试邮件读取成功
- [ ] 测试邮件发送成功
- [ ] 完整工作流测试通过

---

## 🎉 完成!

恭喜! 你已经完成了Outlook邮箱的访问权限配置。现在可以开始使用每日总结自动化工作流了。

如有任何问题,请查看日志文件 `logs/` 或参考上面的常见问题部分。

祝使用愉快! 📧✨

