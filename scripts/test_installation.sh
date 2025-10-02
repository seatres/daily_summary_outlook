#!/bin/bash

# 安装验证测试脚本

echo "======================================================================"
echo "每日总结邮件自动化 - 安装验证"
echo "======================================================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 动态获取项目目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="com.user.dailysummary"

echo -e "${BLUE}📋 测试项目：${NC}"
echo "  项目目录: $PROJECT_DIR"
echo ""

# 测试计数
PASSED=0
FAILED=0

# 测试函数
test_item() {
    local name="$1"
    local test_cmd="$2"

    echo -n "  [$name] "
    if eval "$test_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        ((FAILED++))
        return 1
    fi
}

# 1. 基础环境检查
echo -e "${BLUE}1️⃣  基础环境检查${NC}"
test_item "Python 可用" "which python || which python3"
test_item "项目目录存在" "[ -d '$PROJECT_DIR' ]"
test_item "main.py 存在" "[ -f '$PROJECT_DIR/main.py' ]"
test_item ".env 文件存在" "[ -f '$PROJECT_DIR/.env' ]"
echo ""

# 2. 目录结构检查
echo -e "${BLUE}2️⃣  目录结构检查${NC}"
test_item "logs 目录" "[ -d '$PROJECT_DIR/logs' ]"
test_item "history 目录" "[ -d '$PROJECT_DIR/history' ]"
test_item "LaunchAgents 目录" "[ -d '$HOME/Library/LaunchAgents' ]"
echo ""

# 3. plist 文件检查
echo -e "${BLUE}3️⃣  plist 文件检查${NC}"
test_item "原始 plist 存在" "[ -f '$PROJECT_DIR/com.user.dailysummary.plist' ]"
test_item "已安装 plist" "[ -f '$HOME/Library/LaunchAgents/com.user.dailysummary.plist' ]"
test_item "plist 权限正确" "[ -r '$HOME/Library/LaunchAgents/com.user.dailysummary.plist' ]"
echo ""

# 4. launchd 服务检查
echo -e "${BLUE}4️⃣  launchd 服务检查${NC}"
test_item "服务已注册" "launchctl list | grep -q '$SERVICE_NAME'"

# 详细服务信息
if launchctl list | grep -q "$SERVICE_NAME"; then
    echo "  ${GREEN}服务状态信息：${NC}"
    launchctl list | grep "$SERVICE_NAME" | while read -r line; do
        echo "    $line"
    done
fi
echo ""

# 5. Python 程序检查
echo -e "${BLUE}5️⃣  Python 程序检查${NC}"
PYTHON_PATH=$(which python 2>/dev/null || which python3 2>/dev/null)

if [ -n "$PYTHON_PATH" ]; then
    test_item "程序语法检查" "cd '$PROJECT_DIR' && $PYTHON_PATH -m py_compile main.py"
    test_item "依赖包检查" "cd '$PROJECT_DIR' && $PYTHON_PATH -c 'from dotenv import load_dotenv; from workflow_tools.email import QQIMAPClient'"
fi
echo ""

# 6. 配置文件检查
echo -e "${BLUE}6️⃣  配置文件检查${NC}"

if [ -f "$PROJECT_DIR/.env" ]; then
    # 检查关键配置
    source "$PROJECT_DIR/.env" 2>/dev/null || true

    test_item "EMAIL_CLIENT_TYPE" "[ ! -z '$EMAIL_CLIENT_TYPE' ]"
    test_item "EMAIL_ADDRESS" "[ ! -z '$EMAIL_ADDRESS' ]"
    test_item "EMAIL_PASSWORD" "[ ! -z '$EMAIL_PASSWORD' ]"
    test_item "GEMINI_API_KEY" "[ ! -z '$GEMINI_API_KEY' ]"
    test_item "SUMMARY_RECIPIENT" "[ ! -z '$SUMMARY_RECIPIENT' ]"
else
    echo -e "  ${RED}✗ .env 文件不存在${NC}"
fi
echo ""

# 7. 日志文件检查
echo -e "${BLUE}7️⃣  日志文件检查${NC}"
test_item "日志目录可写" "[ -w '$PROJECT_DIR/logs' ]"

# 检查是否有日志文件
LOG_COUNT=$(ls -1 "$PROJECT_DIR/logs"/*.log 2>/dev/null | wc -l)
echo "  日志文件数量: $LOG_COUNT"
echo ""

# 8. 手动执行测试
echo -e "${BLUE}8️⃣  手动执行测试${NC}"
echo "  正在测试 --once 模式..."

# macOS 使用 gtimeout (需要 brew install coreutils) 或直接运行
if cd "$PROJECT_DIR" && $PYTHON_PATH main.py --once > /tmp/test_once.log 2>&1; then
    echo -e "  ${GREEN}✓ 程序执行成功${NC}"
    ((PASSED++))

    # 检查日志输出
    if grep -q "任务执行完成\|程序已退出" /tmp/test_once.log; then
        echo -e "  ${GREEN}✓ 任务正常完成${NC}"
        ((PASSED++))
    else
        echo -e "  ${YELLOW}⚠️  任务可能未完成${NC}"
        echo "  最后几行日志:"
        tail -5 /tmp/test_once.log | sed 's/^/    /'
    fi
else
    echo -e "  ${RED}✗ 程序执行失败${NC}"
    echo "  查看详细日志: /tmp/test_once.log"
    echo "  最后几行错误:"
    tail -10 /tmp/test_once.log | sed 's/^/    /'
    ((FAILED++))
fi
echo ""

# 总结
echo "======================================================================"
echo -e "${BLUE}测试总结${NC}"
echo "======================================================================"
echo -e "  ${GREEN}通过: $PASSED${NC}"
echo -e "  ${RED}失败: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！系统已正确安装。${NC}"
    echo ""
    echo "下一步："
    echo "  1. 手动触发测试: launchctl start $SERVICE_NAME"
    echo "  2. 查看执行日志: tail -f $PROJECT_DIR/logs/launchd_out.log"
    echo "  3. 等待定时执行: 每天 22:00 自动运行"
    exit 0
else
    echo -e "${RED}⚠️  发现 $FAILED 个问题，请检查并修复。${NC}"
    echo ""
    echo "故障排查："
    echo "  1. 检查 .env 配置: cat $PROJECT_DIR/.env"
    echo "  2. 查看错误日志: tail -50 $PROJECT_DIR/logs/launchd_err.log"
    echo "  3. 查看详细日志: tail -50 /tmp/test_once.log"
    exit 1
fi
