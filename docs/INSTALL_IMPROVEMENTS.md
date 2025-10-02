# 安装脚本改进说明

## 📋 改进概述

根据代码审查，对 `install_launchd.sh` 进行了以下关键改进：

## ✅ 主要改进

### 1. **动态路径检测**（解决硬编码问题）

**改进前**：
```bash
PROJECT_DIR="/Users/jeff/Documents/文稿 - Zhe的Mac mini/codes/daily_summary_outlook"
PYTHON_PATH="/opt/anaconda3/bin/python"
```

**改进后**：
```bash
# 动态获取脚本所在目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 自动检测 Python 路径
PYTHON_PATH=$(which python 2>/dev/null || which python3 2>/dev/null || echo "")
```

**优势**：
- ✅ 可移植性强，适用于任何用户和路径
- ✅ 自动适配不同的 Python 安装位置
- ✅ 避免中文路径导致的潜在问题

### 2. **自动创建必要目录**

**新增**：
```bash
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/history"
mkdir -p "$LAUNCHD_DIR"
```

**解决问题**：
- ✅ 避免因缺少日志目录导致 launchd 启动失败
- ✅ 确保历史记录可以正常保存
- ✅ 自动创建 LaunchAgents 目录

### 3. **动态更新 plist 文件**

**新增功能**：
```bash
# 创建临时文件，替换路径
sed "s|/opt/anaconda3/bin/python|$PYTHON_PATH|g" "$PROJECT_DIR/$PLIST_FILE" | \
sed "s|/Users/jeff/...|$PROJECT_DIR|g" > "$TEMP_PLIST"
```

**优势**：
- ✅ 自动适配当前环境的路径
- ✅ 无需手动修改 plist 文件
- ✅ 支持不同用户和安装位置

### 4. **增强的验证逻辑**

**改进前**：
```bash
if launchctl list | grep -q "dailysummary"; then
```

**改进后**：
```bash
if launchctl list | grep -q "^[0-9-]*\s*[0-9]*\s*$SERVICE_NAME$"; then
```

**优势**：
- ✅ 精确匹配服务名称
- ✅ 避免误匹配其他服务
- ✅ 更可靠的验证结果

### 5. **完善的错误处理**

**新增检查**：
```bash
# 检查 Python 存在性
if [ -z "$PYTHON_PATH" ]; then
    echo "错误: 找不到 Python"
    exit 1
fi

# 检查文件权限
if [ ! -w "$LAUNCHD_DIR" ]; then
    echo "错误: 没有写入权限"
    exit 1
fi

# 检查主程序
if [ ! -f "$PROJECT_DIR/main.py" ]; then
    echo "错误: 找不到 main.py"
    exit 1
fi
```

**优势**：
- ✅ 提前发现问题
- ✅ 提供清晰的错误信息
- ✅ 避免部分安装导致的问题

### 6. **改进的卸载逻辑**

**改进前**：
```bash
launchctl unload "$LAUNCHD_DIR/$PLIST_FILE" 2>/dev/null || true
```

**改进后**：
```bash
if launchctl list | grep -q "^[0-9-]*\s*0\s*$SERVICE_NAME$"; then
    if ! launchctl unload "$LAUNCHD_DIR/$PLIST_FILE" 2>/dev/null; then
        echo "⚠️  无法卸载服务（可能未运行）"
    fi
fi
```

**优势**：
- ✅ 区分"服务未运行"和"卸载失败"
- ✅ 提供更准确的状态信息
- ✅ 避免隐藏真正的错误

## 🔧 使用方法

### 安装
```bash
cd /path/to/daily_summary_outlook
./install_launchd.sh
```

### 验证
```bash
# 查看服务状态
launchctl list | grep com.user.dailysummary

# 检查生成的 plist 文件
cat ~/Library/LaunchAgents/com.user.dailysummary.plist
```

### 测试
```bash
# 手动触发一次
launchctl start com.user.dailysummary

# 查看日志
tail -f logs/launchd_out.log
```

## 📊 改进效果对比

| 方面 | 改进前 | 改进后 |
|------|--------|--------|
| 可移植性 | ❌ 只能在特定用户机器运行 | ✅ 可在任何 macOS 机器运行 |
| Python 适配 | ❌ 硬编码路径 | ✅ 自动检测 |
| 目录管理 | ❌ 假设目录存在 | ✅ 自动创建 |
| 错误处理 | ⚠️ 基础检查 | ✅ 全面验证 |
| 验证准确性 | ⚠️ 模糊匹配 | ✅ 精确匹配 |
| 中文路径 | ⚠️ 可能有问题 | ✅ 动态处理 |

## ⚠️ 注意事项

1. **第一次运行前**：确保 `.env` 文件配置正确
2. **权限问题**：确保有 `~/Library/LaunchAgents` 的写入权限
3. **Python 版本**：脚本会自动检测 `python` 或 `python3`
4. **日志位置**：所有日志都在项目的 `logs/` 目录下

## 🧪 测试清单

- [ ] 在不同用户账户测试
- [ ] 在不同 Python 版本测试（Anaconda、系统自带等）
- [ ] 测试中文路径支持
- [ ] 测试重复安装（覆盖旧版本）
- [ ] 验证日志目录自动创建
- [ ] 确认服务能正常启动和执行

## 📝 后续优化建议

1. **配置文件化**：将关键配置（如执行时间）提取到配置文件
2. **交互式配置**：首次安装时询问用户偏好设置
3. **备份机制**：卸载前备份旧配置
4. **日志轮转**：自动清理旧日志文件
5. **健康检查**：定期检查服务状态的脚本
