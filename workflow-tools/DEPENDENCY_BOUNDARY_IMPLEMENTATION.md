# 依赖边界检查实现总结

本文档总结了为 `workflow-tools` 包实现的依赖边界检查机制。

## 问题背景

在原始实现中，依赖检查只在运行时进行。这意味着：

- ❌ 用户在安装时不知道是否缺少依赖
- ❌ 错误只在首次使用功能时才出现
- ❌ 难以在安装时验证环境配置

## 解决方案

实现了三层依赖验证机制：

### 1. 安装时验证 (Install-time Validation)

**文件**: `workflow-tools/setup.py`

**实现方式**:
- 自定义 `PostInstallCommand` 类扩展 `setuptools.command.install`
- 自定义 `PostDevelopCommand` 类扩展 `setuptools.command.develop`
- 在安装完成后自动执行依赖检查

**关键代码**:
```python
class PostInstallCommand(install):
    """安装后执行依赖验证"""
    def run(self):
        install.run(self)
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """验证关键依赖的安装"""
        # 检查所有可选依赖
        # 输出清晰的安装提示
```

**效果**:
```bash
$ pip install -e .

=== 依赖边界检查 ===
✓  [email] 已安装: msal
✓  [email] 已安装: requests
⚠️  [ai] 缺少: google.generativeai (Gemini AI)
   提示: pip install workflow-tools[ai]
===================
```

### 2. 独立验证工具 (Standalone Validator)

**文件**: `workflow-tools/validate_dependencies.py`

**实现方式**:
- 独立的可执行Python脚本
- 使用 `importlib.util.find_spec()` 检查模块
- 提供多种输出模式和退出码

**使用方法**:
```bash
# 基本检查
python validate_dependencies.py

# 详细模式
python validate_dependencies.py -v

# 严格模式（CI/CD）
python validate_dependencies.py --strict
```

**特性**:
- 🎯 精确检测所有依赖
- 📊 生成详细报告
- 🔄 适合CI/CD集成
- 🎨 友好的彩色输出

### 3. 运行时验证 (Runtime Validation)

**文件**: `workflow-tools/workflow_tools/email/outlook/outlook_client.py` (示例)

**实现方式**:
- 在模块顶部尝试导入依赖
- 设置可用性标志
- 在类初始化时检查标志

**关键代码**:
```python
try:
    from msal import ConfidentialClientApplication
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False

class OutlookClient(EmailClientBase):
    def __init__(self, ...):
        if not MSAL_AVAILABLE:
            raise ImportError("请安装msal: pip install msal")
```

**效果**:
- 提供清晰的错误消息
- 避免模糊的导入错误
- 告诉用户如何解决问题

## 文件清单

### 核心实现

1. **setup.py** (修改)
   - 添加自定义安装命令
   - 实现安装时验证逻辑
   - 版本号提升至 0.1.1

2. **validate_dependencies.py** (新建)
   - 独立验证工具
   - 命令行接口
   - 详细报告生成

### 文档

3. **DEPENDENCY_VALIDATION.md** (新建)
   - 完整的用户文档
   - 使用指南和示例
   - 故障排除建议

4. **DEPENDENCY_BOUNDARY_IMPLEMENTATION.md** (本文件)
   - 实现总结
   - 技术细节

5. **README.md** (更新)
   - 添加依赖验证章节
   - 使用示例

### 测试和示例

6. **tests/test_dependency_validation.py** (新建)
   - 单元测试
   - 覆盖核心功能

7. **examples/check_dependencies.py** (新建)
   - 使用示例
   - 最佳实践演示

## 技术细节

### 使用 importlib.util 而非简单 import

**原因**:
```python
# ❌ 简单 import 会导入模块（有副作用）
try:
    import some_module
except ImportError:
    pass

# ✅ importlib.util 只检查不导入
spec = importlib.util.find_spec('some_module')
if spec is None:
    print("模块不存在")
```

**优点**:
- 更快速（不执行模块代码）
- 无副作用
- 更适合批量检查

### 退出码设计

```python
0: 所有核心依赖已安装
1: 核心依赖缺失（严重错误）
2: 只有可选依赖缺失（警告）
```

