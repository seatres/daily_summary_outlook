#!/usr/bin/env python3
"""
诊断Azure认证问题

帮助识别401错误的原因
"""

import os
import sys
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

print("=" * 70)
print("Azure认证诊断工具")
print("=" * 70)

# 检查环境变量
print("\n[1/5] 检查环境变量...")
required_vars = {
    'OUTLOOK_EMAIL': os.getenv('OUTLOOK_EMAIL'),
    'OUTLOOK_CLIENT_ID': os.getenv('OUTLOOK_CLIENT_ID'),
    'OUTLOOK_CLIENT_SECRET': os.getenv('OUTLOOK_CLIENT_SECRET'),
    'OUTLOOK_TENANT_ID': os.getenv('OUTLOOK_TENANT_ID'),
}

all_present = True
for var_name, var_value in required_vars.items():
    if var_value:
        # 只显示部分值,保护隐私
        if 'SECRET' in var_name:
            display_value = f"{var_value[:8]}...{var_value[-4:]}" if len(var_value) > 12 else "***"
        else:
            display_value = var_value
        print(f"  ✓ {var_name}: {display_value}")
    else:
        print(f"  ✗ {var_name}: 未设置")
        all_present = False

if not all_present:
    print("\n❌ 缺少必要的环境变量")
    sys.exit(1)

# 检查Client Secret格式
print("\n[2/5] 检查Client Secret格式...")
client_secret = required_vars['OUTLOOK_CLIENT_SECRET']
if ' ' in client_secret or '\n' in client_secret or '\r' in client_secret:
    print("  ⚠️  警告: Client Secret包含空格或换行符")
    print("  → 请检查.env文件,确保没有多余的空格")
else:
    print(f"  ✓ Client Secret格式正常 (长度: {len(client_secret)})")

# 测试获取访问令牌
print("\n[3/5] 测试获取访问令牌...")
try:
    from msal import ConfidentialClientApplication
    
    tenant_id = required_vars['OUTLOOK_TENANT_ID']
    client_id = required_vars['OUTLOOK_CLIENT_ID']
    client_secret = required_vars['OUTLOOK_CLIENT_SECRET']
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )
    
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    
    if "access_token" in result:
        token = result["access_token"]
        print(f"  ✓ 成功获取访问令牌")
        print(f"  - 令牌长度: {len(token)}")
        print(f"  - 令牌前缀: {token[:20]}...")
        
        # 检查令牌中的权限
        import jwt
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        print("\n[4/5] 检查令牌中的权限...")
        if 'roles' in decoded:
            roles = decoded['roles']
            print(f"  ✓ 令牌包含 {len(roles)} 个权限:")
            for role in roles:
                print(f"    - {role}")
            
            # 检查是否有Mail.Read权限
            if 'Mail.Read' in roles:
                print("\n  ✅ 确认包含 Mail.Read 权限")
            else:
                print("\n  ❌ 警告: 令牌中没有 Mail.Read 权限!")
                print("  → 可能原因: 权限未正确授予管理员同意")
        else:
            print("  ⚠️  令牌中没有 'roles' 字段")
            print("  → 这通常表示使用了委托权限而不是应用程序权限")
        
        # 测试API调用
        print("\n[5/5] 测试Graph API调用...")
        email = required_vars['OUTLOOK_EMAIL']
        url = f"https://graph.microsoft.com/v1.0/users/{email}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {
            "$top": 1,
            "$select": "subject"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"  - HTTP状态码: {response.status_code}")
        print(f"  - 响应大小: {len(response.text)} bytes")
        
        if response.status_code == 200:
            print("\n  ✅ API调用成功!")
            data = response.json()
            messages = data.get('value', [])
            print(f"  - 获取到 {len(messages)} 封邮件")
            
        elif response.status_code == 401:
            print("\n  ❌ 401 未授权错误")
            print(f"  - 响应内容: {response.text[:200]}")
            print("\n  可能的原因:")
            print("    1. 权限未正确授予管理员同意")
            print("    2. 使用了委托权限而不是应用程序权限")
            print("    3. Client Secret已过期")
            print("    4. 邮箱地址不属于该租户")
            
        elif response.status_code == 403:
            print("\n  ❌ 403 禁止访问")
            print(f"  - 响应内容: {response.text[:200]}")
            print("\n  可能的原因:")
            print("    1. 缺少必要的权限")
            print("    2. 权限未授予管理员同意")
            
        else:
            print(f"\n  ⚠️  其他错误 ({response.status_code})")
            print(f"  - 响应内容: {response.text[:200]}")
        
    else:
        print("  ✗ 获取访问令牌失败")
        if "error" in result:
            print(f"  - 错误: {result.get('error')}")
            print(f"  - 描述: {result.get('error_description')}")
        
except ImportError as e:
    print(f"  ✗ 缺少依赖库: {str(e)}")
    print("  → 运行: pip install msal requests pyjwt")
except Exception as e:
    print(f"  ✗ 发生错误: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)

