# 归档目录

本目录存放项目中已过时或被替代的文件。

## 📦 目录结构

### `docs/` - 归档文档
存放已过时或被新文档替代的配置说明：
- `如何使用IMAP.txt` - 早期 IMAP 使用说明
- `权限配置速查表.txt` - 早期权限配置速查
- `配置完成总结.txt` - 早期配置总结
- `配置流程图.md` - 早期配置流程
- `OUTLOOK_配置指南.md` - 早期 Outlook 配置（已被 IMAP 配置替代）
- `Azure权限配置详解.md` - Azure AD 权限配置（主要用于 Graph API）

### `tests/` - 归档测试
存放早期的测试脚本，已被新的测试文件替代：
- `check_mailbox.py` - 邮箱检查脚本
- `diagnose_auth.py` - 认证诊断脚本
- `test_outlook_read.py` - Outlook 读取测试
- `test_outlook_send.py` - Outlook 发送测试

### 其他归档文件
- `CLEANUP_COMPLETED.md` - 早期清理完成记录
- `DEPENDENCY_BOUNDARY_CHANGES.md` - 依赖边界变更记录

## ⚠️ 注意事项

- 这些文件仅供参考，可能包含过时信息
- 如需查看当前文档，请访问 `../docs/`
- 如需查看当前测试，请访问 `../tests/`
- 这些文件可以安全删除，但建议保留以供参考

## 🗑️ 清理建议

如果确定不再需要这些文件，可以安全删除整个 `archived/` 目录：
```bash
rm -rf archived/
```

