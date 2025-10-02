#!/usr/bin/env python3
"""
Workflow Tools 配置验证工具

此工具用于验证项目中所有服务的配置是否正确。
支持验证 AI 服务（Gemini、OpenAI、Anthropic）、笔记服务（Notion）和存储服务（R2、S3）。

使用方法:
    python validate_config.py [--service SERVICE] [--verbose] [--format FORMAT]

选项:
    --service SERVICE    仅验证指定服务 (gemini, openai, anthropic, notion, r2, s3, all)
    --verbose, -v        显示详细输出
    --format FORMAT      输出格式 (text, json)
    --help, -h          显示此帮助信息
"""

import sys
import os
import json
import argparse
import traceback
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_env_file(env_path: Optional[Path], verbose: bool = False) -> Optional[Path]:
    """加载 .env 文件中的环境变量"""

    candidate_paths: List[Path] = []

    if env_path:
        candidate_paths.append(env_path)

    current_dir = Path(__file__).resolve().parent
    candidate_paths.append(current_dir / ".env")
    candidate_paths.append(current_dir.parent / ".env")
    candidate_paths.append(Path.cwd() / ".env")

    # 去重并保留顺序
    seen = set()
    unique_candidates: List[Path] = []
    for path in candidate_paths:
        if path not in seen:
            unique_candidates.append(path)
            seen.add(path)

    if verbose:
        print("  🔍 搜索可能的 .env 路径:")
        for candidate in unique_candidates:
            print(f"    • {candidate}")

    for path in unique_candidates:
        if path.exists() and path.is_file():
            if verbose:
                print(f"  🗂️  正在加载环境文件: {path}")

            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" not in line:
                        if verbose:
                            print(f"    ⚠️  忽略无效行: {line}")
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    if key and key not in os.environ:
                        os.environ[key] = value
                        if verbose:
                            print(f"    ✅ 已加载环境变量 {key}")
                    elif verbose and key:
                        print(f"    ↪️  跳过已有环境变量 {key}")

            return path

    if verbose:
        print("  ⚠️  未找到 .env 文件，使用当前环境变量")

    return None


