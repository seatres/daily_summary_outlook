# workflow-tools

可重用的API访问工具包，提供标准化的AI模型、笔记工具、存储服务接口。

## 功能特性

- 🤖 **AI模型支持**: Gemini AI (可扩展OpenAI、Anthropic等)
- 📝 **笔记工具**: Notion (可扩展Obsidian等)
- 💾 **存储服务**: Cloudflare R2 (可扩展AWS S3等)
- 📧 **邮件处理**: Outlook (Microsoft Graph API + SMTP)
- ⏰ **任务调度**: APScheduler (支持Cron表达式)
- 🔄 **智能缓存**: 基于文件内容的缓存机制
- 📊 **进度回调**: 实时处理进度反馈
- 🛡️ **错误处理**: 完善的异常处理和重试机制

## 安装

```bash
# 安装所有模块
pip install -e .[all]

# 按需安装
pip install -e .[ai,notes,storage,email,scheduler]

# 验证依赖安装
python validate_dependencies.py -v
```

### 依赖边界检查

本包实现了完善的依赖验证机制，在安装时自动检查依赖状态：

- ✅ **安装时验证**: 自动检测并提示缺失的依赖
- 🔍 **独立验证工具**: 随时手动检查依赖状态
- 🛡️ **运行时保护**: 使用功能前验证所需依赖

详见 [DEPENDENCY_VALIDATION.md](./DEPENDENCY_VALIDATION.md)

## 快速开始

### 1. 环境配置

创建 `.env` 文件：

```bash
# AI模型
GEMINI_API_KEY=your_gemini_api_key

# 笔记工具
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id

# 存储服务
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_ENDPOINT=https://your-endpoint.r2.cloudflarestorage.com
R2_BUCKET_NAME=your_bucket_name

# 邮件服务
OUTLOOK_EMAIL=your_email@outlook.com
OUTLOOK_CLIENT_ID=your_client_id
OUTLOOK_CLIENT_SECRET=your_client_secret
OUTLOOK_TENANT_ID=your_tenant_id
OUTLOOK_SMTP_PASSWORD=your_smtp_password
```

### 2. 使用示例

```python
from workflow_tools.ai_models.gemini import GeminiClient
from workflow_tools.notes.notion import NotionClient
from workflow_tools.storage.cloudflare_r2 import R2Client

# 初始化客户端
ai_client = GeminiClient()
notes_client = NotionClient()
storage_client = R2Client()

# 分析文档
result = ai_client.analyze_document(
    file_path="document.pdf",
    prompt="总结这篇文档的主要内容"
)

if result.success:
    # 创建笔记
    notes_client.create_page(
        title="文档总结",
        content=result.content
    )

    # 上传文件到存储
    storage_client.upload_file(
        file_path="document.pdf",
        object_name="documents/document.pdf"
    )
```

## 开发

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 代码格式化
black workflow_tools/
```