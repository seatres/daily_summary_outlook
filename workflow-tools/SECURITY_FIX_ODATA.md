# OData 过滤器安全修复

## 问题描述

在 `outlook_client.py` 中，邮件过滤条件（主题和发件人）直接用于构建 OData 查询，没有进行输入验证和特殊字符转义。这可能导致：

1. **OData 查询语法错误** - 特殊字符（如单引号 `'`）会破坏查询语法
2. **潜在的注入攻击** - 恶意构造的输入可能操纵查询逻辑
3. **应用程序崩溃** - 控制字符可能导致解析错误

### 问题示例

如果配置文件中的发件人设置为：`user'test@example.com`

生成的 OData 过滤器将是：
```
from/emailAddress/address eq 'user'test@example.com'
```

这会导致语法错误，因为单引号没有被正确转义。

## 修复方案

### 1. 添加 OData 字符串转义函数

```python
@staticmethod
def _escape_odata_string(value: str) -> str:
    """
    转义OData查询字符串中的特殊字符
    
    Args:
        value: 要转义的字符串
        
    Returns:
        转义后的字符串
    """
    if not value:
        return value
        
    # OData规范要求单引号需要转义为两个单引号
    # 参考: https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html
    escaped = value.replace("'", "''")
    
    # 移除可能导致问题的控制字符
    escaped = re.sub(r'[\x00-\x1F\x7F]', '', escaped)
    
    return escaped
```

**功能说明：**
- 按照 OData 规范，单引号 `'` 转义为两个单引号 `''`
- 移除所有控制字符（ASCII 0x00-0x1F 和 0x7F）

### 2. 添加输入验证函数

```python
@staticmethod
def _validate_filter_input(value: str, field_name: str) -> None:
    """
    验证过滤器输入的合法性
    
    Args:
        value: 要验证的值
        field_name: 字段名称（用于错误消息）
        
    Raises:
        ValueError: 如果输入不合法
    """
    if not value:
        return
        
    # 检查长度限制（防止过长的输入）
    max_length = 1000
    if len(value) > max_length:
        raise ValueError(f"{field_name}长度不能超过{max_length}个字符")
    
    # 检查是否包含潜在危险的字符模式
    dangerous_patterns = [
        r'[\x00-\x08\x0B\x0C\x0E-\x1F]',  # 控制字符（除了\t \n \r）
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, value):
            raise ValueError(f"{field_name}包含不允许的控制字符")
```

**功能说明：**
- 长度限制：最大 1000 个字符
- 检测危险的控制字符（但允许常见的空白字符：制表符、换行符、回车符）

### 3. 在 fetch_emails 方法中应用验证和转义

```python
if subject:
    # 验证并转义主题
    self._validate_filter_input(subject, "邮件主题")
    escaped_subject = self._escape_odata_string(subject)
    filters.append(f"subject eq '{escaped_subject}'")
    self.logger.debug("添加主题过滤器: %s", escaped_subject)

if sender:
    # 验证并转义发件人
    self._validate_filter_input(sender, "发件人邮箱")
    escaped_sender = self._escape_odata_string(sender)
    filters.append(f"from/emailAddress/address eq '{escaped_sender}'")
    self.logger.debug("添加发件人过滤器: %s", escaped_sender)
```

### 4. 添加 ValueError 异常处理

```python
except ValueError as e:
    # 捕获输入验证错误
    error_msg = f"输入验证失败: {str(e)}"
    self.logger.error(error_msg)
    return EmailResult(success=False, error=error_msg)
```

## 测试覆盖

创建了完整的单元测试 `test_outlook_security.py`，包含：

### 1. OData 转义测试
- ✅ 单引号转义
- ✅ 多个单引号转义
- ✅ 控制字符移除
- ✅ 正常字符串不受影响
- ✅ 空字符串和 None 值处理

### 2. 输入验证测试
- ✅ 有效输入通过验证
- ✅ 空输入不报错
- ✅ 超长输入被拒绝
- ✅ 危险控制字符被拒绝
- ✅ 允许的空白字符通过验证

### 3. 安全场景测试
- ✅ SQL/OData 注入尝试被正确转义
- ✅ 邮箱特殊字符（+, ., _, -）不受影响
- ✅ 中文字符正常处理

所有 14 个测试均通过 ✅

## 安全改进总结

### 防护措施
1. **输入验证** - 检查长度和危险字符
2. **特殊字符转义** - 按照 OData 规范转义单引号
3. **控制字符过滤** - 移除可能导致问题的控制字符
4. **错误处理** - 优雅处理验证失败情况

### 兼容性
- ✅ 保持与现有功能的兼容性
- ✅ 不影响正常的邮箱地址和主题
- ✅ 支持中文和其他 Unicode 字符
- ✅ 遵循 OData v4.01 规范

### 性能影响
- 最小化 - 只有简单的字符串操作
- 仅在过滤器非空时执行验证和转义

## 参考资料

- [OData Version 4.01 URL Conventions](https://docs.oasis-open.org/odata/odata/v4.01/odata-v4.01-part2-url-conventions.html)
- [Microsoft Graph API Filter Query Parameters](https://docs.microsoft.com/en-us/graph/query-parameters#filter-parameter)

## 修复日期

2025年10月2日

