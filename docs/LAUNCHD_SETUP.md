# macOS 定时任务设置指南

本指南说明如何使用 macOS launchd 设置每天晚上10点自动执行邮件总结任务。

## 📋 运行模式

程序现在支持两种运行模式：

### 1. 立即执行模式（推荐用于 launchd）
```bash
python main.py --once
```
- ✅ 立即执行一次任务
- ✅ 执行完毕后自动退出
- ✅ 读取过去24小时内的邮件
- ✅ 适合定时触发

### 2. 定时任务模式（持续运行）
```bash
python main.py
```
- ✅ 程序持续运行
- ✅ 每晚22:00自动执行
- ⚠️ 需要保持终端开启或后台运行

## 🚀 设置 launchd 定时任务（推荐）

### 步骤 1: 复制 plist 文件

```bash
cp com.user.dailysummary.plist ~/Library/LaunchAgents/
```

### 步骤 2: 加载服务

```bash
launchctl load ~/Library/LaunchAgents/com.user.dailysummary.plist
```

### 步骤 3: 验证服务状态

```bash
# 查看服务是否加载
launchctl list | grep dailysummary

# 查看服务详细信息
launchctl list com.user.dailysummary
```

## ⏰ 执行时间

- **每天晚上 22:00**（10点）自动执行
- 读取过去 24 小时内的"每日总结"邮件
- 使用 Gemini AI 分析后发送结果

## 📊 查看日志

### launchd 日志
```bash
# 标准输出
tail -f logs/launchd_out.log

# 错误输出
tail -f logs/launchd_err.log
```

### 程序日志
```bash
# 查看今天的日志
tail -f logs/workflow_$(date +%Y%m%d).log

# 查看所有日志
ls -lh logs/
```

## 🛠️ 管理服务

### 卸载服务
```bash
launchctl unload ~/Library/LaunchAgents/com.user.dailysummary.plist
```

### 重新加载服务（修改配置后）
```bash
launchctl unload ~/Library/LaunchAgents/com.user.dailysummary.plist
launchctl load ~/Library/LaunchAgents/com.user.dailysummary.plist
```

### 手动触发一次
```bash
launchctl start com.user.dailysummary
```

### 删除服务
```bash
launchctl unload ~/Library/LaunchAgents/com.user.dailysummary.plist
rm ~/Library/LaunchAgents/com.user.dailysummary.plist
```

## 🧪 测试

### 测试立即执行模式
```bash
python main.py --once
```

### 测试定时任务模式
```bash
python main.py
# 程序会持续运行，按 Ctrl+C 停止
```

## ⚠️ 重要提示

1. **Python 路径**: 确保 plist 中的 Python 路径正确
   ```bash
   which python  # 查看 Python 路径
   ```

2. **权限问题**: 如果遇到权限问题，检查文件权限
   ```bash
   chmod 644 ~/Library/LaunchAgents/com.user.dailysummary.plist
   ```

3. **环境变量**: launchd 运行时可能无法访问 `.env` 文件
   - 确保 `.env` 文件在项目根目录
   - 或在 plist 中添加完整的环境变量

4. **时区**: 执行时间基于系统时区（macOS 系统时间）

## 🔍 故障排查

### 服务未执行
1. 检查服务是否加载
   ```bash
   launchctl list | grep dailysummary
   ```

2. 查看错误日志
   ```bash
   tail -50 logs/launchd_err.log
   ```

3. 手动测试
   ```bash
   python main.py --once
   ```

### Python 路径错误
```bash
# 查找正确的 Python 路径
which python
# 或
which python3

# 更新 plist 文件中的路径
```

### .env 文件未加载
在 plist 中添加环境变量，或使用绝对路径加载 .env：
```python
load_dotenv('/Users/jeff/Documents/文稿 - Zhe的Mac mini/codes/daily_summary_outlook/.env')
```

## 📝 修改执行时间

编辑 `~/Library/LaunchAgents/com.user.dailysummary.plist`：

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>22</integer>  <!-- 修改这里，0-23 -->
    <key>Minute</key>
    <integer>0</integer>   <!-- 修改这里，0-59 -->
</dict>
```

然后重新加载服务：
```bash
launchctl unload ~/Library/LaunchAgents/com.user.dailysummary.plist
launchctl load ~/Library/LaunchAgents/com.user.dailysummary.plist
```

## ✅ 验证设置

1. **立即测试一次**:
   ```bash
   python main.py --once
   ```

2. **检查邮箱**: 确认收到AI分析邮件

3. **查看日志**:
   ```bash
   tail -f logs/workflow_*.log
   ```

4. **等待定时执行**: 第二天晚上10点自动运行
