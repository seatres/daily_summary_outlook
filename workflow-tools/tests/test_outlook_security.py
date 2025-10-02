"""
测试Outlook客户端的安全功能
主要测试输入验证和OData字符串转义
"""
# pylint: disable=protected-access

import pytest
from workflow_tools.email.outlook.outlook_client import OutlookClient


class TestODataSecurity:
    """测试OData过滤器的安全性"""

    def test_escape_single_quote(self):
        """测试单引号转义"""
        # 单引号应该被转义为两个单引号
        result = OutlookClient._escape_odata_string("user'test")
        assert result == "user''test"

    def test_escape_multiple_quotes(self):
        """测试多个单引号的转义"""
        result = OutlookClient._escape_odata_string("user''test'")
        assert result == "user''''test''"

    def test_remove_control_characters(self):
        """测试移除控制字符"""
        # 控制字符应该被移除
        result = OutlookClient._escape_odata_string("user\x00test\x1F")
        assert result == "usertest"

    def test_normal_string(self):
        """测试正常字符串不受影响"""
        result = OutlookClient._escape_odata_string("user@example.com")
        assert result == "user@example.com"

    def test_empty_string(self):
        """测试空字符串"""
        result = OutlookClient._escape_odata_string("")
        assert result == ""

    def test_none_value(self):
        """测试None值"""
        result = OutlookClient._escape_odata_string(None)
        assert result is None


class TestInputValidation:
    """测试输入验证功能"""

    def test_valid_input(self):
        """测试有效输入"""
        # 正常输入不应该抛出异常
        OutlookClient._validate_filter_input("user@example.com", "测试字段")
        OutlookClient._validate_filter_input("每日总结", "测试字段")

    def test_empty_input(self):
        """测试空输入"""
        # 空输入不应该抛出异常
        OutlookClient._validate_filter_input("", "测试字段")
        OutlookClient._validate_filter_input(None, "测试字段")

    def test_length_limit(self):
        """测试长度限制"""
        # 超长输入应该抛出ValueError
        long_string = "a" * 1001
        with pytest.raises(ValueError) as excinfo:
            OutlookClient._validate_filter_input(long_string, "测试字段")
        assert "长度不能超过" in str(excinfo.value)

    def test_control_characters(self):
        """测试危险的控制字符"""
        # 某些控制字符应该抛出ValueError
        with pytest.raises(ValueError) as excinfo:
            OutlookClient._validate_filter_input("user\x00test", "测试字段")
        assert "不允许的控制字符" in str(excinfo.value)

    def test_allowed_whitespace(self):
        """测试允许的空白字符"""
        # 普通空格、制表符、换行符应该被允许
        OutlookClient._validate_filter_input("user test\t\n", "测试字段")


class TestSecurityScenarios:
    """测试实际的安全场景"""

    def test_injection_attempt_single_quote(self):
        """测试单引号注入尝试"""
        malicious_input = "test' or '1'='1"
        escaped = OutlookClient._escape_odata_string(malicious_input)
        # 单引号应该被正确转义
        assert "''" in escaped
        assert "test'' or ''1''=''1" == escaped

    def test_special_email_characters(self):
        """测试邮箱中的特殊字符"""
        # 这些都是邮箱地址中合法的字符
        valid_emails = [
            "user+tag@example.com",
            "user.name@example.com",
            "user_name@example.com",
            "user-name@example.com",
        ]
        for email in valid_emails:
            result = OutlookClient._escape_odata_string(email)
            # 这些字符不需要转义
            assert result == email

    def test_chinese_characters(self):
        """测试中文字符"""
        chinese_text = "每日总结"
        result = OutlookClient._escape_odata_string(chinese_text)
        # 中文字符应该保持不变
        assert result == chinese_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

