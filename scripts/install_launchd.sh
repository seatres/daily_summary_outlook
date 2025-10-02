#!/bin/bash

# 每日总结邮件自动化 - launchd 安装脚本

set -e

echo "======================================================================"
echo "每日总结邮件自动化 - launchd 定时任务安装"
echo "======================================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 动态获取项目目录（脚本所在目录）
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_FILE="com.user.dailysummary.plist"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
SERVICE_NAME="com.user.dailysummary"

echo "项目目录: $PROJECT_DIR"
echo "plist 文件: $PLIST_FILE"
echo ""

# 检查 plist 文件是否存在
if [ ! -f "$PROJECT_DIR/$PLIST_FILE" ]; then
    echo -e "${RED}✗ 错误: 找不到 $PLIST_FILE${NC}"
    echo "请确保文件存在于项目目录中"
    exit 1
fi

# 创建必要的目录
echo "检查并创建必要的目录..."
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/history"
mkdir -p "$LAUNCHD_DIR"
echo -e "${GREEN}✓ 目录已就绪${NC}"

# 动态检测 Python 路径
PYTHON_PATH=$(which python 2>/dev/null || which python3 2>/dev/null || echo "")
if [ -z "$PYTHON_PATH" ]; then
    echo -e "${RED}✗ 错误: 找不到 Python${NC}"
    echo "请确保已安装 Python 并在 PATH 中"
    exit 1
fi

echo "检测到 Python 路径: $PYTHON_PATH"

# 更新 plist 文件中的路径
TEMP_PLIST="/tmp/${PLIST_FILE}.tmp"
sed "s|/opt/anaconda3/bin/python|$PYTHON_PATH|g" "$PROJECT_DIR/$PLIST_FILE" | \
sed "s|/Users/jeff/Documents/文稿 - Zhe的Mac mini/codes/daily_summary_outlook|$PROJECT_DIR|g" > "$TEMP_PLIST"

# 验证 Python 和主程序
if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${RED}✗ 错误: Python 路径无效: $PYTHON_PATH${NC}"
    rm -f "$TEMP_PLIST"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/main.py" ]; then
    echo -e "${RED}✗ 错误: 找不到 main.py${NC}"
    rm -f "$TEMP_PLIST"
    exit 1
fi

# 检查权限
if [ ! -w "$LAUNCHD_DIR" ]; then
    echo -e "${RED}✗ 错误: 没有写入权限: $LAUNCHD_DIR${NC}"
    rm -f "$TEMP_PLIST"
    exit 1
fi

# 检查是否已安装
if [ -f "$LAUNCHD_DIR/$PLIST_FILE" ]; then
    echo -e "${YELLOW}⚠️  检测到已安装的服务${NC}"

    # 检查服务是否正在运行
    if launchctl list | grep -q "^[0-9-]*\s*0\s*$SERVICE_NAME$"; then
        echo "正在停止运行中的服务..."
        if ! launchctl unload "$LAUNCHD_DIR/$PLIST_FILE" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  无法卸载服务（可能未运行）${NC}"
        else
            echo -e "${GREEN}✓ 已停止旧服务${NC}"
        fi
    else
        echo "旧服务未运行"
    fi
fi

# 复制更新后的 plist 文件
echo "正在安装 plist 文件..."
cp "$TEMP_PLIST" "$LAUNCHD_DIR/$PLIST_FILE"
chmod 644 "$LAUNCHD_DIR/$PLIST_FILE"
rm -f "$TEMP_PLIST"
echo -e "${GREEN}✓ plist 文件已安装${NC}"

# 加载服务
echo "正在加载服务..."
if launchctl load "$LAUNCHD_DIR/$PLIST_FILE" 2>&1; then
    echo -e "${GREEN}✓ 服务已加载${NC}"
else
    echo -e "${RED}✗ 服务加载失败${NC}"
    echo "请检查 plist 文件格式和路径"
    exit 1
fi

# 验证服务（精确匹配）
echo ""
echo "正在验证服务..."
sleep 1  # 等待服务注册
if launchctl list | grep -q "^[0-9-]*\s*[0-9]*\s*$SERVICE_NAME$"; then
    echo -e "${GREEN}✓ 服务安装成功！${NC}"
else
    echo -e "${RED}✗ 服务验证失败${NC}"
    echo "服务可能未正确注册，请检查日志"
    exit 1
fi

echo ""
echo "======================================================================"
echo "安装完成"
echo "======================================================================"
echo ""
echo "📋 服务信息:"
echo "  - 服务名称: com.user.dailysummary"
echo "  - 执行时间: 每天 22:00 (晚上10点)"
echo "  - 执行命令: python main.py --once"
echo ""
echo "📊 查看日志:"
echo "  launchd 输出: tail -f $PROJECT_DIR/logs/launchd_out.log"
echo "  launchd 错误: tail -f $PROJECT_DIR/logs/launchd_err.log"
echo "  程序日志:     tail -f $PROJECT_DIR/logs/workflow_*.log"
echo ""
echo "🛠️  管理命令:"
echo "  查看状态:    launchctl list | grep dailysummary"
echo "  手动执行:    launchctl start com.user.dailysummary"
echo "  卸载服务:    launchctl unload $LAUNCHD_DIR/$PLIST_FILE"
echo ""
echo "🧪 立即测试:"
echo "  cd $PROJECT_DIR"
echo "  python main.py --once"
echo ""
echo "详细说明请查看: LAUNCHD_SETUP.md"
echo ""
