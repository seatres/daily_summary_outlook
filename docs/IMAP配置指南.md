# Outlook IMAP配置指南 📧

本指南将帮助你配置IMAP方式访问个人Outlook邮箱(如: @outlook.com, @hotmail.com, @live.com等)。

## 📋 适用场景

**IMAP方式适用于**:
- ✅ 个人Microsoft账户(@outlook.com, @hotmail.com等)
- ✅ 无需Azure应用注册
- ✅ 配置简单快速

**Graph API方式适用于**:
- ✅ 组织Microsoft 365账户
- ✅ 需要高级功能
- ✅ 企业级应用

---

## 🚀 快速配置(3步完成)

### 第1步: 启用双重验证 (2分钟)

1. 访问 [Microsoft账户安全](https://account.microsoft.com/security)
2. 登录你的Outlook账号
3. 找到 **"双重验证"**
4. 如果未启用,点击 **"启用"**
5. 按照提示完成设置(通常需要手机验证)

### 第2步: 生成应用专用密码 (1分钟)

1. 在安全页面找到 **"应用密码"** (App passwords)
2. 点击 **"创建新的应用密码"**
3. 输入名称: `Daily Summary App`
4. 系统会生成一个16位密码(格式类似: `abcd efgh ijkl mnop`)
5. **重要**: 立即复制这个密码!

### 第3步: 配置环境变量 (1分钟)

编辑项目根目录的 `.env` 文件:

```bash
# 邮箱地址
OUTLOOK_EMAIL=你的邮箱@outlook.com

# 使用IMAP客户端
EMAIL_CLIENT_TYPE=imap

# IMAP密码(应用专用密码)
OUTLOOK_IMAP_PASSWORD=你刚才复制的16位密码

# SMTP密码(可以使用同一个应用专用密码)
OUTLOOK_SMTP_PASSWORD=你刚才复制的16位密码

# 邮件筛选
EMAIL_FILTER_SENDER=发送每日总结的邮箱

# Gemini AI密钥
GEMINI_API_KEY=你的Gemini_API_Key

# 接收结果的邮箱
SUMMARY_RECIPIENT=接收分析结果的邮箱
```

---

## ✅ 测试配置

运行测试脚本验证配置:

```bash
python test_outlook_imap.py
```

**预期输出**:
```
[1/5] 加载环境变量...
✓ 环境变量加载完成

[2/5] 创建IMAP客户端...
✓ 客户端创建成功

[3/5] 连接到IMAP服务器...
✓ 连接成功!

[4/5] 获取最近5封邮件...
✓ 成功获取 X 封邮件

[5/5] 测试SMTP发送...
✓ 邮件发送成功!

✓ 所有测试通过! IMAP配置正确
```

---

## 📊 完整配置说明

### 必需的环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `OUTLOOK_EMAIL` | 你的Outlook邮箱地址 | `john@outlook.com` |
| `EMAIL_CLIENT_TYPE` | 客户端类型(使用imap) | `imap` |
| `OUTLOOK_IMAP_PASSWORD` | 应用专用密码 | `abcdefghijklmnop` |
| `OUTLOOK_SMTP_PASSWORD` | SMTP密码(可与IMAP相同) | `abcdefghijklmnop` |

### 可选的环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `EMAIL_FILTER_SENDER` | 筛选发件人 | 无 |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `SAVE_HISTORY` | 是否保存历史 | `true` |

---

## 🔧 故障排除

### 问题1: 连接失败 - 认证错误

```
✗ 连接失败: IMAP认证失败
```

**原因**:
- 应用专用密码不正确
- 双重验证未启用
- 密码中有多余的空格

**解决方案**:
1. 确认双重验证已启用
2. 重新生成应用专用密码
3. 确保密码复制正确,没有多余空格

---

### 问题2: 找不到"应用密码"选项

**原因**:
- 双重验证未启用
- 账户是组织账户而非个人账户

**解决方案**:
1. 先启用双重验证
2. 刷新页面,重新查找"应用密码"
3. 如果仍找不到,可能是组织账户,需要使用Graph API方式

---

### 问题3: 无法获取邮件

```
✓ 连接成功!
✗ 获取邮件失败: 搜索失败
```

**原因**:
- IMAP搜索条件语法错误
- 邮箱中没有符合条件的邮件

**解决方案**:
1. 检查日志中的搜索条件
2. 先不加筛选条件测试获取所有邮件
3. 确认邮箱中有邮件

---

### 问题4: SMTP发送失败

```
✓ 连接成功!
✗ SMTP认证失败
```

**原因**:
- SMTP密码不正确
- 使用了账号密码而非应用专用密码

**解决方案**:
1. 确认使用的是应用专用密码
2. SMTP密码可以与IMAP密码相同
3. 重新生成应用专用密码

---

## 🔐 安全最佳实践

### 1. 保护应用专用密码

```bash
# ✅ 正确: 使用环境变量
OUTLOOK_IMAP_PASSWORD=your_password

# ❌ 错误: 硬编码在代码中
password = "abc123..."
```

### 2. 永远不要提交.env文件

`.env` 文件已在 `.gitignore` 中,确保不要提交到Git仓库。

### 3. 定期轮换密码

建议每3-6个月重新生成应用专用密码:
1. 撤销旧密码
2. 生成新密码
3. 更新.env文件

### 4. 最小权限原则

应用专用密码只用于这个项目,不要在其他地方使用。

---

## 📚 IMAP vs Graph API 对比

| 特性 | IMAP | Graph API |
|------|------|-----------|
| **账户类型** | 个人账户 | 组织账户 |
| **配置难度** | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| **需要Azure注册** | ❌ 不需要 | ✅ 需要 |
| **读取邮件** | ✅ 支持 | ✅ 支持 |
| **发送邮件** | ✅ SMTP | ✅ SMTP |
| **高级筛选** | ⭐⭐ 基础 | ⭐⭐⭐ 强大 |
| **性能** | ⭐⭐ 一般 | ⭐⭐⭐ 优秀 |
| **适用场景** | 个人项目 | 企业应用 |

---

## 🎯 完整配置示例

### .env文件完整示例

```bash
# ===== Outlook IMAP配置 =====
OUTLOOK_EMAIL=seatre83@outlook.com
EMAIL_CLIENT_TYPE=imap
OUTLOOK_IMAP_PASSWORD=abcd1234efgh5678
OUTLOOK_SMTP_PASSWORD=abcd1234efgh5678

# ===== 邮件筛选 =====
EMAIL_FILTER_SENDER=daily@example.com

# ===== Gemini AI =====
GEMINI_API_KEY=AIzaSy...

# ===== 接收邮箱 =====
SUMMARY_RECIPIENT=seatre83@outlook.com

# ===== 日志配置 =====
LOG_LEVEL=INFO

# ===== 历史记录 =====
SAVE_HISTORY=true
HISTORY_LEVEL=detailed
```

---

## 🚦 运行流程

配置完成后,运行主程序:

```bash
# 方式1: 立即执行一次
python main.py

# 方式2: 后台定时运行
nohup python main.py &
```

---

## 📝 常见问题FAQ

### Q1: IMAP密码是账号密码吗?

**A**: 不是! 必须使用 **应用专用密码**。

使用账号密码会导致认证失败。应用专用密码是16位的随机密码,在Microsoft账户安全设置中生成。

---

### Q2: 一个应用专用密码可以同时用于IMAP和SMTP吗?

**A**: 可以! 

在配置中,你可以将同一个应用专用密码同时用于:
- `OUTLOOK_IMAP_PASSWORD` (读取邮件)
- `OUTLOOK_SMTP_PASSWORD` (发送邮件)

---

### Q3: IMAP方式比Graph API慢吗?

**A**: 是的,但对于个人使用影响不大。

- IMAP: 适合每天处理少量邮件
- Graph API: 适合高频率、大量邮件处理

对于本项目(每天一次,读取少量邮件),IMAP完全够用。

---

### Q4: 可以随时切换回Graph API吗?

**A**: 可以!

只需修改 `.env` 文件:
```bash
EMAIL_CLIENT_TYPE=graph  # 改为graph
```

然后填写Graph API相关的配置即可。

---

### Q5: 如何确认IMAP是否启用?

**A**: Outlook个人账户默认启用IMAP,无需额外配置。

如果遇到连接问题,可以访问:
1. [Outlook设置](https://outlook.live.com/mail/options/mail/accounts)
2. 检查POP和IMAP设置

---

## ✨ 优势总结

使用IMAP方式的优势:

1. **✅ 简单快速** - 3步配置,5分钟完成
2. **✅ 无需Azure** - 不需要注册Azure应用
3. **✅ 适合个人** - 完美支持个人Outlook账户
4. **✅ 功能完整** - 满足读取和发送邮件的所有需求
5. **✅ 易于调试** - 问题排查简单直接

---

## 📞 获取帮助

如果遇到问题:

1. **运行诊断脚本**:
   ```bash
   python test_outlook_imap.py
   ```

2. **查看日志**:
   ```bash
   tail -f logs/workflow_$(date +%Y%m%d).log
   ```

3. **参考文档**:
   - 本文档: `IMAP配置指南.md`
   - 主文档: `README.md`
   - 快速开始: `快速开始.md`

---

## 🎉 配置完成!

现在你的Outlook个人账户已经配置好了!

**下一步**:
1. ✅ 运行测试: `python test_outlook_imap.py`
2. ✅ 启动程序: `python main.py`
3. ✅ 享受自动化! 🚀

---

**提示**: 如果未来需要切换到组织账户,可以参考 `OUTLOOK_配置指南.md` 配置Graph API方式。

