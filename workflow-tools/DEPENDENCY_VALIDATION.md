# 依赖验证机制

本文档说明 `workflow-tools` 包的依赖边界检查机制。

## 概述

为了提供更好的用户体验，`workflow-tools` 实现了多层依赖验证机制：

1. **安装时验证** - 在 `pip install` 时自动检查依赖
2. **运行时验证** - 在使用特定功能时检查相关依赖
3. **独立验证工具** - 可随时手动检查依赖状态

## 1. 安装时验证

### 工作原理

在 `setup.py` 中定义了自定义安装命令 `PostInstallCommand` 和 `PostDevelopCommand`，它们会在安装完成后自动执行依赖检查。

### 示例输出

```bash
$ pip install -e .

# ... 安装过程 ...

=== 依赖边界检查 ===
✓  [email] 已安装: msal
✓  [email] 已安装: requests
⚠️  [ai] 缺少: google.generativeai (Gemini AI)
   提示: pip install workflow-tools[ai]
⚠️  [notes] 缺少: notion_client (Notion API)
   提示: pip install workflow-tools[notes]
✓  [storage] 已安装: boto3
✓  [scheduler] 已安装: apscheduler
===================
```

### 优点

- **早期发现问题**: 在安装时而非运行时发现缺失的依赖
- **清晰的提示**: 告诉用户如何安装缺失的依赖
- **非阻塞**: 不会因可选依赖缺失而中断安装

## 2. 运行时验证

### 工作原理

各个客户端类（如 `OutlookClient`）在初始化时会检查其所需的依赖是否已安装。

### 示例代码

```python
# 在 outlook_client.py 中
try:
    from msal import ConfidentialClientApplication
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False

class OutlookClient(EmailClientBase):
    def __init__(self, ...):
        # 检查依赖
        if not MSAL_AVAILABLE:
            raise ImportError("请安装msal: pip install msal")
        if not REQUESTS_AVAILABLE:
            raise ImportError("请安装requests: pip install requests")
```

### 优点

- **精确的错误消息**: 明确告诉用户缺少哪个包
- **防止模糊错误**: 避免因缺少依赖导致的难以理解的运行时错误
- **按需加载**: 只有在实际使用功能时才检查相关依赖

## 3. 独立验证工具

### 使用方法

```bash
# 基本检查（只显示问题）
python workflow-tools/validate_dependencies.py

# 详细模式（显示所有依赖状态）
python workflow-tools/validate_dependencies.py -v

# 严格模式（任何依赖缺失都报错）
python workflow-tools/validate_dependencies.py --strict
```

### 示例输出

```bash
$ python workflow-tools/validate_dependencies.py -v

============================================================
📦 Workflow-Tools 依赖检查报告
============================================================

✅ 已安装的依赖:

  [core]
    ✓ typing_extensions - 类型扩展
    ✓ dotenv - 环境变量加载

  [email]
    ✓ msal - Microsoft身份认证
    ✓ requests - HTTP请求

  [storage]
    ✓ boto3 - AWS S3
    ✓ botocore - AWS核心库

⚠️  缺失的依赖:

  [ai]
    ✗ google.generativeai - Gemini AI
    💡 安装建议: pip install workflow-tools[ai]

  [notes]
    ✗ notion_client - Notion API
    💡 安装建议: pip install workflow-tools[notes]

💡 一次性安装所有依赖:
   pip install workflow-tools[all]

============================================================
```

### 退出码

- `0`: 所有核心依赖已安装
- `1`: 核心依赖缺失（严重问题）
- `2`: 只有可选依赖缺失

### 在 CI/CD 中使用

```bash
# 在 CI 流程中验证依赖
python workflow-tools/validate_dependencies.py --strict
if [ $? -ne 0 ]; then
    echo "依赖检查失败"
    exit 1
fi
```

## 依赖分类

### 核心依赖（必需）

这些是基础功能所需的依赖，会自动安装：

- `typing-extensions>=4.0.0` - 类型提示扩展
- `python-dotenv>=0.19.0` - 环境变量加载

### 可选依赖（按功能分组）

#### Email 功能
```bash
pip install workflow-tools[email]
```
- `msal>=1.20.0` - Microsoft身份认证
- `requests>=2.28.0` - HTTP请求

#### AI 功能
```bash
pip install workflow-tools[ai]
```
- `google-generativeai>=0.3.0` - Gemini AI

#### Notes 功能
```bash
pip install workflow-tools[notes]
```
- `notion-client>=2.0.0` - Notion API

#### Storage 功能
```bash
pip install workflow-tools[storage]
```
- `boto3>=1.26.0` - AWS S3
- `botocore>=1.29.0` - AWS核心库

#### Scheduler 功能
```bash
pip install workflow-tools[scheduler]
```
- `APScheduler>=3.10.0` - 任务调度
- `pytz>=2023.3` - 时区支持

#### 安装所有功能
```bash
pip install workflow-tools[all]
```

## 最佳实践

### 1. 开发环境

开发时建议安装所有依赖：

```bash
cd workflow-tools
pip install -e .[all,dev]
```

### 2. 生产环境

根据实际使用的功能安装：

```bash
# 只使用邮件和 AI 功能
pip install workflow-tools[email,ai]
```

### 3. 定期验证

在代码审查或部署前运行验证：

```bash
python workflow-tools/validate_dependencies.py -v
```

### 4. Docker 镜像

在 Dockerfile 中可以这样使用：

```dockerfile
# 安装特定功能
RUN pip install workflow-tools[email,ai,scheduler]

# 验证安装
RUN python -m workflow-tools.validate_dependencies --strict
```

## 故障排除

### 问题：安装后仍提示缺少依赖

**原因**: 可能使用了错误的 Python 环境

**解决方法**:
```bash
# 确认 Python 版本和位置
which python
python --version

# 重新安装
pip install --force-reinstall workflow-tools[all]
```

### 问题：某个依赖安装失败

**原因**: 可能是网络问题或版本冲突

**解决方法**:
```bash
# 手动安装失败的包
pip install msal==1.20.0

# 查看详细错误信息
pip install workflow-tools[email] -v
```

### 问题：在虚拟环境中依赖检查失败

**原因**: 虚拟环境配置问题

**解决方法**:
```bash
# 重新创建虚拟环境
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e .[all]
```

## 技术细节

### 实现架构

```
setup.py
├── PostInstallCommand (install 命令钩子)
│   └── _validate_dependencies() (验证逻辑)
└── PostDevelopCommand (develop 命令钩子)

validate_dependencies.py
└── DependencyValidator (独立验证器)
    ├── check_module() (检查单个模块)
    ├── validate_all() (验证所有依赖)
    └── print_report() (生成报告)
```

### 使用 importlib.util

我们使用 `importlib.util.find_spec()` 而不是简单的 `import` 来检查模块：

```python
import importlib.util

spec = importlib.util.find_spec('msal')
if spec is None:
    # 模块不存在
    print("msal 未安装")
else:
    # 模块存在
    print("msal 已安装")
```

**优点**:
- 不会导入模块（避免副作用）
- 更快速
- 可以检查未导入的模块

## 参考资料

- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [importlib Documentation](https://docs.python.org/3/library/importlib.html)

