"""
测试依赖验证功能
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
import importlib.util

# 添加父目录到路径以便导入
sys.path.insert(0, '..')

from validate_dependencies import DependencyValidator


class TestDependencyValidator(unittest.TestCase):
    """测试依赖验证器"""
    
    def setUp(self):
        """测试前准备"""
        self.validator = DependencyValidator()
    
    def test_check_module_exists(self):
        """测试检查存在的模块"""
        # sys 是标准库，肯定存在
        self.assertTrue(self.validator.check_module('sys'))
        self.assertTrue(self.validator.check_module('os'))
    
    def test_check_module_not_exists(self):
        """测试检查不存在的模块"""
        # 假设这个模块不存在
        self.assertFalse(self.validator.check_module('nonexistent_module_xyz'))
    
    def test_validate_all_structure(self):
        """测试验证所有依赖的返回结构"""
        result = self.validator.validate_all()
        
        # 应该返回布尔值
        self.assertIsInstance(result, bool)
        
        # 应该有已安装和缺失的依赖字典
        self.assertIsInstance(self.validator.installed_deps, dict)
        self.assertIsInstance(self.validator.missing_deps, dict)
    
    def test_get_exit_code_all_installed(self):
        """测试所有依赖都安装时的退出码"""
        self.validator.missing_deps = {}
        self.assertEqual(self.validator.get_exit_code(), 0)
    
    def test_get_exit_code_core_missing(self):
        """测试核心依赖缺失时的退出码"""
        self.validator.missing_deps = {
            'core': [('typing_extensions', '类型扩展')]
        }
        self.assertEqual(self.validator.get_exit_code(), 1)
    
    def test_get_exit_code_optional_missing(self):
        """测试可选依赖缺失时的退出码"""
        self.validator.missing_deps = {
            'email': [('msal', 'Microsoft身份认证')]
        }
        self.assertEqual(self.validator.get_exit_code(), 2)
    
    def test_dependency_map_structure(self):
        """测试依赖映射的结构"""
        # 确保所有功能都有定义
        expected_features = ['core', 'email', 'ai', 'notes', 'storage', 'scheduler']
        for feature in expected_features:
            self.assertIn(feature, DependencyValidator.DEPENDENCY_MAP)
        
        # 确保每个功能都有模块列表
        for feature, modules in DependencyValidator.DEPENDENCY_MAP.items():
            self.assertIsInstance(modules, list)
            self.assertGreater(len(modules), 0)
            
            # 每个模块应该是 (模块名, 描述) 元组
            for module in modules:
                self.assertIsInstance(module, tuple)
                self.assertEqual(len(module), 2)
                self.assertIsInstance(module[0], str)
                self.assertIsInstance(module[1], str)
    
    @patch('builtins.print')
    def test_print_report_no_verbose(self, mock_print):
        """测试非详细模式的报告输出"""
        self.validator.installed_deps = {
            'core': [('typing_extensions', '类型扩展')]
        }
        self.validator.missing_deps = {
            'email': [('msal', 'Microsoft身份认证')]
        }
        
        self.validator.print_report(verbose=False)
        
        # 应该有打印调用
        self.assertTrue(mock_print.called)
        
        # 检查是否包含关键信息
        all_calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(all_calls)
        
        self.assertTrue('依赖检查报告' in output)
        self.assertTrue('缺失的依赖' in output)
    
    @patch('builtins.print')
    def test_print_report_verbose(self, mock_print):
        """测试详细模式的报告输出"""
        self.validator.installed_deps = {
            'core': [('typing_extensions', '类型扩展')]
        }
        self.validator.missing_deps = {}
        
        self.validator.print_report(verbose=True)
        
        # 详细模式应该显示已安装的依赖
        all_calls = [str(call) for call in mock_print.call_args_list]
        output = ' '.join(all_calls)
        
        self.assertTrue('已安装的依赖' in output or 'typing_extensions' in output)


class TestDependencyMapCompleteness(unittest.TestCase):
    """测试依赖映射的完整性"""
    
    def test_core_dependencies(self):
        """测试核心依赖是否完整"""
        core_deps = DependencyValidator.DEPENDENCY_MAP['core']
        module_names = [dep[0] for dep in core_deps]
        
        # 核心依赖应该包含这些
        expected = ['typing_extensions', 'dotenv']
        for module in expected:
            self.assertIn(module, module_names)
    
    def test_email_dependencies(self):
        """测试邮件功能依赖"""
        email_deps = DependencyValidator.DEPENDENCY_MAP['email']
        module_names = [dep[0] for dep in email_deps]
        
        # 邮件功能需要这些
        self.assertIn('msal', module_names)
        self.assertIn('requests', module_names)
    
    def test_ai_dependencies(self):
        """测试AI功能依赖"""
        ai_deps = DependencyValidator.DEPENDENCY_MAP['ai']
        module_names = [dep[0] for dep in ai_deps]
        
        # AI功能需要这些
        self.assertIn('google.generativeai', module_names)


if __name__ == '__main__':
    unittest.main()

