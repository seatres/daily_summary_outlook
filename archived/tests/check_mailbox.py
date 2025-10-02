#!/usr/bin/env python3
"""
检查邮箱账户类型

帮助确定邮箱是个人账户还是组织账户
"""

import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()

email = os.getenv('OUTLOOK_EMAIL')
tenant_id = os.getenv('OUTLOOK_TENANT_ID')

print("=" * 70)
print("邮箱账户类型检查")
print("=" * 70)

print(f"\n配置的邮箱: {email}")
print(f"应用租户ID: {tenant_id}")

# 分析邮箱域名
if '@' in email:
    domain = email.split('@')[1]
    print(f"\n邮箱域名: {domain}")
    
    if domain in ['outlook.com', 'hotmail.com', 'live.com', 'msn.com']:
        print("\n⚠️  这是一个 **个人Microsoft账户**")
        print("\n问题:")
        print("  - 应用程序权限(Application Permissions)不支持个人账户")
        print("  - Graph API的应用权限只能访问组织租户内的邮箱")
        print("\n解决方案:")
        print("  1. 使用组织邮箱(如: user@company.com)")
        print("  2. 注册Microsoft 365开发者计划获取免费租户:")
        print("     https://developer.microsoft.com/microsoft-365/dev-program")
        print("  3. 改用IMAP协议读取邮件(需要修改代码)")
    else:
        print(f"\n✓ 这可能是一个 **组织账户** (域名: {domain})")
        print("\n如果仍然遇到401错误,请检查:")
        print("  1. 该邮箱是否存在于当前租户")
        print("  2. 权限是否已正确授予管理员同意")

print("\n" + "=" * 70)

