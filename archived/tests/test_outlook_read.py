#!/usr/bin/env python3
"""
测试Outlook邮件读取功能

用途: 验证Microsoft Graph API配置是否正确
"""

import os
import sys
from dotenv import load_dotenv

# 添加workflow-tools到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'workflow-tools'))

from workflow_tools.email.outlook import OutlookClient


def test_outlook_read():
    """测试Outlook邮件读取"""
    print("=" * 60)
    print("Outlook邮件读取测试")
    print("=" * 60)
    
    # 加载环境变量
    print("\n[1/4] 加载环境变量...")
    load_dotenv()
    
    # 检查必需的环境变量
    required_vars = [
        'OUTLOOK_EMAIL',
        'OUTLOOK_CLIENT_ID',
        'OUTLOOK_CLIENT_SECRET',
        'OUTLOOK_TENANT_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"✗ 缺少环境变量: {', '.join(missing_vars)}")
        print("\n请检查.env文件,确保所有变量都已配置")
        return False
    
    print("✓ 环境变量加载完成")
    
    # 创建客户端
    print("\n[2/4] 创建Outlook客户端...")
    try:
        client = OutlookClient()
        print("✓ 客户端创建成功")
    except Exception as e:
        print(f"✗ 客户端创建失败: {str(e)}")
        return False
    
    # 连接到Outlook
    print("\n[3/4] 连接到Microsoft Graph API...")
    try:
        client.connect()
        print("✓ 连接成功!")
        print(f"  - 邮箱地址: {client.email_address}")
        print(f"  - 租户ID: {client.tenant_id}")
    except Exception as e:
        print(f"✗ 连接失败: {str(e)}")
        print("\n可能的原因:")
        print("  1. Client ID、Secret或Tenant ID不正确")
        print("  2. Azure应用权限未授予管理员同意")
        print("  3. 客户端密钥已过期")
        print("\n请参考OUTLOOK_配置指南.md重新检查配置")
        return False
    
    # 获取邮件
    print("\n[4/4] 获取最近5封邮件...")
    try:
        result = client.fetch_emails(limit=5)
        
        if result.success:
            print(f"✓ 成功获取 {len(result.messages)} 封邮件\n")
            
            if result.messages:
                print("邮件列表:")
                print("-" * 60)
                for i, msg in enumerate(result.messages, 1):
                    print(f"{i}. 主题: {msg.subject}")
                    print(f"   发件人: {msg.sender}")
                    print(f"   时间: {msg.received_time}")
                    print(f"   正文长度: {len(msg.body)} 字符")
                    print()
            else:
                print("邮箱中没有邮件")
        else:
            print(f"✗ 获取邮件失败: {result.error}")
            return False
            
    except Exception as e:
        print(f"✗ 获取邮件失败: {str(e)}")
        return False
    finally:
        # 断开连接
        client.disconnect()
    
    # 测试完成
    print("=" * 60)
    print("✓ 所有测试通过! Microsoft Graph API配置正确")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_outlook_read()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试过程中发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

