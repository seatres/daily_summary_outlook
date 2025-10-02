#!/usr/bin/env python3
"""
依赖检查示例
演示如何在代码中使用依赖验证器
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validate_dependencies import DependencyValidator


def example_basic_check():
    """示例: 基本依赖检查"""
    print("示例 1: 基本依赖检查")
    print("-" * 40)
    
    validator = DependencyValidator()
    core_ok = validator.validate_all()
    
    if core_ok:
        print("✅ 核心依赖检查通过")
    else:
        print("❌ 核心依赖缺失")
    
    print()


def example_feature_check():
    """示例: 检查特定功能的依赖"""
    print("示例 2: 检查特定功能")
    print("-" * 40)
    
    validator = DependencyValidator()
    validator.validate_all()
    
    # 检查邮件功能
    if 'email' not in validator.missing_deps:
        print("✅ 邮件功能可用")
    else:
        print("❌ 邮件功能不可用，缺少依赖:")
        for module, desc in validator.missing_deps['email']:
            print(f"   - {module}: {desc}")
    
    # 检查AI功能
    if 'ai' not in validator.missing_deps:
        print("✅ AI功能可用")
    else:
        print("❌ AI功能不可用，缺少依赖:")
        for module, desc in validator.missing_deps['ai']:
            print(f"   - {module}: {desc}")
    
    print()


def example_conditional_import():
    """示例: 根据依赖可用性条件导入"""
    print("示例 3: 条件导入")
    print("-" * 40)
    
    validator = DependencyValidator()
    
    # 检查msal是否可用
    if validator.check_module('msal'):
        print("✅ 可以导入 OutlookClient")
        try:
            from workflow_tools.email.outlook import OutlookClient
            print("   OutlookClient 导入成功")
        except ImportError as e:
            print(f"   导入失败: {e}")
    else:
        print("⚠️  无法导入 OutlookClient (缺少 msal)")
    
    # 检查google.generativeai是否可用
    if validator.check_module('google.generativeai'):
        print("✅ 可以导入 GeminiClient")
        try:
            from workflow_tools.ai_models.gemini import GeminiClient
            print("   GeminiClient 导入成功")
        except ImportError as e:
            print(f"   导入失败: {e}")
    else:
        print("⚠️  无法导入 GeminiClient (缺少 google-generativeai)")
    
    print()


def example_installation_guide():
    """示例: 生成安装指南"""
    print("示例 4: 生成安装指南")
    print("-" * 40)
    
    validator = DependencyValidator()
    validator.validate_all()
    
    if not validator.missing_deps:
        print("✅ 所有依赖都已安装!")
        return
    
    print("需要安装以下依赖:\n")
    
    features_to_install = []
    for feature in validator.missing_deps.keys():
        if feature != 'core':
            features_to_install.append(feature)
    
    if features_to_install:
        install_cmd = f"pip install workflow-tools[{','.join(features_to_install)}]"
        print(f"推荐命令: {install_cmd}")
    
    if 'core' in validator.missing_deps:
        print("\n⚠️  核心依赖缺失，请先安装:")
        print("   pip install workflow-tools")
    
    print()


def example_ci_check():
    """示例: CI/CD 环境检查"""
    print("示例 5: CI/CD 检查")
    print("-" * 40)
    
    validator = DependencyValidator()
    core_ok = validator.validate_all()
    
    # 模拟CI环境的检查
    if not core_ok:
        print("❌ CI检查失败: 核心依赖缺失")
        sys.exit(1)
    
    # 检查是否有任何缺失的依赖
    if validator.missing_deps:
        print("⚠️  警告: 部分可选依赖缺失")
        for feature, modules in validator.missing_deps.items():
            print(f"   [{feature}]: {len(modules)}个模块缺失")
        
        # 根据需要决定是否继续
        # 在CI中，可能希望所有依赖都安装
        print("\n💡 提示: 在CI环境中建议安装所有依赖")
        print("   pip install workflow-tools[all]")
    else:
        print("✅ CI检查通过: 所有依赖都已安装")
    
    print()


def main():
    """主函数"""
    print("=" * 60)
    print("依赖验证示例")
    print("=" * 60)
    print()
    
    # 运行所有示例
    example_basic_check()
    example_feature_check()
    example_conditional_import()
    example_installation_guide()
    example_ci_check()
    
    print("=" * 60)
    print("所有示例执行完成")
    print("=" * 60)


if __name__ == '__main__':
    main()

