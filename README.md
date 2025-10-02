# 每日总结邮件自动化工作流

这是一个自动化工作流系统，用于从Outlook邮箱中读取每日总结邮件，使用Gemini AI进行智能分析，并将结果发送回邮箱。

## 功能特性

- ⏰ **定时执行**: 每晚10点（东八区）自动运行
- 📧 **智能筛选**: 自动筛选主题为"每日总结"且来自指定发件人的邮件
- 🤖 **AI分析**: 使用Gemini 2.5 Pro进行深度分析和总结
- 🔒 **安全认证**: 使用Microsoft Graph API（OAuth）安全读取邮件
- 📊 **历史记录**: 可配置的历史记录保存（minimal/normal/detailed）
- 🔄 **错误重试**: 自动重试机制，确保任务可靠执行
- 🐳 **容器友好**: 适合在Docker容器中运行

## 系统架构

```
daily_summary_outlook/
├── main.py                 # 主程序
├── config.py               # 配置文件
├── requirements.txt        # 依赖列表
├── env.example            # 环境变量示例
├── workflow-tools/         # 可重用的工具模块（类似n8n的节点）
│   └── workflow_tools/
│       ├── email/          # 邮件处理模块
│       ├── ai_models/      # AI模型模块
│       ├── scheduler/      # 调度器模块
│       ├── storage/        # 存储模块
│       ├── notes/          # 笔记模块
│       └── utils/          # 工具模块
├── docs/                   # 文档目录
├── tests/                  # 测试目录
├── scripts/                # 脚本目录
├── logs/                   # 日志目录
├── history/                # 历史记录目录
└── archived/               # 归档目录
```

> 📖 详细的目录结构说明请参考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 安装步骤

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd daily_summary_outlook
```

### 2. 安装workflow-tools

```bash
cd workflow-tools
pip install -e .[all]
cd ..
```

### 3. 安装主程序依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制`env.example`为`.env`并填入你的配置：

```bash
cp env.example .env
```

然后编辑`.env`文件，填入以下信息：

#### 4.1 获取Microsoft Graph API凭据

1. 访问 [Azure Portal](https://portal.azure.com/)
2. 进入 **Azure Active Directory** > **应用注册** > **新注册**
3. 填写应用信息：
   - 名称：`DailySummaryApp`（可自定义）
   - 支持的账户类型：选择"仅此组织目录中的账户"
4. 注册后，记录以下信息：
   - **应用程序(客户端) ID** → `OUTLOOK_CLIENT_ID`
   - **目录(租户) ID** → `OUTLOOK_TENANT_ID`
5. 创建客户端密钥：
   - 进入 **证书和密码** > **新客户端密码**
   - 记录密钥值 → `OUTLOOK_CLIENT_SECRET`
6. 配置API权限：
   - 进入 **API权限** > **添加权限** > **Microsoft Graph** > **应用程序权限**
   - 添加以下权限：
     - `Mail.Read`（读取邮件）
     - `Mail.ReadWrite`（如果需要标记已读）
   - 点击 **授予管理员同意**

#### 4.2 获取SMTP应用专用密码

1. 访问 [Microsoft账户安全设置](https://account.microsoft.com/security)
2. 选择 **高级安全选项**
3. 选择 **应用密码** > **创建新的应用密码**
4. 记录生成的密码 → `OUTLOOK_SMTP_PASSWORD`

#### 4.3 获取Gemini API密钥

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API密钥
3. 记录密钥 → `GEMINI_API_KEY`

### 5. 测试运行

首先测试一次性运行（不启动定时任务）：

```python
# 在main.py中临时修改，添加测试代码
if __name__ == "__main__":
    workflow = DailySummaryWorkflow()
    workflow.initialize_clients()
    workflow.process_daily_summary()  # 直接执行一次
```

### 6. 启动定时任务

```bash
python main.py
```

程序将在后台运行，每晚10点自动执行任务。

## 配置说明

### 邮件筛选条件

在`config.py`中配置：

```python
EMAIL_FILTER_SUBJECT = "每日总结"  # 主题完全匹配
EMAIL_FILTER_SENDER = "seatre@icloud.com"  # 发件人严格匹配
EMAIL_SEARCH_HOURS = 24  # 搜索最近24小时
```

### 定时任务配置

```python
TIMEZONE = "Asia/Shanghai"  # 东八区
SCHEDULE_HOUR = 22  # 22点（晚上10点）
SCHEDULE_MINUTE = 0  # 0分
```

### 历史记录配置

在`.env`文件中配置：

```bash
SAVE_HISTORY=true  # 是否保存历史记录
HISTORY_LEVEL=detailed  # 历史记录详细程度
```

历史记录级别说明：
- `minimal`: 只保存基本信息（时间、邮件数量、是否成功）
- `normal`: 保存邮件标题和分析结果摘要
- `detailed`: 保存完整的邮件内容和分析结果

### AI分析提示词

在`config.py`中自定义：

```python
AI_ANALYSIS_PROMPT = """你是一位专业的日记分析专家...."""
```

## Docker部署（可选）

虽然暂时不需要Docker实现，但未来可以通过以下方式部署：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt workflow-tools/ ./
RUN cd workflow-tools && pip install -e .[all] && cd ..
RUN pip install -r requirements.txt

# 复制代码
COPY . .

# 运行
CMD ["python", "main.py"]
```

## 日志查看

日志文件位于`logs/`目录：

```bash
# 查看今天的日志
tail -f logs/workflow_$(date +%Y%m%d).log

# 查看所有日志
ls -lh logs/
```

## 历史记录查看

历史记录以JSON格式保存在`history/`目录：

```bash
# 查看最新的历史记录
ls -lt history/ | head -5

# 查看某个历史记录
cat history/history_20251001_220000.json
```

## 故障排除

### 1. 邮件读取失败

检查：
- Microsoft Graph API凭据是否正确
- API权限是否已授予
- 邮箱地址是否正确

### 2. 邮件发送失败

检查：
- SMTP应用专用密码是否正确
- 网络连接是否正常
- Outlook SMTP服务器是否可访问

### 3. AI分析失败

检查：
- Gemini API密钥是否正确
- API配额是否充足
- 网络连接是否正常

### 4. 定时任务未执行

检查：
- 程序是否正在运行
- 时区配置是否正确
- 日志中是否有错误信息

## 扩展功能

### 添加新的邮件源

在`workflow-tools/workflow_tools/email/`中添加新的客户端：

```python
from .base.email_base import EmailClientBase

class GmailClient(EmailClientBase):
    # 实现Gmail客户端
    pass
```

### 添加新的AI模型

在`workflow-tools/workflow_tools/ai_models/`中添加新模型：

```python
from .base.ai_client_base import AIClientBase

class OpenAIClient(AIClientBase):
    # 实现OpenAI客户端
    pass
```

### 添加通知功能

可以集成Telegram、Slack等通知服务，在任务完成时发送通知。

## 许可证

MIT License

## 支持

如有问题，请查看日志文件或联系开发者。


