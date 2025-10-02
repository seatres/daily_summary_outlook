#!/usr/bin/env python3
"""
Gemini AI 配置验证演示脚本

此脚本演示如何在您的应用程序中集成 Gemini 配置验证功能。
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_tools.ai_models.gemini.gemini_client import GeminiClient


def main():
    """演示 Gemini 配置验证功能"""
    print("🚀 Gemini AI 配置验证演示")
    print("=" * 50)

    # 方式1: 直接调用验证并获取结果
    print("\n📊 获取验证结果:")
    result = GeminiClient.validate_gemini_config()

    print(f"配置是否正确: {'✅ 是' if result.is_valid else '❌ 否'}")
    print(f"API密钥存在: {'✅' if result.api_key_exists else '❌'}")
    print(f"API密钥格式正确: {'✅' if result.api_key_format_valid else '❌'}")
    print(f"可以初始化客户端: {'✅' if result.can_initialize else '❌'}")
    print(f"可以连接API: {'✅' if result.can_connect else '❌'}")
    print(f"模型可用: {'✅' if result.model_available else '❌'}")

    if result.errors:
        print("\n❌ 错误:")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print("\n⚠️  警告:")
        for warning in result.warnings:
            print(f"  - {warning}")

    # 方式2: 使用内置的报告打印功能
    print("\n" + "=" * 50)
    print("📋 完整验证报告:")
    GeminiClient.print_validation_report(result)

    # 方式3: 在您的应用中根据验证结果进行处理
    print("\n" + "=" * 50)
    print("🔧 应用程序集成示例:")

    if result.is_valid:
        print("✅ 配置正确，可以正常使用 Gemini AI 功能")

        # 这里可以初始化 Gemini 客户端并开始使用
        try:
            client = GeminiClient()
            print("✅ Gemini 客户端初始化成功")

            # 发送测试消息
            test_result = client.generate_content("Hello! This is a test.")
            if test_result.success:
                print(f"✅ 测试消息发送成功: {test_result.content[:100]}...")
            else:
                print(f"❌ 测试消息发送失败: {test_result.error}")

        except Exception as e:
            print(f"❌ Gemini 客户端使用失败: {e}")

    else:
        print("❌ 配置有问题，请根据上述报告修复配置")

        # 处理错误情况
        if not result.api_key_exists:
            print("💡 请在 .env 文件中设置 GEMINI_API_KEY")
        if not result.api_key_format_valid:
            print("💡 请检查 GEMINI_API_KEY 的格式")
        if not result.can_connect:
            print("💡 请检查网络连接和 API 密钥权限")

        return False  # 表示配置验证失败

    return result.is_valid


if __name__ == "__main__":
    success = main()
    print(f"\n🎯 验证结果: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1)
