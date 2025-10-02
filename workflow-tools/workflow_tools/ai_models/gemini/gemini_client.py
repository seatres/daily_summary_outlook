"""
Gemini AI客户端实现
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Any, List

try:
    # 尝试使用新版本的Google GenAI SDK
    from google import genai
    from google.genai import types
    from google.api_core import exceptions as google_exceptions
    NEW_SDK = True
except ImportError:
    try:
        # 回退到旧版本
        import google.generativeai as genai
        from google.api_core import exceptions as google_exceptions
        NEW_SDK = False
    except ImportError:
        raise ImportError("请安装google-genai或google-generativeai: pip install google-genai")

from ..base.ai_client_base import AIClientBase, AIResult, ProgressCallback
from ...exceptions.ai_exceptions import GeminiAPIError
from ...utils.config_manager import ConfigManager
from ...utils.cache_manager import CacheManager
from ...utils.file_utils import get_cache_key

# 导入settings配置
try:
    # 尝试从主项目导入settings
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    sys.path.insert(0, project_root)
    from config.settings import GEMINI_MODEL_NAME, GEMINI_TEMPERATURE
    SETTINGS_AVAILABLE = True
except ImportError:
    # 如果无法导入settings，使用默认值
    GEMINI_MODEL_NAME = "gemini-1.5-flash"
    GEMINI_TEMPERATURE = 1.0
    SETTINGS_AVAILABLE = False


@dataclass
class GeminiResult(AIResult):
    """Gemini分析结果"""
    raw_response: Optional[Any] = None


@dataclass
class GeminiValidationResult:
    """Gemini配置验证结果"""
    is_valid: bool
    api_key_exists: bool
    api_key_format_valid: bool
    can_initialize: bool
    can_connect: bool
    model_available: bool
    errors: List[str]
    warnings: List[str]


class GeminiClient(AIClientBase):
    """Gemini AI客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        cache_enabled: bool = True,
        cache_ttl: int = 3600
    ):
        """
        初始化Gemini客户端

        Args:
            api_key: API密钥，如果为None则从环境变量获取
            model_name: 模型名称，如果为None则从settings.py获取
            cache_enabled: 是否启用缓存
            cache_ttl: 缓存生存时间（秒）
        """
        super().__init__(api_key)

        # 获取API密钥
        if self.api_key is None:
            self.api_key = ConfigManager.get_required_env('GEMINI_API_KEY')

        # 获取模型名称
        if model_name is None:
            model_name = GEMINI_MODEL_NAME

        # 配置Gemini API
        if NEW_SDK:
            # 使用新版本SDK，支持更好的超时控制
            self.client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(timeout=600_000)  # 10分钟超时，单位毫秒
            )
            self.model_name = model_name
        else:
            # 使用旧版本SDK
            genai.configure(api_key=self.api_key)

            # 配置生成参数
            generation_config = genai.types.GenerationConfig(
                temperature=GEMINI_TEMPERATURE,
                max_output_tokens=65535,
            )

            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
        self.model_name = model_name

        # 缓存配置
        self.cache_enabled = cache_enabled
        self.cache_manager = CacheManager(cache_dir=".cache/gemini", ttl=cache_ttl) if cache_enabled else None

        # 日志配置
        self.logger = logging.getLogger(__name__)

    def _get_test_model_name(self) -> str:
        """
        获取用于测试的模型名称
        
        Returns:
            测试模型名称（与运行时使用的模型相同）
        """
        return self.model_name

    def analyze_document(
        self,
        file_path: Union[str, Path],
        prompt: str,
        progress_callback: Optional[ProgressCallback] = None
    ) -> GeminiResult:
        """
        分析文档

        Args:
            file_path: 文档文件路径
            prompt: 分析提示
            progress_callback: 进度回调函数

        Returns:
            分析结果
        """
        file_path = Path(file_path)
        callback = self._get_progress_callback(progress_callback)

        try:
            callback("开始分析文档", 1, 4)

            # 检查缓存
            if self.cache_enabled:
                cache_key = get_cache_key(file_path, prompt)
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    callback("从缓存获取结果", 4, 4)
                    self.logger.info(f"从缓存获取分析结果: {file_path}")
                    return GeminiResult(**cached_result)

            callback("上传文件", 2, 4)

            # 上传文件到Gemini
            sample_file = self._upload_file(file_path)

            callback("分析中", 3, 4)

            # 生成内容
            response = self._generate_content([sample_file, prompt])

            # 构建结果
            result = GeminiResult(
                success=True,
                content=response.text.strip(),
                metadata={
                    'model': self.model_name,
                    'file_path': str(file_path),
                    'prompt': prompt
                },
                raw_response=response
            )

            # 缓存结果
            if self.cache_enabled:
                cache_data = {
                    'success': result.success,
                    'content': result.content,
                    'metadata': result.metadata,
                    'error': result.error
                }
                self.cache_manager.set(cache_key, cache_data)

            callback("分析完成", 4, 4)
            self.logger.info(f"文档分析完成: {file_path}")

            return result

        except Exception as e:
            error_msg = f"文档分析失败: {str(e)}"
            self.logger.error(error_msg)
            return GeminiResult(success=False, error=error_msg)

    def generate_content(self, prompt: str) -> GeminiResult:
        """
        生成内容

        Args:
            prompt: 生成提示

        Returns:
            生成结果
        """
        try:
            response = self._generate_content(prompt)

            result = GeminiResult(
                success=True,
                content=response.text.strip(),
                metadata={
                    'model': self.model_name,
                    'prompt': prompt
                },
                raw_response=response
            )

            self.logger.info("内容生成完成")
            return result

        except Exception as e:
            error_msg = f"内容生成失败: {str(e)}"
            self.logger.error(error_msg)
            return GeminiResult(success=False, error=error_msg)

    def extract_title(self, file_path: Union[str, Path]) -> GeminiResult:
        """
        提取文档标题

        Args:
            file_path: 文档文件路径

        Returns:
            提取结果
        """
        title_prompt = "只输出论文的题目，不要包含其它任何别的内容。"
        result = self.analyze_document(file_path, title_prompt)

        if result.success:
            result.title = result.content
            result.metadata['task'] = 'title_extraction'

        return result

    def classify_paper_type(self, file_path: Union[str, Path]) -> GeminiResult:
        """
        分类论文类型（综述 vs 非综述）

        Args:
            file_path: 文档文件路径

        Returns:
            分类结果
        """
        classification_prompt = """判断上传的文件是否属于综述性文章。具体判断方法如下：
	1.	如果论文提出了新的算法、方法或对已有算法的改进，且具有创新性的贡献，输出false，表示这是一篇非综述性论文。
	2.	如果论文仅对现有的算法或方法进行系统性的总结、分析和评估，并且没有提出任何实质性的新算法或改进，输出true，表示这是一篇综述性论文。

要求：
	•	如果是综述文章，输出true；
	•	如果不是综述文章，输出false。"""

        result = self.analyze_document(file_path, classification_prompt)

        if result.success:
            is_survey = "true" in result.content.lower()
            result.metadata.update({
                'task': 'paper_classification',
                'is_survey': is_survey,
                'paper_type': 'survey' if is_survey else 'research'
            })

        return result

    def _upload_file(self, file_path: Path) -> Any:
        """上传文件到Gemini"""
        try:
            if NEW_SDK:
                # 新版本SDK使用file参数
                sample_file = self.client.files.upload(file=str(file_path))
            else:
                # 旧版本SDK使用path参数
                sample_file = genai.upload_file(path=str(file_path), display_name=file_path.name)
            self.logger.debug(f"文件上传成功: {file_path}")
            return sample_file
        except Exception as e:
            raise GeminiAPIError(f"文件上传失败: {str(e)}")

    def _generate_content(self, content_input) -> Any:
        """生成内容，包含错误处理和重试"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if NEW_SDK:
                    # 新版本SDK，支持更长超时时间
                    if isinstance(content_input, list):
                        # 包含文件和提示的情况
                        response = self.client.models.generate_content(
                            model=self.model_name,
                            contents=content_input,
                            config=types.GenerateContentConfig(
                                temperature=GEMINI_TEMPERATURE,
                                max_output_tokens=65535,
                            )
                        )
                    else:
                        # 只有提示的情况
                        response = self.client.models.generate_content(
                            model=self.model_name,
                            contents=content_input,
                            config=types.GenerateContentConfig(
                                temperature=GEMINI_TEMPERATURE,
                                max_output_tokens=65535,
                            )
                        )
                else:
                    # 旧版本SDK
                    response = self.model.generate_content(content_input)
                return response
            except Exception as e:
                error_msg = str(e).lower()
                if "resource" in error_msg and "exhaust" in error_msg:
                    # 配额耗尽
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"API配额耗尽，等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        raise GeminiAPIError("API配额耗尽，请稍后重试")
                else:
                    # 其他错误
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"API调用失败，等待 {wait_time} 秒后重试: {str(e)}")
                        time.sleep(wait_time)
                    else:
                        raise GeminiAPIError(f"API调用失败: {str(e)}")

        raise GeminiAPIError("所有重试尝试都失败")

    @staticmethod
    def _get_test_model_name_static() -> str:
        """
        获取用于测试的模型名称（静态方法版本）
        
        Returns:
            测试模型名称（从settings.py获取）
        """
        return GEMINI_MODEL_NAME

    @staticmethod
    def validate_gemini_config() -> GeminiValidationResult:
        """
        验证Gemini AI配置是否正确

        Returns:
            GeminiValidationResult: 验证结果
        """
        errors = []
        warnings = []

        # 1. 检查API密钥是否存在
        api_key = ConfigManager.get_env('GEMINI_API_KEY')
        api_key_exists = api_key is not None and api_key.strip() != ""

        if not api_key_exists:
            errors.append("GEMINI_API_KEY环境变量未设置或为空")
            return GeminiValidationResult(
                is_valid=False,
                api_key_exists=False,
                api_key_format_valid=False,
                can_initialize=False,
                can_connect=False,
                model_available=False,
                errors=errors,
                warnings=warnings
            )

        # 2. 验证API密钥格式
        api_key_format_valid = api_key.startswith("AIza") and len(api_key) > 20

        if not api_key_format_valid:
            errors.append("GEMINI_API_KEY格式不正确，应该是以'AIZA'开头且长度大于20的字符串")
            # 继续测试其他步骤，即使格式不正确

        # 3. 测试客户端初始化
        can_initialize = False
        can_connect = False
        model_available = False

        try:
            # 尝试配置Gemini API
            if NEW_SDK:
                client = genai.Client(api_key=api_key.strip())
            else:
                genai.configure(api_key=api_key.strip())

            # 获取测试模型名称
            test_model_name = GeminiClient._get_test_model_name_static()
            print(f"      🔄 使用测试模型: {test_model_name}")

            # 尝试创建模型实例
            model = genai.GenerativeModel(test_model_name)
            can_initialize = True

            # 4. 测试连接和模型可用性
            try:
                # 发送一个简单的测试请求
                test_message = "Hello, this is a test message. Please respond with 'Test successful' to confirm the connection."
                print(f"      🔄 发送测试消息: {test_message}")
                response = model.generate_content(test_message)
                if response and response.text:
                    can_connect = True
                    model_available = True
                    print(f"      ✅ 收到API响应: {response.text.strip()}")
                else:
                    warnings.append("API响应为空或格式异常")
                    print("      ❌ API响应为空或格式异常")

            except google_exceptions.ResourceExhausted:
                # 配额耗尽，但连接是正常的
                can_connect = True
                warnings.append("API连接正常，但配额耗尽，请稍后重试")
                print("      ⚠️ API连接正常，但配额耗尽，请稍后重试")
            except google_exceptions.InvalidArgument as e:
                warnings.append("API密钥可能无效或无权限访问指定模型")
                print(f"      ❌ API密钥可能无效或无权限访问指定模型: {str(e)}")
            except google_exceptions.PermissionDenied as e:
                errors.append("API密钥无权限访问Gemini API")
                print(f"      ❌ API密钥无权限访问Gemini API: {str(e)}")
            except Exception as e:
                errors.append(f"API连接测试失败: {str(e)}")
                print(f"      ❌ API连接测试失败: {str(e)}")

        except Exception as e:
            errors.append(f"Gemini客户端初始化失败: {str(e)}")
            print(f"      ❌ Gemini客户端初始化失败: {str(e)}")

        # 5. 综合验证结果
        is_valid = (
            api_key_exists and
            api_key_format_valid and
            can_initialize and
            can_connect and
            model_available
        )

        if not is_valid:
            # 提供修复建议
            if not api_key_exists:
                warnings.append("请在.env文件中设置GEMINI_API_KEY")
            if not api_key_format_valid:
                warnings.append("请检查GEMINI_API_KEY是否为有效的Google AI API密钥")
            if not can_initialize:
                warnings.append("请检查google-generativeai是否正确安装: pip install google-generativeai")
            if not can_connect:
                warnings.append("请检查网络连接和API密钥权限")

        return GeminiValidationResult(
            is_valid=is_valid,
            api_key_exists=api_key_exists,
            api_key_format_valid=api_key_format_valid,
            can_initialize=can_initialize,
            can_connect=can_connect,
            model_available=model_available,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def print_validation_report(result: GeminiValidationResult) -> None:
        """
        打印验证报告

        Args:
            result: 验证结果
        """
        print("\n" + "="*60)
        print("🔍 Gemini AI 配置验证报告")
        print("="*60)

        print(f"✅ 总体状态: {'✅ 配置正确' if result.is_valid else '❌ 配置有问题'}")

        print("\n📋 详细检查结果:")
        print(f"  • API密钥存在: {'✅' if result.api_key_exists else '❌'}")
        print(f"  • API密钥格式: {'✅' if result.api_key_format_valid else '❌'}")
        print(f"  • 客户端初始化: {'✅' if result.can_initialize else '❌'}")
        print(f"  • API连接测试: {'✅' if result.can_connect else '❌'}")
        print(f"  • 模型可用性: {'✅' if result.model_available else '❌'}")

        if result.errors:
            print("\n❌ 错误信息:")
            for i, error in enumerate(result.errors, 1):
                print(f"  {i}. {error}")

        if result.warnings:
            print("\n⚠️  警告信息:")
            for i, warning in enumerate(result.warnings, 1):
                print(f"  {i}. {warning}")

        if result.is_valid:
            print("\n🎉 所有检查都通过了！Gemini AI配置正确。")
        else:
            print("\n💡 修复建议:")
            print("  1. 检查.env文件中的GEMINI_API_KEY设置")
            print("  2. 确认API密钥是有效的Google AI API密钥")
            print("  3. 确保网络连接正常")
            print("  4. 确认google-generativeai已正确安装")

        print("="*60)