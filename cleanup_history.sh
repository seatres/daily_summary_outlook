#!/bin/bash

# Git 历史清理脚本 - 移除敏感邮箱信息
# 警告：此脚本会重写 Git 历史！

set -e

echo "⚠️  警告：此操作将重写 Git 历史！"
echo "建议先备份当前仓库："
echo "  cp -r . ../daily_summary_outlook_backup"
echo ""
read -p "是否继续？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 1
fi

echo "开始清理 Git 历史..."

# 创建一个临时的配置文件，用于替换敏感信息
cat > /tmp/filter_script.sh << 'EOF'
#!/bin/bash
if [ "$GIT_COMMIT" = "124a2e3ba347804835788c7deed68e25b6afd9cf" ] || [ "$GIT_COMMIT" = "0a159852ec3a8d4b6f7c9e3a1b2d5f8a9c0e1f2a3" ]; then
    sed -i.bak 's/seatre83@outlook\.com/your_email@example.com/g' config.py
    sed -i.bak 's/seatre@icloud\.com/sender@example.com/g' config.py
    sed -i.bak 's/seatre83@outlook\.com/recipient@example.com/g' env.example
    rm -f config.py.bak env.example.bak
fi
EOF

chmod +x /tmp/filter_script.sh

# 使用 filter-branch 重写历史
git filter-branch --tree-filter '/tmp/filter_script.sh' --tag-name-filter cat -- --all

# 清理备份引用
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✅ Git 历史清理完成！"
echo ""
echo "下一步："
echo "1. 检查修改：git log --oneline"
echo "2. 强制推送到远程仓库：git push origin --force --all"
echo "3. 如果有标签：git push origin --force --tags"
echo ""
echo "⚠️  注意：强制推送会覆盖远程仓库的历史！"

rm -f /tmp/filter_script.sh

