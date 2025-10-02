# Azure应用程序权限配置详解 🔑

## 📋 正确的权限名称

根据Microsoft Graph应用程序权限列表,邮件相关权限的**准确名称**如下:

### 邮件权限清单

| 权限名称 | 描述 | 是否需要管理员同意 | 用途 |
|---------|------|------------------|------|
| **Mail.Read** | Read mail in all mailboxes | ✅ 是 | **读取邮件(推荐)** |
| **Mail.ReadBasic** | Read basic mail in all mailboxes | ✅ 是 | 读取基本邮件信息 |
| **Mail.ReadBasic.All** | Read basic mail in all mailboxes | ✅ 是 | 读取基本邮件信息 |
| **Mail.ReadWrite** | Read and write mail in all mailboxes | ✅ 是 | 读写邮件(可选) |
| **Mail.Send** | Send mail as any user | ✅ 是 | 发送邮件(不需要) |
| **Mail-Advanced.ReadWrite.All** | Read and write mail in all mailboxes, including modifying existing non-draft mails | ✅ 是 | 高级邮件操作 |

---

## ✅ 本项目推荐配置

### 方案1: 最小权限(推荐) ⭐

仅添加一个权限:

```
权限名称: Mail.Read
描述: Read mail in all mailboxes
类型: 应用程序权限
```

**优点**:
- ✅ 满足读取邮件的所有需求
- ✅ 遵循最小权限原则
- ✅ 安全性最高

**缺点**:
- ❌ 无法标记邮件为已读
- ❌ 无法修改邮件属性

---

### 方案2: 扩展权限(可选)

如果需要更多功能,添加:

```
权限1: Mail.Read
描述: Read mail in all mailboxes
类型: 应用程序权限

权限2: Mail.ReadWrite
描述: Read and write mail in all mailboxes  
类型: 应用程序权限
```

**额外功能**:
- ✅ 可以标记邮件为已读
- ✅ 可以移动邮件到其他文件夹
- ✅ 可以修改邮件元数据

---

## 🔍 在Azure门户中查找权限

### 步骤1: 进入API权限页面

1. 打开Azure Portal: https://portal.azure.com/
2. 进入 **应用注册** → 选择你的应用
3. 点击左侧 **API权限**
4. 点击 **+ 添加权限**

### 步骤2: 选择Microsoft Graph

1. 在权限选择界面,点击 **Microsoft Graph**
2. 选择 **应用程序权限** (Application permissions)
   - ⚠️ **不是** "委托权限" (Delegated permissions)

### 步骤3: 搜索邮件权限

在搜索框中输入: **`mail`**

你会看到如下权限列表:

```
📧 Mail
  ├─ Mail.Read                          应用程序权限
  ├─ Mail.ReadBasic                     应用程序权限
  ├─ Mail.ReadBasic.All                 应用程序权限
  ├─ Mail.ReadWrite                     应用程序权限
  └─ Mail.Send                          应用程序权限

📧 Mail-Advanced
  └─ Mail-Advanced.ReadWrite.All        应用程序权限

📧 MailboxFolder
  ├─ MailboxFolder.Read.All             应用程序权限
  └─ MailboxFolder.ReadWrite.All        应用程序权限

📧 MailboxItem
  ├─ MailboxItem.ImportExport.All       应用程序权限
  └─ MailboxItem.Read.All               应用程序权限

📧 MailboxSettings
  ├─ MailboxSettings.Read               应用程序权限
  └─ MailboxSettings.ReadWrite          应用程序权限
```

### 步骤4: 选择并添加

1. **展开 "Mail" 分组**
2. **勾选** `Mail.Read` 左侧的复选框
3. (可选) 如果需要写权限,也勾选 `Mail.ReadWrite`
4. 点击底部的 **添加权限** 按钮

### 步骤5: 授予管理员同意

⚠️ **这是最关键的一步!**

1. 在 "API权限" 页面,找到刚添加的权限
2. 点击 **"为 [组织名称] 授予管理员同意"**
3. 在弹出对话框中点击 **"是"**
4. 等待状态列显示: **"✓ 已授予管理员同意"**

---

## 🎯 配置完成后的验证

### 正确的配置应该显示:

```
╔═══════════════════════════════════════════════════════════╗
║                    已配置的权限                            ║
╠═══════════════════╦═══════════╦═══════════════════════════╣
║ 权限名称          ║ 类型      ║ 状态                      ║
╠═══════════════════╬═══════════╬═══════════════════════════╣
║ Mail.Read         ║ 应用程序  ║ ✓ 已授予管理员同意         ║
╚═══════════════════╩═══════════╩═══════════════════════════╝
```

如果添加了可选的写权限:

```
╔═══════════════════════════════════════════════════════════╗
║                    已配置的权限                            ║
╠═══════════════════╦═══════════╦═══════════════════════════╣
║ 权限名称          ║ 类型      ║ 状态                      ║
╠═══════════════════╬═══════════╬═══════════════════════════╣
║ Mail.Read         ║ 应用程序  ║ ✓ 已授予管理员同意         ║
║ Mail.ReadWrite    ║ 应用程序  ║ ✓ 已授予管理员同意         ║
╚═══════════════════╩═══════════╩═══════════════════════════╝
```

