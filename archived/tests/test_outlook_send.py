#!/usr/bin/env python3
"""
测试Outlook邮件发送功能

用途: 验证SMTP应用专用密码配置是否正确
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 添加workflow-tools到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'workflow-tools'))

from workflow_tools.email.outlook import OutlookClient


def test_outlook_send():
    """测试Outlook邮件发送"""
    print("=" * 60)
    print("Outlook邮件发送测试")
    print("=" * 60)
    
    # 加载环境变量
    print("\n[1/3] 加载环境变量...")
    load_dotenv()
    
    # 检查必需的环境变量
    required_vars = [
        'OUTLOOK_EMAIL',
        'OUTLOOK_SMTP_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"✗ 缺少环境变量: {', '.join(missing_vars)}")
        print("\n请检查.env文件,确保所有变量都已配置")
        return False
    
    print("✓ 环境变量加载完成")
    
    # 创建客户端
    print("\n[2/3] 创建Outlook客户端...")
    try:
        client = OutlookClient()
        print("✓ 客户端创建成功")
        print(f"  - 邮箱地址: {client.email_address}")
    except Exception as e:
        print(f"✗ 客户端创建失败: {str(e)}")
        return False
    
    # 发送测试邮件
    print("\n[3/3] 发送测试邮件...")
    recipient = client.email_address  # 发送给自己
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    subject = "Outlook SMTP配置测试"
    body = f"""这是一封自动发送的测试邮件。

如果你收到了这封邮件，说明你的Outlook SMTP配置成功！

测试信息:
- 发送时间: {current_time}
- 发件人: {client.email_address}
- 收件人: {recipient}

配置的内容:
✓ SMTP服务器: smtp-mail.outlook.com
✓ 端口: 587
✓ 安全连接: STARTTLS
✓ 认证方式: 应用专用密码

这封邮件由每日总结自动化工作流系统发送。
"""
    
    try:
        print(f"  - 收件人: {recipient}")
        print(f"  - 主题: {subject}")
        print("\n正在发送...")
        
        success = client.send_email(
            to=[recipient],
            subject=subject,
            body=body
        )
        
        if success:
            print(f"\n✓ 邮件发送成功!")
            print(f"\n请检查 {recipient} 的收件箱")
            print("(如果没收到,请检查垃圾邮件文件夹)")
        else:
            print("\n✗ 邮件发送失败")
            return False
            
    except Exception as e:
        print(f"\n✗ 发送邮件失败: {str(e)}")
        print("\n可能的原因:")
        print("  1. SMTP应用专用密码不正确")
        print("  2. 邮箱地址不正确")
        print("  3. 网络连接问题")
        print("  4. SMTP服务器被防火墙阻止")
        print("\n请参考OUTLOOK_配置指南.md重新检查配置")
        return False
    
    # 测试完成
    print("\n" + "=" * 60)
    print("✓ 测试通过! SMTP配置正确")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_outlook_send()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试过程中发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

