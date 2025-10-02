# 配置验证工具使用指南

## 概述

`validate_config.py` 是一个综合性的配置验证工具，用于检查项目中所有服务的配置是否正确。该工具可以验证以下服务：

- **AI 服务**: Gemini, OpenAI, Anthropic
- **笔记服务**: Notion
- **存储服务**: Cloudflare R2, AWS S3

## 快速开始

### 基本使用

```bash
# 验证所有服务配置
python validate_config.py

# 仅验证 Gemini AI 配置
python validate_config.py --service gemini

# 显示详细验证过程
python validate_config.py --verbose

# JSON 格式输出（适用于 CI/CD）
python validate_config.py --format json
```

### 完整命令行选项

```bash
python validate_config.py [选项]

选项:
  --service SERVICE    仅验证指定服务 (gemini, openai, anthropic, notion, r2, s3, all)
  --verbose, -v        显示详细输出
  --format FORMAT      输出格式 (text, json)
  --help, -h          显示此帮助信息
```

## 验证范围

### AI 服务验证

#### Gemini AI
- ✅ API 密钥存在性检查
- ✅ API 密钥格式验证（必须以 "AIza" 开头）
- ✅ 客户端初始化测试
- ✅ API 连接和权限测试
- ✅ 模型可用性测试

#### OpenAI
- ✅ API 密钥存在性检查
- ✅ API 密钥格式验证（必须以 "sk-" 开头）
- ✅ 基本配置验证

#### Anthropic
- ✅ API 密钥存在性检查
- ✅ API 密钥格式验证（必须以 "sk-ant-" 开头）
- ✅ 基本配置验证

### 笔记服务验证

#### Notion
- ✅ Token 存在性检查
- ✅ Database ID 存在性检查
- ✅ 基本配置验证

### 存储服务验证

#### Cloudflare R2
- ✅ Access Key ID 存在性检查
- ✅ Secret Access Key 存在性检查
- ✅ Endpoint 存在性检查
- ✅ Bucket Name 存在性检查

#### AWS S3
- ✅ Access Key ID 存在性检查
- ✅ Secret Access Key 存在性检查
- ✅ Region 配置验证

## 输出示例

### 文本格式输出

```
🚀 开始验证所有服务配置...
  🔍 验证 Gemini AI 配置...
  ✅ Gemini AI 配置正确
  🔍 验证 OpenAI 配置...
  ❌ OpenAI 配置有问题
  🔍 验证 Anthropic 配置...
  ✅ Anthropic 配置正确

============================================================
📊 配置验证结果摘要
============================================================
✅ 验证通过: 2/3
❌ 验证失败: 1/3

📋 详细结果:
  ✅ GEMINI
  ❌ OPENAI
    💡 OPENAI_API_KEY环境变量未设置或为空
  ✅ ANTHROPIC

💡 使用 --verbose 参数查看详细验证过程
💡 使用 --service 参数验证特定服务
============================================================
```

### JSON 格式输出

```json
{
  "gemini": {
    "valid": true,
    "details": {
      "api_key_exists": true,
      "api_key_format_valid": true,
      "can_initialize": true,
      "can_connect": true,
      "model_available": true,
      "errors": [],
      "warnings": []
    }
  },
  "openai": {
    "valid": false,
    "details": {
      "api_key_exists": false,
      "errors": ["OPENAI_API_KEY环境变量未设置或为空"],
      "warnings": []
    }
  }
}
```

## 环境变量配置

在您的 `.env` 文件中设置以下变量：

```bash
# AI 服务配置
GEMINI_API_KEY=AIzaSyD...your_gemini_key_here
OPENAI_API_KEY=sk-...your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-...your_anthropic_key_here

# 笔记服务配置
NOTION_TOKEN=secret_...your_notion_token_here
NOTION_DATABASE_ID=...your_database_id_here

# 存储服务配置 - Cloudflare R2
R2_ACCESS_KEY_ID=...your_r2_access_key_here
R2_SECRET_ACCESS_KEY=...your_r2_secret_key_here
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_BUCKET_NAME=your_bucket_name_here

# 存储服务配置 - AWS S3
AWS_ACCESS_KEY_ID=...your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=...your_aws_secret_key_here
AWS_REGION=us-east-1
```

## 集成到工作流程

### 作为独立工具使用

```bash
# 在项目根目录运行
cd /path/to/your/project
python workflow-tools/validate_config.py --verbose
```

### 在 Python 代码中集成

```python
from workflow_tools.validate_config import ConfigValidator

# 创建验证器
validator = ConfigValidator(verbose=True)

# 验证所有服务
results = validator.validate_all()

# 验证特定服务
gemini_result = validator.validate_gemini()
notion_result = validator.validate_notion()

# 检查验证结果
if results['gemini']['valid']:
    print("Gemini 配置正确")
else:
    print("Gemini 配置有问题")
    for error in results['gemini']['details']['errors']:
        print(f"  - {error}")
```

### CI/CD 集成

```yaml
# GitHub Actions 示例
- name: Validate Configuration
  run: |
    cd workflow-tools
    python validate_config.py --format json > config_validation.json

- name: Check Validation Results
  run: |
    python -c "
    import json
    with open('workflow-tools/config_validation.json') as f:
        results = json.load(f)
    all_valid = all(r['valid'] for r in results.values())
    exit(0 if all_valid else 1)
    "
```

## 故障排除

### 常见问题

1. **ImportError**: 确保已安装所需依赖包
   ```bash
   pip install google-generativeai notion-client boto3
   ```

2. **网络连接错误**: 检查网络连接和防火墙设置

3. **权限错误**: 确认 API 密钥有正确的权限

4. **格式错误**: 检查 API 密钥格式是否正确

### 调试模式

使用 `--verbose` 参数查看详细的验证过程：

```bash
python validate_config.py --verbose --service gemini
```

这将显示每个验证步骤的详细信息，帮助您定位问题。

## 扩展开发

如果需要添加新的验证服务，请参考现有代码结构：

1. 在 `ConfigValidator` 类中添加新的验证方法
2. 在命令行参数中添加新的服务选项
3. 在环境变量配置中添加新的变量说明

## 支持的服务

- ✅ **Gemini AI** - Google 的 Gemini AI 服务
- ✅ **OpenAI** - OpenAI API 服务
- ✅ **Anthropic** - Anthropic Claude 服务
- ✅ **Notion** - Notion 笔记服务
- ✅ **Cloudflare R2** - Cloudflare 对象存储
- ✅ **AWS S3** - Amazon S3 对象存储

如果您需要验证其他服务，可以通过修改代码轻松添加支持。
