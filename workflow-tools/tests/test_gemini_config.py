#!/usr/bin/env python3
"""
Gemini AI 配置测试脚本

使用示例:
    python test_gemini_config.py
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """运行 Gemini 配置验证测试"""
    print("🧪 开始验证 Gemini AI 配置...")

    try:
        from workflow_tools.ai_models.gemini.gemini_client import GeminiClient
        # 运行验证
        result = GeminiClient.validate_gemini_config()

        # 打印验证报告
        GeminiClient.print_validation_report(result)

        # 返回适当的退出代码
        sys.exit(0 if result.is_valid else 1)

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所需依赖: pip install google-generativeai")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
