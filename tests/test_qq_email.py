"""
QQ邮箱功能测试脚本
测试 QQ 邮箱的连接、读取和发送功能
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# 添加workflow-tools到Python路径
sys.path.insert(0, str(Path(__file__).parent / "workflow-tools"))

from workflow_tools.email import QQIMAPClient
from workflow_tools.exceptions.email_exceptions import (
    EmailAuthError,
    EmailConnectionError,
    SMTPError
)


def print_section(title: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_qq_email():
    """测试 QQ 邮箱功能"""
    
    # 加载环境变量
    load_dotenv()
    
    print_section("QQ 邮箱配置测试")
    
    # 读取配置
    email_client_type = os.getenv("EMAIL_CLIENT_TYPE", "")
    email_address = os.getenv("EMAIL_ADDRESS", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")
    email_filter_sender = os.getenv("EMAIL_FILTER_SENDER", "")
    summary_recipient = os.getenv("SUMMARY_RECIPIENT", "")
    
    print(f"\n📋 当前配置：")
    print(f"   邮件客户端类型: {email_client_type}")
    print(f"   邮箱地址: {email_address if email_address else '❌ 未配置'}")
    print(f"   授权码: {'✓ 已配置' if email_password else '❌ 未配置'}")
    print(f"   筛选发件人: {email_filter_sender if email_filter_sender else '❌ 未配置'}")
    print(f"   总结收件人: {summary_recipient if summary_recipient else '❌ 未配置'}")
    
    # 检查配置
    if email_client_type != "qq":
        print("\n⚠️  警告：EMAIL_CLIENT_TYPE 不是 'qq'")
        print("   当前值:", email_client_type)
        print("   请在 .env 文件中设置: EMAIL_CLIENT_TYPE=qq")
        response = input("\n是否继续测试 QQ 邮箱功能？(y/n): ")
        if response.lower() != 'y':
            return False
    
    if not email_address:
        print("\n❌ 错误：未配置 EMAIL_ADDRESS")
        print("   请在 .env 文件中设置您的 QQ 邮箱地址")
        print("   示例: EMAIL_ADDRESS=12345678@qq.com")
        return False
    
    if not email_password:
        print("\n❌ 错误：未配置 EMAIL_PASSWORD")
        print("   请在 .env 文件中设置 QQ 邮箱授权码")
        print("   获取方法：")
        print("   1. 登录 https://mail.qq.com")
        print("   2. 设置 -> 账户 -> 开启 IMAP/SMTP 服务")
        print("   3. 生成授权码")
        return False
    
    # 开始测试
    print_section("步骤 1/3: 测试连接")
    
    try:
        # 创建客户端
        print("\n正在创建 QQ 邮箱客户端...")
        client = QQIMAPClient(
            email_address=email_address,
            password=email_password
        )
        print("✓ 客户端创建成功")
        
        # 测试连接
        print("\n正在连接到 QQ 邮箱 IMAP 服务器...")
        client.connect()
        print("✓ IMAP 连接成功！")
        print(f"  服务器: imap.qq.com:993")
        
    except EmailAuthError as e:
        print(f"\n❌ 认证失败: {e}")
        print("\n可能的原因：")
        print("1. 授权码错误（不是 QQ 密码！）")
        print("2. 未开启 IMAP/SMTP 服务")
        print("3. 授权码已过期或被撤销")
        print("\n请检查：")
        print("- 确认使用的是授权码，不是 QQ 密码")
        print("- 在 QQ 邮箱设置中确认 IMAP/SMTP 服务已开启")
        return False
        
    except EmailConnectionError as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n可能的原因：")
        print("1. 网络连接问题")
        print("2. 防火墙阻止了 993 端口")
        print("3. QQ 邮箱服务器暂时不可用")
        return False
        
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        return False
    
    # 测试读取邮件
    print_section("步骤 2/3: 测试读取邮件")
    
    try:
        print("\n正在读取最近 24 小时的邮件...")
        since_date = datetime.now(timezone.utc) - timedelta(hours=24)
        
        result = client.fetch_emails(
            subject=None,  # 不筛选主题，读取所有邮件
            sender=None,   # 不筛选发件人
            since_date=since_date,
            limit=5  # 只读取最新 5 封
        )
        
        if result.success:
            email_count = len(result.messages)
            print(f"✓ 成功读取 {email_count} 封邮件")
            
            if email_count > 0:
                print("\n📧 最新的邮件：")
                for i, email in enumerate(result.messages[:3], 1):
                    print(f"\n   {i}. 主题: {email.subject}")
                    print(f"      发件人: {email.sender}")
                    print(f"      时间: {email.received_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"      正文预览: {email.body[:50]}...")
                
                if email_count > 3:
                    print(f"\n   ... 还有 {email_count - 3} 封邮件")
            else:
                print("\n💡 提示：最近 24 小时内没有邮件")
                print("   这是正常的，说明连接和读取功能正常")
        else:
            print(f"❌ 读取邮件失败: {result.error}")
            return False
            
    except Exception as e:
        print(f"\n❌ 读取邮件时发生错误: {e}")
        return False
    
    # 测试发送邮件
    print_section("步骤 3/3: 测试发送邮件")
    
    # 确认是否发送测试邮件
    print("\n是否要发送一封测试邮件？")
    if summary_recipient:
        print(f"测试邮件将发送到: {summary_recipient}")
    else:
        print("⚠️  未配置 SUMMARY_RECIPIENT，将发送到您自己的邮箱")
        summary_recipient = email_address
    
    response = input("\n继续发送测试邮件？(y/n): ")
    
    if response.lower() == 'y':
        try:
            print("\n正在发送测试邮件...")
            
            test_subject = f"QQ邮箱测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            test_body = f"""这是一封来自每日总结工作流的测试邮件。