---

## ⚠️ 常见错误

### 错误1: 选择了委托权限

**症状**:
```
权限类型显示: "委托" 而不是 "应用程序"
```

**解决方案**:
1. 删除该权限
2. 重新添加时选择 **"应用程序权限"**

---

### 错误2: 未授予管理员同意

**症状**:
```
状态列显示: "未授予同意" 或空白
```

**解决方案**:
1. 点击 "为 [组织] 授予管理员同意"
2. 如果按钮是灰色的,说明你没有管理员权限
3. 联系IT管理员帮助授予

---

### 错误3: 找不到Mail.Read权限

**症状**:
```
搜索框输入后找不到权限
```

**解决方案**:
1. 确认选择的是 **"应用程序权限"** 而不是 "委托权限"
2. 尝试展开 "Mail" 分组
3. 向下滚动查看完整列表

---

## 📊 权限对比表

### Mail.Read vs Mail.ReadWrite

| 操作 | Mail.Read | Mail.ReadWrite |
|------|-----------|----------------|
| 读取邮件列表 | ✅ | ✅ |
| 读取邮件内容 | ✅ | ✅ |
| 读取邮件附件 | ✅ | ✅ |
| 筛选邮件 | ✅ | ✅ |
| 标记已读/未读 | ❌ | ✅ |
| 移动邮件 | ❌ | ✅ |
| 删除邮件 | ❌ | ✅ |
| 创建草稿 | ❌ | ✅ |
| 发送邮件 | ❌ | ❌* |

*注: 发送邮件需要 `Mail.Send` 权限,但本项目使用SMTP发送,不需要此权限

---

## 🔐 安全最佳实践

### 1. 使用最小权限原则

```
✅ 推荐: 只添加 Mail.Read
❌ 避免: 添加不必要的权限如 Mail.Send
```

### 2. 定期审查权限

每3-6个月检查一次:
- 是否有不再使用的权限
- 是否有过度授权的情况

### 3. 保护密钥安全

```bash
# ✅ 正确: 使用环境变量
OUTLOOK_CLIENT_SECRET=your_secret

# ❌ 错误: 硬编码在代码中
client_secret = "abc123..."
```

### 4. 监控API使用

在Azure Portal中监控:
- API调用频率
- 是否有异常访问
- 权限使用情况

---

## 🧪 测试权限配置

### 方法1: 使用项目测试脚本

```bash
python test_outlook_read.py
```

**预期输出**:
```
[3/4] 连接到Microsoft Graph API...
✓ 连接成功!

[4/4] 获取最近5封邮件...
✓ 成功获取 5 封邮件
```

### 方法2: 使用Microsoft Graph Explorer

1. 访问: https://developer.microsoft.com/graph/graph-explorer
2. 登录你的账号
3. 尝试执行查询:
   ```
   GET https://graph.microsoft.com/v1.0/me/messages
   ```

---

## 📚 参考文档

### Microsoft官方文档

- [Mail permissions (Application)](https://learn.microsoft.com/en-us/graph/permissions-reference#mail-permissions)
- [Application permissions overview](https://learn.microsoft.com/en-us/graph/auth/auth-concepts#microsoft-graph-permissions)
- [Grant admin consent](https://learn.microsoft.com/en-us/graph/auth-v2-service)

### Graph API端点

```
# 读取邮件列表
GET https://graph.microsoft.com/v1.0/users/{user-id}/messages

# 读取特定邮件
GET https://graph.microsoft.com/v1.0/users/{user-id}/messages/{message-id}

# 筛选邮件
GET https://graph.microsoft.com/v1.0/users/{user-id}/messages?$filter=subject eq '每日总结'
```

---

## ✅ 配置检查清单

完成权限配置后,使用此清单确认:

- [ ] 已选择 **"应用程序权限"** (不是委托权限)
- [ ] 已添加 **`Mail.Read`** 权限
- [ ] 权限类型显示为 **"应用程序"**
- [ ] 状态显示为 **"✓ 已授予管理员同意"**
- [ ] 已记录 Client ID、Tenant ID、Client Secret
- [ ] 客户端密钥未过期
- [ ] 测试脚本运行成功

---

## 🎉 总结

### 本项目需要的权限(最简配置):

```
权限名称: Mail.Read
描述: Read mail in all mailboxes
类型: 应用程序权限
状态: 已授予管理员同意
```

这个权限就足够完成所有邮件读取任务了!

### 关键要点:

1. ✅ 权限名称是 **`Mail.Read`** (不是 `Mail.Read.All`)
2. ✅ 必须选择 **"应用程序权限"**
3. ✅ 必须 **授予管理员同意**
4. ✅ 在搜索框输入 **"mail"** 可以找到

---

祝配置顺利! 🎊

如有问题,请查看主配置文档: `OUTLOOK_配置指南.md`

