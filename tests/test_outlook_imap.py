#!/usr/bin/env python3
"""
测试Outlook IMAP邮件功能

用途: 验证IMAP配置是否正确(适用于个人Outlook账户)
"""

import os
import sys
from dotenv import load_dotenv

# 添加workflow-tools到Python路径
# 从 tests/ 目录向上一级到项目根目录，然后访问 workflow-tools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workflow-tools'))

from workflow_tools.email.outlook.outlook_imap_client import OutlookIMAPClient


def test_outlook_imap():
    """测试Outlook IMAP功能"""
    print("=" * 60)
    print("Outlook IMAP测试")
    print("=" * 60)
    
    # 加载环境变量
    print("\n[1/5] 加载环境变量...")
    load_dotenv()
    
    # 检查必需的环境变量
    email_address = os.getenv('OUTLOOK_EMAIL')
    imap_password = os.getenv('OUTLOOK_IMAP_PASSWORD')
    smtp_password = os.getenv('OUTLOOK_SMTP_PASSWORD')
    
    # 如果没有设置IMAP密码,尝试使用SMTP密码
    password = imap_password or smtp_password
    
    if not email_address:
        print("✗ 缺少环境变量: OUTLOOK_EMAIL")
        return False
    
    if not password:
        print("✗ 缺少环境变量: OUTLOOK_IMAP_PASSWORD 或 OUTLOOK_SMTP_PASSWORD")
        print("\n请在.env文件中设置:")
        print("  OUTLOOK_IMAP_PASSWORD=你的应用专用密码")
        return False
    
    print("✓ 环境变量加载完成")
    print(f"  - 邮箱地址: {email_address}")
    print(f"  - 密码长度: {len(password)} 字符")
    
    # 创建客户端
    print("\n[2/5] 创建IMAP客户端...")
    try:
        client = OutlookIMAPClient(
            email_address=email_address,
            password=password
        )
        print("✓ 客户端创建成功")
    except Exception as e:
        print(f"✗ 客户端创建失败: {str(e)}")
        return False
    
    # 连接到IMAP服务器
    print("\n[3/5] 连接到IMAP服务器...")
    try:
        client.connect()
        print("✓ 连接成功!")
        print(f"  - IMAP服务器: {client.IMAP_SERVER}")
        print(f"  - 端口: {client.IMAP_PORT}")
    except Exception as e:
        print(f"✗ 连接失败: {str(e)}")
        print("\n可能的原因:")
        print("  1. 应用专用密码不正确")
        print("  2. 账户未启用双重验证")
        print("  3. 网络连接问题")
        print("  4. 账户未启用IMAP")
        print("\n解决方案:")
        print("  1. 访问 https://account.microsoft.com/security")
        print("  2. 启用双重验证")
        print("  3. 生成新的应用专用密码")
        return False
    
    # 获取邮件
    print("\n[4/5] 获取最近5封邮件...")
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
                    if len(msg.body) > 0:
                        preview = msg.body[:100].replace('\n', ' ')
                        print(f"   预览: {preview}...")
                    print()
            else:
                print("邮箱中没有邮件")
        else:
            print(f"✗ 获取邮件失败: {result.error}")
            return False
            
    except Exception as e:
        print(f"✗ 获取邮件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 断开连接
        client.disconnect()
    
    # 测试发送邮件
    print("\n[5/5] 测试SMTP发送...")
    test_send = input("是否测试发送邮件? (y/n): ").strip().lower()
    
    if test_send == 'y':
        print("\n正在发送测试邮件...")
        from datetime import datetime
        
        try:
            success = client.send_email(
                to=[email_address],
                subject="IMAP配置测试",
                body=f"""这是一封自动发送的测试邮件。

如果你收到了这封邮件,说明你的Outlook IMAP配置成功!

测试信息:
- 发送时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 客户端类型: IMAP
- 邮箱地址: {email_address}

这封邮件由每日总结自动化工作流系统发送。
"""
            )
            
            if success:
                print(f"\n✓ 邮件发送成功!")
                print(f"\n请检查 {email_address} 的收件箱")
                print("(如果没收到,请检查垃圾邮件文件夹)")
            else:
                print("\n✗ 邮件发送失败")
                return False
        except Exception as e:
            print(f"\n✗ 发送邮件失败: {str(e)}")
            return False
    else:
        print("跳过发送测试")
    
    # 测试完成
    print("\n" + "=" * 60)
    print("✓ 所有测试通过! IMAP配置正确")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 更新.env文件:")
    print("     EMAIL_CLIENT_TYPE=imap")
    print("  2. 运行主程序:")
    print("     python main.py")
    return True


if __name__ == "__main__":
    try:
        success = test_outlook_imap()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试过程中发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

