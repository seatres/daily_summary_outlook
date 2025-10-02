# Gemini模型配置说明

## 概述

Gemini模型名称现在统一通过 `config/settings.py` 文件进行配置，确保测试和运行时使用相同的模型，避免配置不一致的问题。

## 配置方式

### 主配置文件

模型名称在 `config/settings.py` 中配置：

```python
# Gemini配置
GEMINI_MODEL_NAME = "gemini-1.5-flash"
```

### 支持的模型

常用的Gemini模型包括：
- `gemini-1.5-flash` - 快速响应，适合大多数任务
- `gemini-1.5-pro` - 更强性能，适合复杂任务
- `gemini-2.0-flash-exp` - 实验性版本

## 使用方式

### 1. 默认使用（推荐）

```python
from workflow_tools.ai_models.gemini import GeminiClient

# 自动使用settings.py中配置的模型
client = GeminiClient()
```

### 2. 显式指定模型

```python
from workflow_tools.ai_models.gemini import GeminiClient

# 覆盖默认配置，使用特定模型
client = GeminiClient(model_name="gemini-1.5-pro")
```

### 3. 在PDF处理器中的使用

```python
# src/processors/pdf_processor.py
class PDFProcessor:
    def __init__(self):
        # 自动使用settings.py中的配置
        self.ai_client = GeminiClient()
```

## 配置验证

API连接测试现在使用与运行时相同的模型：

```python
from workflow_tools.ai_models.gemini.gemini_client import GeminiClient

# 验证配置，使用settings.py中的模型
result = GeminiClient.validate_gemini_config()
```

## 修改模型配置

1. **编辑配置文件**：
   ```bash
   # 编辑 config/settings.py
   vim config/settings.py
   ```

2. **修改模型名称**：
   ```python
   # 将这行
   GEMINI_MODEL_NAME = "gemini-1.5-flash"
   
   # 改为
   GEMINI_MODEL_NAME = "gemini-1.5-pro"
   ```

3. **重启应用程序**：
   配置更改后需要重启应用程序才能生效。

## 环境变量支持

虽然主要配置在settings.py中，但仍然需要在.env文件中配置API密钥：

```env
# .env文件
GEMINI_API_KEY=your_gemini_api_key_here
```

## 优势

1. **配置统一**：测试和运行时使用相同模型
2. **版本控制**：模型配置可以纳入版本控制
3. **环境一致**：所有环境使用相同的配置逻辑
4. **易于管理**：集中管理所有应用程序配置

## 迁移说明

如果您之前使用了 `GEMINI_TEST_MODEL` 环境变量：

1. **移除环境变量**：
   ```bash
   # 从.env文件中删除这行
   # GEMINI_TEST_MODEL=gemini-1.5-flash
   ```

2. **更新settings.py**：
   ```python
   # 在config/settings.py中设置
   GEMINI_MODEL_NAME = "your_preferred_model"
   ```

3. **无需修改代码**：
   现有的GeminiClient使用方式无需更改，会自动使用新的配置方式。

## 故障排除

### 问题：无法导入settings模块

如果在独立使用workflow-tools时遇到导入错误：

```python
# 会自动回退到默认模型
# 默认值：gemini-1.5-flash
```

### 问题：模型访问权限错误

确保您的API密钥有权限访问配置的模型：

1. 检查API密钥权限
2. 确认模型名称正确
3. 验证模型在您的地区可用

### 问题：配置不生效

确保：

1. 正确编辑了 `config/settings.py`
2. 重启了应用程序
3. 没有在代码中硬编码模型名称