测试时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
发件人: {email_address}
客户端类型: QQ邮箱 (QQIMAPClient)

如果您收到这封邮件，说明：
✓ QQ 邮箱配置正确
✓ SMTP 发送功能正常
✓ 可以正常使用每日总结工作流

---
此邮件由自动化程序发送，请勿回复。
"""
            
            success = client.send_email(
                to=[summary_recipient],
                subject=test_subject,
                body=test_body
            )
            
            if success:
                print(f"✓ 测试邮件发送成功！")
                print(f"  收件人: {summary_recipient}")
                print(f"  主题: {test_subject}")
                print("\n请检查收件箱确认是否收到邮件")
            else:
                print("❌ 发送失败（未知原因）")
                return False
                
        except EmailAuthError as e:
            print(f"\n❌ SMTP 认证失败: {e}")
            print("\n请确认：")
            print("- 授权码正确")
            print("- SMTP 服务已开启")
            return False
            
        except SMTPError as e:
            print(f"\n❌ SMTP 发送错误: {e}")
            return False
            
        except Exception as e:
            print(f"\n❌ 发送邮件时发生错误: {e}")
            return False
    else:
        print("\n⏭️  跳过发送测试")
    
    # 断开连接
    try:
        client.disconnect()
        print("\n✓ 已断开连接")
    except Exception:
        pass
    
    # 测试完成
    print_section("测试完成")
    print("\n🎉 所有测试通过！")
    print("\nQQ 邮箱配置正确，可以正常使用。")
    print("\n下一步：")
    print("1. 运行 python main.py 启动主程序")
    print("2. 程序将每晚 22:00 自动执行")
    print("3. 查看日志: logs/workflow_*.log")
    
    return True


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           QQ 邮箱功能测试脚本                                ║
║                                                            ║
║  本脚本将测试：                                              ║
║  1. QQ 邮箱连接                                             ║
║  2. 读取邮件功能                                            ║
║  3. 发送邮件功能                                            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        success = test_qq_email()
        
        if success:
            print("\n" + "=" * 60)
            print("  ✅ 测试结果: 通过")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("  ❌ 测试结果: 失败")
            print("=" * 60)
            print("\n请根据上述错误信息修复配置后重试")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

