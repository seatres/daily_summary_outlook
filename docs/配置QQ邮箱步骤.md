# 配置 QQ 邮箱步骤

## 📋 当前配置状态

根据您的 `.env` 文件，当前配置：
- ❌ `EMAIL_CLIENT_TYPE=imap` （应该是 `qq`）
- ❌ 缺少 `EMAIL_ADDRESS` 配置
- ❌ 缺少 `EMAIL_PASSWORD` 配置

## 🔧 修改 .env 文件

请按以下步骤修改您的 `.env` 文件：

### 步骤 1：打开 .env 文件

```bash
nano .env
# 或使用其他编辑器
# code .env
# vim .env
```

### 步骤 2：修改配置

找到以下行并修改：

```bash
# 原来的配置（需要修改）
EMAIL_CLIENT_TYPE=imap

# 改为（使用 QQ 邮箱）
EMAIL_CLIENT_TYPE=qq
```

### 步骤 3：添加 QQ 邮箱配置

在 `.env` 文件中添加或修改以下配置：

```bash
# ===== QQ 邮箱配置 =====
# 您的 QQ 邮箱地址
EMAIL_ADDRESS=你的QQ号@qq.com

# QQ 邮箱授权码（不是 QQ 密码！）
EMAIL_PASSWORD=你的16位授权码

# 发送每日总结的邮箱（用于筛选）
EMAIL_FILTER_SENDER=seatre@icloud.com

# 接收分析结果的邮箱
SUMMARY_RECIPIENT=seatre@foxmail.com
```

### 步骤 4：获取 QQ 邮箱授权码

如果您还没有授权码，请按以下步骤获取：

1. **登录 QQ 邮箱**
   - 访问：https://mail.qq.com
   - 使用您的 QQ 号和密码登录

2. **进入设置**
   - 点击页面右上角"设置"
   - 选择"账户"标签

3. **开启 IMAP/SMTP 服务**
   - 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
   - 找到"IMAP/SMTP服务"
   - 点击"开启"

4. **生成授权码**
   - 系统会要求发送短信验证
   - 按提示用手机发送指定内容到指定号码
   - 发送成功后，页面会显示一个 **16 位授权码**
   - **立即复制保存这个授权码！**

5. **填入 .env 文件**
   ```bash
   EMAIL_PASSWORD=你复制的16位授权码
   ```

## 📝 完整的 .env 配置示例

```bash
# ===== 邮件客户端类型配置 =====
EMAIL_CLIENT_TYPE=qq

# ===== QQ 邮箱配置 =====
EMAIL_ADDRESS=12345678@qq.com
EMAIL_PASSWORD=abcdefghijklmnop

# 邮件筛选发件人
EMAIL_FILTER_SENDER=seatre@icloud.com

# 总结结果接收邮箱
SUMMARY_RECIPIENT=seatre@foxmail.com

# ===== Gemini AI 配置 =====
GEMINI_API_KEY=你的Gemini_API_Key

# ===== 日志配置 =====
LOG_LEVEL=INFO

# ===== 历史记录配置 =====
SAVE_HISTORY=true
HISTORY_LEVEL=detailed
```

## ✅ 验证配置

配置完成后，运行测试脚本：

```bash
python test_qq_email.py
```

测试脚本会：
1. ✓ 检查配置是否正确
2. ✓ 测试连接到 QQ 邮箱
3. ✓ 测试读取邮件
4. ✓ 测试发送邮件（可选）

## 🚨 常见问题

### 问题 1：535 Authentication failed

**原因**：
- 使用了 QQ 密码而不是授权码
- 授权码错误
- 未开启 IMAP/SMTP 服务

**解决**：
- 确认使用的是授权码
- 重新生成授权码
- 确认 IMAP/SMTP 服务已开启

### 问题 2：找不到 EMAIL_ADDRESS

**原因**：
- .env 文件中没有配置 `EMAIL_ADDRESS`

**解决**：
- 在 .env 文件中添加 `EMAIL_ADDRESS=你的QQ邮箱`

### 问题 3：连接超时

**原因**：
- 网络问题
- 防火墙阻止

**解决**：
- 检查网络连接
- 确保防火墙允许 993（IMAP）和 587（SMTP）端口

## 🎯 快速配置命令

如果您想快速创建配置，可以使用以下命令：

```bash
# 备份现有配置
cp .env .env.backup

# 在 .env 文件末尾添加 QQ 邮箱配置
cat >> .env << 'EOF'

# ===== QQ 邮箱配置 =====
EMAIL_CLIENT_TYPE=qq
EMAIL_ADDRESS=你的QQ号@qq.com
EMAIL_PASSWORD=你的16位授权码
EOF

# 编辑并填入实际值
nano .env
```

## 📞 需要帮助？

如果遇到问题：
1. 查看测试脚本的错误提示
2. 查看 QQ 邮箱配置指南：`QQ邮箱配置指南.md`
3. 检查日志文件：`logs/workflow_*.log`

