# Git 历史敏感信息清理指南

## 📋 问题概述

在提交 `124a2e3` 中，以下邮箱信息被意外提交到 GitHub：
- `seatre83@outlook.com`
- `seatre@icloud.com`

## 🔧 解决方案

### 方案 1：重写 Git 历史（最彻底）

#### 前置准备
```bash
# 1. 备份当前仓库
cd ..
cp -r daily_summary_outlook daily_summary_outlook_backup
cd daily_summary_outlook
```

#### 方法 A：使用 git-filter-repo（推荐）
```bash
# 安装 git-filter-repo
pip install git-filter-repo

# 创建替换规则文件
cat > replacements.txt << 'EOF'
seatre83@outlook.com==>your_email@example.com
seatre@icloud.com==>sender@example.com
EOF

# 执行清理
git filter-repo --replace-text replacements.txt --force

# 重新添加远程仓库（filter-repo 会删除 remote）
git remote add origin https://github.com/seatres/daily_summary_outlook.git

# 强制推送
git push origin --force --all
```

#### 方法 B：使用 BFG Repo-Cleaner
```bash
# 下载 BFG
# macOS: brew install bfg
# 或从 https://rtyley.github.io/bfg-repo-cleaner/ 下载

# 创建替换文件
cat > passwords.txt << 'EOF'
seatre83@outlook.com
seatre@icloud.com
EOF

# 运行 BFG
bfg --replace-text passwords.txt

# 清理
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送
git push origin --force --all
```

---

### 方案 2：创建新的干净历史（最简单）

如果这是一个新项目，建议直接重建仓库：

```bash
# 1. 删除 .git 目录
rm -rf .git

# 2. 重新初始化仓库
git init

# 3. 确保 .gitignore 正确
# （已经配置好了）

# 4. 添加所有文件（.env 会被自动忽略）
git add .

# 5. 提交
git commit -m "Initial commit with clean history"

# 6. 在 GitHub 上删除原仓库，创建新仓库
# 或者强制推送覆盖
git remote add origin https://github.com/seatres/daily_summary_outlook.git
git push origin main --force
```

---

### 方案 3：使其成为私有仓库 + 修改邮箱（临时方案）

如果暂时不想重写历史：

1. **立即将 GitHub 仓库设为私有**
   - 访问：https://github.com/seatres/daily_summary_outlook/settings
   - 滚动到 "Danger Zone"
   - 点击 "Change repository visibility" → "Make private"

2. **更换邮箱地址**（如果可能）
   - 虽然邮箱地址已泄漏，但这些只是普通邮箱（不是 API 密钥）
   - 风险相对较低，主要是会收到垃圾邮件

---

## 🔒 后续安全措施

### 1. 更新 .gitignore（已完成）
```gitignore
.env
.env.*
*.key
secrets/
```

### 2. 使用 git-secrets 防止未来泄漏
```bash
# 安装
brew install git-secrets

# 在仓库中配置
git secrets --install
git secrets --register-aws

# 添加自定义规则
git secrets --add '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
```

### 3. 使用 pre-commit hooks
```bash
# 安装 pre-commit
pip install pre-commit

# 创建 .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: check-added-large-files
      - id: detect-private-key
      - id: check-yaml
      - id: check-json
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
EOF

# 安装 hooks
pre-commit install
```

### 4. 定期扫描敏感信息
```bash
# 使用 trufflehog 扫描
docker run --rm -v $(pwd):/repo trufflesecurity/trufflehog:latest filesystem /repo
```

---

## 📊 风险评估

| 泄漏信息 | 风险等级 | 说明 |
|---------|---------|------|
| 邮箱地址 | 🟡 中等 | 可能收到垃圾邮件，建议设置邮件过滤 |
| API 密钥 | 🔴 高危 | **未泄漏** - 已正确配置在 .env 中 |
| 密码 | 🔴 高危 | **未泄漏** - 已正确配置在 .env 中 |

## ✅ 推荐行动

**对于你的情况，我推荐方案 2（重建干净历史）**，因为：
1. 这是一个新项目（只有 3 个提交）
2. 操作简单，风险最低
3. 不需要安装额外工具
4. 只泄漏了邮箱地址，没有泄漏 API 密钥或密码

## 🚨 紧急情况处理

如果有 API 密钥或密码泄漏：
1. **立即撤销/重置所有密钥**
2. **立即将仓库设为私有**
3. **联系 GitHub Support 请求缓存清理**
4. **考虑使用 GitHub Secret Scanning alerts**

---

## 📞 相关链接

- [GitHub - Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [git-filter-repo](https://github.com/newren/git-filter-repo)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [git-secrets](https://github.com/awslabs/git-secrets)

