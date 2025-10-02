# 依赖检查快速参考

快速参考指南，用于检查和管理 `workflow-tools` 的依赖。

## 快速命令

```bash
# 检查依赖状态
python validate_dependencies.py

# 详细报告
python validate_dependencies.py -v

# 严格模式（CI/CD）
python validate_dependencies.py --strict

# 安装所有依赖
pip install -e .[all]

# 按功能安装
pip install -e .[email,ai,scheduler]
```

## 依赖速查表

| 功能 | 依赖包 | 安装命令 |
|------|--------|----------|
| 核心 | typing-extensions, python-dotenv | 自动安装 |
| 邮件 | msal, requests | `pip install -e .[email]` |
| AI | google-generativeai | `pip install -e .[ai]` |
| 笔记 | notion-client | `pip install -e .[notes]` |
| 存储 | boto3, botocore | `pip install -e .[storage]` |
| 调度 | APScheduler, pytz | `pip install -e .[scheduler]` |
| 全部 | 以上所有 | `pip install -e .[all]` |

## 常见问题

### ❓ 如何知道我缺少哪些依赖？

```bash
python validate_dependencies.py -v
```

### ❓ 安装后如何验证？

```bash
python validate_dependencies.py
# 退出码 0 表示成功
echo $?
```

### ❓ 在CI中如何使用？

```bash
python validate_dependencies.py --strict
if [ $? -ne 0 ]; then
    echo "依赖检查失败"
    exit 1
fi
```

### ❓ 如何只安装我需要的功能？

```bash
# 例如：只需要邮件和调度功能
pip install -e .[email,scheduler]
```

## 错误码

- `0` = ✅ 所有核心依赖已安装
- `1` = ❌ 核心依赖缺失（严重）
- `2` = ⚠️  可选依赖缺失

## 示例输出

### 正常情况

```
============================================================
📦 Workflow-Tools 依赖检查报告
============================================================

✅ 所有核心依赖已正确安装!

============================================================
```

### 缺少依赖

```
============================================================
📦 Workflow-Tools 依赖检查报告
============================================================

⚠️  缺失的依赖:

  [ai]
    ✗ google.generativeai - Gemini AI
    💡 安装建议: pip install workflow-tools[ai]

💡 一次性安装所有依赖:
   pip install workflow-tools[all]

============================================================
```

## 编程接口

```python
from validate_dependencies import DependencyValidator

# 创建验证器
validator = DependencyValidator()

# 验证所有依赖
core_ok = validator.validate_all()

# 检查特定模块
if validator.check_module('msal'):
    from workflow_tools.email.outlook import OutlookClient
    # 使用OutlookClient
else:
    print("邮件功能不可用")

# 获取退出码
exit_code = validator.get_exit_code()
```

## 更多信息

- 完整文档: [DEPENDENCY_VALIDATION.md](./DEPENDENCY_VALIDATION.md)
- 实现细节: [DEPENDENCY_BOUNDARY_IMPLEMENTATION.md](./DEPENDENCY_BOUNDARY_IMPLEMENTATION.md)
- 使用示例: [examples/check_dependencies.py](./examples/check_dependencies.py)

