# 脚本目录

本目录包含项目的安装和维护脚本。

## 📜 可用脚本

### 安装脚本
- **install_launchd.sh** - macOS LaunchD 自动安装脚本
  - 自动配置定时任务
  - 动态检测 Python 和项目路径
  - 创建必要的日志和历史记录目录

### 测试脚本
- **test_installation.sh** - 安装验证脚本
  - 检查依赖安装
  - 验证配置文件
  - 测试服务状态

### 配置文件
- **com.user.dailysummary.plist** - LaunchD 服务配置模板
  - 定时任务配置
  - 日志输出路径
  - 环境变量设置

## 🔧 使用方法

### 安装 LaunchD 服务
```bash
cd scripts
./install_launchd.sh
```

### 测试安装
```bash
cd scripts
./test_installation.sh
```

### 卸载服务
```bash
launchctl unload ~/Library/LaunchAgents/com.user.dailysummary.plist
rm ~/Library/LaunchAgents/com.user.dailysummary.plist
```

## 📖 详细文档

关于脚本的详细说明，请参考：
- `../docs/INSTALL_IMPROVEMENTS.md` - 安装脚本改进说明
- `../docs/LAUNCHD_SETUP.md` - LaunchD 设置指南

