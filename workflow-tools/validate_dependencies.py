#!/usr/bin/env python3
"""
依赖验证工具
可以独立运行以检查workflow-tools的依赖安装情况
"""

import sys
import importlib.util
from typing import Dict, List, Tuple


class DependencyValidator:
    """依赖验证器"""
    
    # 定义所有可选依赖及其功能描述
    DEPENDENCY_MAP: Dict[str, List[Tuple[str, str]]] = {
        'core': [
            ('typing_extensions', '类型扩展'),
            ('dotenv', '环境变量加载')
        ],
        'email': [
            ('msal', 'Microsoft身份认证'),
            ('requests', 'HTTP请求')
        ],
        'ai': [
            ('google.generativeai', 'Gemini AI')
        ],
        'notes': [
            ('notion_client', 'Notion API')
        ],
        'storage': [
            ('boto3', 'AWS S3'),
            ('botocore', 'AWS核心库')
        ],
        'scheduler': [
            ('apscheduler', '任务调度'),
            ('pytz', '时区支持')
        ],
        'utils': [
            ('ratelimit', '速率限制')
        ],
        'dev': [
            ('pytest', '单元测试'),
            ('pytest_mock', '测试模拟')
        ]
    }
    
    def __init__(self):
        self.missing_deps: Dict[str, List[Tuple[str, str]]] = {}
        self.installed_deps: Dict[str, List[Tuple[str, str]]] = {}
    
    def check_module(self, module_name: str) -> bool:
        """
        检查模块是否已安装
        
        Args:
            module_name: 模块名称
            
        Returns:
            是否已安装
        """
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    
    def validate_all(self) -> bool:
        """
        验证所有依赖
        
        Returns:
            是否所有核心依赖都已安装
        """
        all_core_installed = True
        
        for feature, modules in self.DEPENDENCY_MAP.items():
            for module_name, description in modules:
                if self.check_module(module_name):
                    if feature not in self.installed_deps:
                        self.installed_deps[feature] = []
                    self.installed_deps[feature].append((module_name, description))
                else:
                    if feature not in self.missing_deps:
                        self.missing_deps[feature] = []
                    self.missing_deps[feature].append((module_name, description))
                    
                    # 核心依赖缺失是严重问题
                    if feature == 'core':
                        all_core_installed = False
        
        return all_core_installed
    
    def print_report(self, verbose: bool = False) -> None:
        """
        打印依赖报告
        
        Args:
            verbose: 是否显示详细信息（包括已安装的依赖）
        """
        print("\n" + "=" * 60)
        print("📦 Workflow-Tools 依赖检查报告")
        print("=" * 60)
        
        # 打印已安装的依赖
        if verbose and self.installed_deps:
            print("\n✅ 已安装的依赖:")
            for feature, modules in sorted(self.installed_deps.items()):
                print(f"\n  [{feature}]")
                for module_name, description in modules:
                    print(f"    ✓ {module_name} - {description}")
        
        # 打印缺失的依赖
        if self.missing_deps:
            print("\n⚠️  缺失的依赖:")
            for feature, modules in sorted(self.missing_deps.items()):
                print(f"\n  [{feature}]")
                for module_name, description in modules:
                    print(f"    ✗ {module_name} - {description}")
                
                # 提供安装建议
                if feature == 'core':
                    print(f"    🔴 核心依赖! 必须安装")
                    print(f"    💡 运行: pip install workflow-tools")
                else:
                    print(f"    💡 安装建议: pip install workflow-tools[{feature}]")
        else:
            print("\n✅ 所有核心依赖已正确安装!")
        
        # 安装完整包的建议
        if self.missing_deps and 'core' not in self.missing_deps:
            print("\n💡 一次性安装所有依赖:")
            print("   pip install workflow-tools[all]")
        
        print("\n" + "=" * 60 + "\n")
    
    def get_exit_code(self) -> int:
        """
        获取退出码
        
        Returns:
            0: 所有核心依赖已安装
            1: 有核心依赖缺失
            2: 只有可选依赖缺失
        """
        if 'core' in self.missing_deps:
            return 1
        elif self.missing_deps:
            return 2
        else:
            return 0


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='验证 workflow-tools 的依赖安装情况'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息（包括已安装的依赖）'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='严格模式：任何依赖缺失都返回错误码'
    )
    
    args = parser.parse_args()
    
    # 创建验证器并执行检查
    validator = DependencyValidator()
    core_ok = validator.validate_all()
    
    # 打印报告
    validator.print_report(verbose=args.verbose)
    
    # 确定退出码
    if args.strict:
        # 严格模式：任何依赖缺失都是错误
        exit_code = 1 if validator.missing_deps else 0
    else:
        # 正常模式：只有核心依赖缺失才是错误
        exit_code = validator.get_exit_code()
    
    if exit_code == 1:
        print("❌ 核心依赖缺失，请先安装必需的包", file=sys.stderr)
    elif exit_code == 2:
        print("⚠️  部分可选功能不可用，请根据需要安装相应的包")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