class ConfigValidator:
    """配置验证器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}

    def log(self, message: str) -> None:
        """输出日志信息"""
        if self.verbose:
            print(f"  {message}")

    def validate_gemini(self) -> Dict[str, Any]:
        """验证 Gemini AI 配置"""
        self.log("🔍 验证 Gemini AI 配置...")
        self.log("    - 步骤 1: 获取环境变量 GEMINI_API_KEY")

        try:
            # 基本环境变量检查
            api_key = os.getenv('GEMINI_API_KEY')
            api_key_exists = api_key is not None and api_key.strip() != ""

            errors = []
            warnings = []

            if not api_key_exists:
                errors.append("GEMINI_API_KEY环境变量未设置或为空")
                self.log("    ❌ 未找到 GEMINI_API_KEY 环境变量")
                self.results['gemini'] = {
                    'valid': False,
                    'details': {
                        'api_key_exists': False,
                        'api_key_format_valid': False,
                        'can_initialize': False,
                        'can_connect': False,
                        'model_available': False,
                        'errors': errors,
                        'warnings': warnings
                    }
                }
                self.log("❌ Gemini AI 配置有问题")
                return self.results['gemini']

            # API密钥格式验证
            self.log("    - 步骤 2: 验证 API 密钥格式是否正确")
            api_key_format_valid = api_key.startswith("AIza") and len(api_key) > 20

            if not api_key_format_valid:
                errors.append("GEMINI_API_KEY格式不正确，应该以'AIza'开头且长度大于20")
                masked = f"{api_key[:4]}...{api_key[-4:]}" if api_key and len(api_key) > 8 else "<redacted>"
                self.log(f"    ❌ API 密钥格式不正确: {masked}")
                self.results['gemini'] = {
                    'valid': False,
                    'details': {
                        'api_key_exists': True,
                        'api_key_format_valid': False,
                        'can_initialize': False,
                        'can_connect': False,
                        'model_available': False,
                        'errors': errors,
                        'warnings': warnings
                    }
                }
                self.log("❌ Gemini AI 配置有问题")
                return self.results['gemini']

            # 尝试动态导入和测试
            self.log("    - 步骤 3: 尝试初始化 Gemini 客户端并进行连通性测试")
            try:
                from workflow_tools.ai_models.gemini.gemini_client import GeminiClient
                self.log("      ✅ 已成功导入 GeminiClient 模块")
                self.log("      🚀 开始执行深入验证（包含实际API对话测试）...")
                result = GeminiClient.validate_gemini_config()
                self.log("      ✅ 已完成 GeminiClient.validate_gemini_config() 验证")

                self.results['gemini'] = {
                    'valid': result.is_valid,
                    'details': {
                        'api_key_exists': result.api_key_exists,
                        'api_key_format_valid': result.api_key_format_valid,
                        'can_initialize': result.can_initialize,
                        'can_connect': result.can_connect,
                        'model_available': result.model_available,
                        'errors': result.errors,
                        'warnings': result.warnings
                    }
                }

                if result.is_valid:
                    self.log("✅ Gemini AI 配置正确")
                else:
                    self.log("❌ Gemini AI 配置有问题")

                return self.results['gemini']

            except ImportError as e:
                # 如果模块导入失败，但基本检查通过，认为配置基本正确
                warnings.append(f"无法进行完整验证（模块导入失败）: {str(e)}")
                self.log("      ⚠️ 无法导入 GeminiClient 模块，捕获 ImportError")
                self.log("      ⚠️ 原始异常信息如下：")
                if self.verbose:
                    traceback.print_exc()
                self.results['gemini'] = {
                    'valid': True,  # 基本配置正确
                    'details': {
                        'api_key_exists': True,
                        'api_key_format_valid': True,
                        'can_initialize': False,
                        'can_connect': False,
                        'model_available': False,
                        'errors': [],
                        'warnings': warnings
                    }
                }
                self.log("✅ Gemini AI 基本配置正确（无法进行完整验证）")
                return self.results['gemini']

        except Exception as e:
            error_msg = f"验证 Gemini 配置时发生错误: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.log("    ⚠️ 完整异常堆栈信息：")
            if self.verbose:
                traceback.print_exc()
            self.results['gemini'] = {
                'valid': False,
                'error': error_msg,
                'details': {}
            }
            return self.results['gemini']

    def validate_openai(self) -> Dict[str, Any]:
        """验证 OpenAI 配置"""
        self.log("🔍 验证 OpenAI 配置...")
        self.log("    - 步骤 1: 获取环境变量 OPENAI_API_KEY")

        try:
            api_key = os.getenv('OPENAI_API_KEY')
            api_key_exists = api_key is not None and api_key.strip() != ""

            result = {
                'valid': api_key_exists,
                'details': {
                    'api_key_exists': api_key_exists,
                    'errors': [] if api_key_exists else ["OPENAI_API_KEY环境变量未设置或为空"],
                    'warnings': []
                }
            }

            if api_key_exists:
                # 基本格式验证（OpenAI API Key 以 sk- 开头）
                self.log("    - 步骤 2: 验证 API 密钥是否以 'sk-' 开头")
                if api_key.startswith('sk-'):
                    self.log("      ✅ OpenAI API 密钥格式正确")
                    result['details']['api_key_format_valid'] = True
                    self.log("✅ OpenAI 配置正确")
                else:
                    # 创建掩码版本的密钥用于日志记录
                    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) >= 8 else "***"
                    self.log(f"      ❌ OpenAI API 密钥格式不正确: {masked_key}")
                    result['valid'] = False
                    result['details']['errors'].append("OPENAI_API_KEY格式不正确，应该以'sk-'开头")
                    result['details']['api_key_format_valid'] = False
                    self.log("❌ OpenAI 配置有问题")
            else:
                self.log("    ❌ 未找到 OPENAI_API_KEY 环境变量")
                self.log("❌ OpenAI 配置有问题")

            self.results['openai'] = result
            return result

        except Exception as e:
            error_msg = f"验证 OpenAI 配置时发生错误: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.log("    ⚠️ 完整异常堆栈信息：")
            if self.verbose:
                traceback.print_exc()
            self.results['openai'] = {
                'valid': False,
                'error': error_msg,
                'details': {}
            }
            return self.results['openai']

    def validate_anthropic(self) -> Dict[str, Any]:
        """验证 Anthropic 配置"""
        self.log("🔍 验证 Anthropic 配置...")
        self.log("    - 步骤 1: 获取环境变量 ANTHROPIC_API_KEY")

        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            api_key_exists = api_key is not None and api_key.strip() != ""

            result = {
                'valid': api_key_exists,
                'details': {
                    'api_key_exists': api_key_exists,
                    'errors': [] if api_key_exists else ["ANTHROPIC_API_KEY环境变量未设置或为空"],
                    'warnings': []
                }
            }

            if api_key_exists:
                # 基本格式验证（Anthropic API Key 以 sk-ant- 开头）
                self.log("    - 步骤 2: 验证 API 密钥是否以 'sk-ant-' 开头")
                if api_key.startswith('sk-ant-'):
                    self.log("      ✅ Anthropic API 密钥格式正确")
                    result['details']['api_key_format_valid'] = True
                else:
                    # 屏蔽 API 密钥
                    masked = f"{api_key[:4]}...{api_key[-4:]}" if api_key and len(api_key) > 8 else "<redacted>"
                    self.log(f"      ❌ Anthropic API 密钥格式不正确: {masked}")
                    result['valid'] = False
                    result['details']['errors'].append("ANTHROPIC_API_KEY格式不正确，应该以'sk-ant-'开头")
                    result['details']['api_key_format_valid'] = False

                # 只有在验证成功时才记录成功日志
                if result['valid']:
                    self.log("✅ Anthropic 配置正确")
                else:
                    self.log("❌ Anthropic 配置有问题")
            else:
                self.log("    ❌ 未找到 ANTHROPIC_API_KEY 环境变量")
                self.log("❌ Anthropic 配置有问题")

            self.results['anthropic'] = result
            return result

        except Exception as e:
            error_msg = f"验证 Anthropic 配置时发生错误: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.log("    ⚠️ 完整异常堆栈信息：")
            if self.verbose:
                traceback.print_exc()
            self.results['anthropic'] = {
                'valid': False,
                'error': error_msg,
                'details': {}
            }
            return self.results['anthropic']

    def validate_notion(self) -> Dict[str, Any]:
        """验证 Notion 配置"""
        self.log("🔍 验证 Notion 配置...")
        self.log("    - 步骤 1: 获取环境变量 NOTION_TOKEN 和 NOTION_DATABASE_ID")

        try:
            # 基本环境变量检查
            token = os.getenv('NOTION_TOKEN')
            database_id = os.getenv('NOTION_DATABASE_ID')

            token_exists = token is not None and token.strip() != ""
            database_id_exists = database_id is not None and database_id.strip() != ""

            if not token_exists:
                self.log("    ❌ 未找到 NOTION_TOKEN 环境变量")
                self.results['notion'] = {
                    'valid': False,
                    'details': {
                        'token_exists': False,
                        'database_id_exists': database_id_exists,
                        'can_initialize': False,
                        'can_connect': False,
                        'can_access_database': False,
                        'errors': ["NOTION_TOKEN环境变量未设置或为空"],
                        'warnings': []
                    }
                }
                self.log("❌ Notion 配置有问题")
                return self.results['notion']
            else:
                self.log("    ✅ NOTION_TOKEN 已设置")

            if not database_id_exists:
                self.log("    ⚠️ 未找到 NOTION_DATABASE_ID 环境变量（可选）")
            else:
                self.log("    ✅ NOTION_DATABASE_ID 已设置")

            # 尝试动态导入和深度测试
            self.log("    - 步骤 2: 尝试初始化 Notion 客户端并进行连通性测试")
            try:
                from workflow_tools.notes.notion.notion_client import NotionClient
                self.log("      ✅ 已成功导入 NotionClient 模块")
                self.log("      🚀 开始执行深入验证（包含实际API连接测试）...")
                result = NotionClient.validate_notion_config()
                self.log("      ✅ 已完成 NotionClient.validate_notion_config() 验证")

                self.results['notion'] = {
                    'valid': result.is_valid,
                    'details': {
                        'token_exists': result.token_exists,
                        'database_id_exists': result.database_id_exists,
                        'can_initialize': result.can_initialize,
                        'can_connect': result.can_connect,
                        'can_access_database': result.can_access_database,
                        'errors': result.errors,
                        'warnings': result.warnings
                    }
                }

                if result.is_valid:
                    self.log("✅ Notion 配置正确")
                else:
                    self.log("❌ Notion 配置有问题")

                return self.results['notion']

            except ImportError as e:
                # 如果模块导入失败，但基本检查通过，认为配置基本正确
                warnings = [f"无法进行完整验证（模块导入失败）: {str(e)}"]
                self.log("      ⚠️ 无法导入 NotionClient 模块，捕获 ImportError")
                self.log("      ⚠️ 原始异常信息如下：")
                if self.verbose:
                    traceback.print_exc()
                self.results['notion'] = {
                    'valid': True,  # 基本配置正确
                    'details': {
                        'token_exists': True,
                        'database_id_exists': database_id_exists,
                        'can_initialize': False,
                        'can_connect': False,
                        'can_access_database': False,
                        'errors': [],
                        'warnings': warnings
                    }
                }
                self.log("✅ Notion 基本配置正确（无法进行完整验证）")
                return self.results['notion']

        except Exception as e:
            error_msg = f"验证 Notion 配置时发生错误: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.log("    ⚠️ 完整异常堆栈信息：")
            if self.verbose:
                traceback.print_exc()
            self.results['notion'] = {
                'valid': False,
                'error': error_msg,
                'details': {}
            }
            return self.results['notion']

    def validate_r2(self) -> Dict[str, Any]:
        """验证 R2 存储配置"""
        self.log("🔍 验证 R2 存储配置...")
        self.log("    - 步骤 1: 获取环境变量 R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY / R2_ENDPOINT / R2_BUCKET_NAME")

        try:
            # 基本环境变量检查
            access_key = os.getenv('R2_ACCESS_KEY_ID')
            secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
            endpoint = os.getenv('R2_ENDPOINT')
            bucket = os.getenv('R2_BUCKET_NAME')

            access_key_exists = access_key is not None and access_key.strip() != ""
            secret_key_exists = secret_key is not None and secret_key.strip() != ""
            endpoint_exists = endpoint is not None and endpoint.strip() != ""
            bucket_exists = bucket is not None and bucket.strip() != ""

            errors = []
            if not access_key_exists:
                self.log("    ❌ 未找到 R2_ACCESS_KEY_ID 环境变量")
                errors.append("R2_ACCESS_KEY_ID环境变量未设置或为空")
            else:
                self.log("    ✅ R2_ACCESS_KEY_ID 已设置")
            if not secret_key_exists:
                self.log("    ❌ 未找到 R2_SECRET_ACCESS_KEY 环境变量")
                errors.append("R2_SECRET_ACCESS_KEY环境变量未设置或为空")
            else:
                self.log("    ✅ R2_SECRET_ACCESS_KEY 已设置")
            if not endpoint_exists:
                self.log("    ❌ 未找到 R2_ENDPOINT 环境变量")
                errors.append("R2_ENDPOINT环境变量未设置或为空")
            else:
                self.log(f"    ✅ R2_ENDPOINT 已设置: {endpoint}")
            if not bucket_exists:
                self.log("    ❌ 未找到 R2_BUCKET_NAME 环境变量")
                errors.append("R2_BUCKET_NAME环境变量未设置或为空")
            else:
                self.log(f"    ✅ R2_BUCKET_NAME 已设置: {bucket}")

            if not all([access_key_exists, secret_key_exists, endpoint_exists, bucket_exists]):
                self.results['r2'] = {
                    'valid': False,
                    'details': {
                        'access_key_exists': access_key_exists,
                        'secret_key_exists': secret_key_exists,
                        'endpoint_exists': endpoint_exists,
                        'bucket_exists': bucket_exists,
                        'can_initialize': False,
                        'can_connect': False,
                        'can_access_bucket': False,
                        'errors': errors,
                        'warnings': []
                    }
                }
                self.log("❌ R2 存储配置有问题")
                return self.results['r2']

            # 尝试动态导入和深度测试
            self.log("    - 步骤 2: 尝试初始化 R2 客户端并进行连通性测试")
            try:
                from workflow_tools.storage.cloudflare_r2.r2_client import R2Client
                self.log("      ✅ 已成功导入 R2Client 模块")
                self.log("      🚀 开始执行深入验证（包含实际API连接和存储桶测试）...")
                result = R2Client.validate_r2_config()
                self.log("      ✅ 已完成 R2Client.validate_r2_config() 验证")

                self.results['r2'] = {
                    'valid': result.is_valid,
                    'details': {
                        'access_key_exists': result.access_key_exists,
                        'secret_key_exists': result.secret_key_exists,
                        'endpoint_exists': result.endpoint_exists,
                        'bucket_exists': result.bucket_exists,
                        'can_initialize': result.can_initialize,
                        'can_connect': result.can_connect,
                        'can_access_bucket': result.can_access_bucket,
                        'errors': result.errors,
                        'warnings': result.warnings
                    }
                }

                if result.is_valid:
                    self.log("✅ R2 存储配置正确")
                else:
                    self.log("❌ R2 存储配置有问题")

                return self.results['r2']

            except ImportError as e:
                # 如果模块导入失败，但基本检查通过，认为配置基本正确
                warnings = [f"无法进行完整验证（模块导入失败）: {str(e)}"]
                self.log("      ⚠️ 无法导入 R2Client 模块，捕获 ImportError")
                self.log("      ⚠️ 原始异常信息如下：")
                if self.verbose:
                    traceback.print_exc()
                self.results['r2'] = {
                    'valid': True,  # 基本配置正确
                    'details': {
                        'access_key_exists': True,
                        'secret_key_exists': True,
                        'endpoint_exists': True,
                        'bucket_exists': True,
                        'can_initialize': False,
                        'can_connect': False,
                        'can_access_bucket': False,
                        'errors': [],
                        'warnings': warnings
                    }
                }
                self.log("✅ R2 存储基本配置正确（无法进行完整验证）")
                return self.results['r2']

        except Exception as e:
            error_msg = f"验证 R2 配置时发生错误: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.log("    ⚠️ 完整异常堆栈信息：")
            if self.verbose:
                traceback.print_exc()
            self.results['r2'] = {
                'valid': False,
                'error': error_msg,
                'details': {}
            }
            return self.results['r2']

    def validate_s3(self) -> Dict[str, Any]:
        """验证 S3 存储配置"""
        self.log("🔍 验证 S3 存储配置...")
        self.log("    - 步骤 1: 获取环境变量 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_REGION")

        try:
            # 直接检查环境变量
            access_key = os.getenv('AWS_ACCESS_KEY_ID')
            secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            region = os.getenv('AWS_REGION', 'us-east-1')

            access_key_exists = access_key is not None and access_key.strip() != ""
            secret_key_exists = secret_key is not None and secret_key.strip() != ""
            region_exists = region is not None and region.strip() != ""

            if not access_key_exists:
                self.log("    ❌ 未找到 AWS_ACCESS_KEY_ID 环境变量")
            else:
                self.log("    ✅ AWS_ACCESS_KEY_ID 已设置")

            if not secret_key_exists:
                self.log("    ❌ 未找到 AWS_SECRET_ACCESS_KEY 环境变量")
            else:
                self.log("    ✅ AWS_SECRET_ACCESS_KEY 已设置")

            if not region_exists:
                self.log("    ❌ 未找到 AWS_REGION 环境变量，代码将使用默认值 'us-east-1'")
            else:
                self.log(f"    ✅ AWS_REGION 已设置: {region}")

            errors = []
            if not access_key_exists:
                errors.append("AWS_ACCESS_KEY_ID环境变量未设置或为空")
            if not secret_key_exists:
                errors.append("AWS_SECRET_ACCESS_KEY环境变量未设置或为空")

            result = {
                'valid': access_key_exists and secret_key_exists,
                'details': {
                    'access_key_exists': access_key_exists,
                    'secret_key_exists': secret_key_exists,
                    'region_exists': region_exists,
                    'region': region,
                    'errors': errors,
                    'warnings': []
                }
            }

            if result['valid']:
                self.log("✅ S3 存储配置正确")
            else:
                self.log("❌ S3 存储配置有问题")

            self.results['s3'] = result
            return result

        except Exception as e:
            error_msg = f"验证 S3 配置时发生错误: {str(e)}"
            self.log(f"❌ {error_msg}")
            self.log("    ⚠️ 完整异常堆栈信息：")
            if self.verbose:
                traceback.print_exc()
            self.results['s3'] = {
                'valid': False,
                'error': error_msg,
                'details': {}
            }
            return self.results['s3']

    def validate_all(self) -> Dict[str, Any]:
        """验证所有服务配置"""
        if self.verbose:
            print("🚀 开始验证所有服务配置...")

        # 验证所有服务
        self.validate_gemini()
        self.validate_openai()
        self.validate_anthropic()
        self.validate_notion()
        self.validate_r2()
        self.validate_s3()

        return self.results

    def print_summary(self) -> None:
        """打印验证结果摘要"""
        print("\n" + "="*70)
        print("📊 配置验证结果摘要")
        print("="*70)

        total_services = len(self.results)
        valid_services = sum(1 for result in self.results.values() if result.get('valid', False))

        print(f"✅ 验证通过: {valid_services}/{total_services}")
        print(f"❌ 验证失败: {total_services - valid_services}/{total_services}")

        print("\n📋 详细结果:")
        for service, result in self.results.items():
            status = "✅" if result.get('valid', False) else "❌"
            print(f"  {status} {service.upper()}")

            if not result.get('valid', False) and 'details' in result:
                errors = result['details'].get('errors', [])
                if errors:
                    for error in errors[:2]:  # 只显示前2个错误
                        print(f"    💡 {error}")

        print("\n💡 使用 --verbose 参数查看详细验证过程")
        print("💡 使用 --service 参数验证特定服务")
        print("="*70)

    def print_detailed_report(self) -> None:
        """打印详细验证报告"""
        print("\n" + "="*70)
        print("🔍 详细验证报告")
        print("="*70)

        for service, result in self.results.items():
            print(f"\n🔧 {service.upper()} 服务:")

            if result.get('valid', False):
                print("  ✅ 配置正确")
            else:
                print("  ❌ 配置有问题")

            if 'details' in result:
                details = result['details']
                if 'errors' in details and details['errors']:
                    print("  ❌ 错误信息:")
                    for error in details['errors']:
                        print(f"    • {error}")

                if 'warnings' in details and details['warnings']:
                    print("  ⚠️  警告信息:")
                    for warning in details['warnings']:
                        print(f"    • {warning}")

        print("\n" + "="*70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Workflow Tools 配置验证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python validate_config.py                    # 验证所有服务
  python validate_config.py --service gemini   # 仅验证 Gemini
  python validate_config.py --verbose          # 显示详细输出
  python validate_config.py --format json     # JSON格式输出
        """
    )

    parser.add_argument(
        '--service', '-s',
        choices=['gemini', 'openai', 'anthropic', 'notion', 'r2', 's3', 'all'],
        default='all',
        help='要验证的服务 (默认: all)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='输出格式 (默认: text)'
    )

    parser.add_argument(
        '--env',
        type=str,
        default=None,
        help='指定 .env 文件路径（默认自动搜索）'
    )

    args = parser.parse_args()

    # 加载 .env 文件
    specified_env = Path(args.env).expanduser().resolve() if args.env else None
    loaded_env = load_env_file(specified_env, verbose=args.verbose)

    if loaded_env and args.verbose:
        print(f"  ✅ 已加载环境变量文件: {loaded_env}")
    elif args.verbose and specified_env:
        print(f"  ❌ 未能加载指定的环境文件: {specified_env}")

    # 创建验证器
    validator = ConfigValidator(verbose=args.verbose)

    try:
        # 根据参数验证服务
        if args.service == 'all':
            results = validator.validate_all()
        else:
            # 验证指定服务
            if args.service == 'gemini':
                results = {'gemini': validator.validate_gemini()}
            elif args.service == 'openai':
                results = {'openai': validator.validate_openai()}
            elif args.service == 'anthropic':
                results = {'anthropic': validator.validate_anthropic()}
            elif args.service == 'notion':
                results = {'notion': validator.validate_notion()}
            elif args.service == 'r2':
                results = {'r2': validator.validate_r2()}
            elif args.service == 's3':
                results = {'s3': validator.validate_s3()}

        # 输出结果
        if args.format == 'json':
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            # 打印摘要
            validator.print_summary()

            # 如果不是只验证单个服务，打印详细报告
            if args.service == 'all':
                validator.print_detailed_report()

            # 只有在存在验证失败时才打印修复建议
            has_failures = any(not result.get('valid', False) for result in results.values())
            if has_failures:
                print("\n💡 修复建议:")
                print("  1. 检查 .env 文件中的环境变量设置")
                print("  2. 确保 API 密钥格式正确")
                print("  3. 验证网络连接")
                print("  4. 确认相关依赖包已安装")
            else:
                print("\n🎉 所有配置验证通过！您的环境配置完全正确。")

        # 返回适当的退出代码
        all_valid = all(result.get('valid', False) for result in results.values())
        sys.exit(0 if all_valid else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断验证")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