这使得工具可以在CI/CD中正确使用：
```bash
python validate_dependencies.py
if [ $? -eq 1 ]; then
    echo "核心依赖缺失，终止构建"
    exit 1
fi
```

### 依赖分类

**核心依赖** (必需):
- `typing-extensions` - 类型提示
- `python-dotenv` - 环境配置

**可选依赖** (按功能):
- `email`: msal, requests
- `ai`: google-generativeai
- `notes`: notion-client
- `storage`: boto3, botocore
- `scheduler`: APScheduler, pytz

## 用户体验改进

### 之前 ❌

```bash
$ python main.py
Traceback (most recent call last):
  File "main.py", line 5, in <module>
    from workflow_tools.email.outlook import OutlookClient
  ...
ModuleNotFoundError: No module named 'msal'
```

用户不知道：
- 需要安装什么
- 如何安装
- 是否是配置问题

### 之后 ✅

**安装时**:
```bash
$ pip install -e .[email]

=== 依赖边界检查 ===
✓  [email] 已安装: msal
✓  [email] 已安装: requests
===================
```

**运行时**:
```bash
$ python main.py
ImportError: 请安装msal: pip install msal
```

用户清楚地知道：
- 缺少什么依赖
- 如何安装
- 属于哪个功能

## 最佳实践

### 1. 开发环境

```bash
# 安装所有依赖（包括开发工具）
cd workflow-tools
pip install -e .[all,dev]

# 验证安装
python validate_dependencies.py -v
```

### 2. 生产环境

```bash
# 只安装需要的功能
pip install workflow-tools[email,ai,scheduler]

# 验证安装
python -m workflow_tools.validate_dependencies
```

### 3. CI/CD 集成

```yaml
# .github/workflows/test.yml
- name: Install dependencies
  run: |
    pip install -e .[all,dev]
    
- name: Validate dependencies
  run: |
    python validate_dependencies.py --strict
```

### 4. Docker 镜像

```dockerfile
# 安装运行时依赖
RUN pip install workflow-tools[email,ai,scheduler]

# 验证（构建时失败而非运行时）
RUN python -c "from validate_dependencies import DependencyValidator; \
    v = DependencyValidator(); \
    assert v.validate_all(), 'Dependencies missing'"
```

## 性能影响

### 安装时验证
- **开销**: ~0.1-0.5秒
- **频率**: 每次安装（很少）
- **影响**: 可忽略

### 运行时验证
- **开销**: ~0.001秒（每个模块）
- **频率**: 每次导入（很少）
- **影响**: 可忽略

### 独立工具
- **开销**: ~0.1秒
- **频率**: 手动运行
- **影响**: 无

## 未来改进

### 可能的增强

1. **版本检查**
   ```python
   # 不仅检查是否安装，还检查版本
   import msal
   if msal.__version__ < '1.20.0':
       print("msal版本过低，建议升级")
   ```

2. **自动修复**
   ```python
   # 提供自动安装选项
   if not check_module('msal'):
       answer = input("是否自动安装msal? [y/n]: ")
       if answer.lower() == 'y':
           subprocess.run(['pip', 'install', 'msal'])
   ```

3. **配置文件支持**
   ```yaml
   # .dependency-check.yml
   strict_mode: false
   auto_install: false
   ignore_optional: ['dev', 'docs']
   ```

4. **IDE集成**
   - VS Code 扩展
   - PyCharm 插件
   - 实时依赖状态显示

## 相关资源

- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools Custom Commands](https://setuptools.pypa.io/en/latest/userguide/extension.html)
- [importlib Documentation](https://docs.python.org/3/library/importlib.html)

## 总结

通过实现三层依赖验证机制，我们：

✅ **提升了用户体验** - 清晰的错误消息和安装提示
✅ **提前发现问题** - 安装时而非运行时
✅ **支持CI/CD** - 适合自动化环境
✅ **保持灵活性** - 可选依赖不阻塞安装
✅ **提供工具** - 随时手动验证依赖状态

这个实现遵循了Python打包的最佳实践，并提供了企业级的依赖管理能力。

