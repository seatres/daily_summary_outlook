"""
Cloudflare R2存储客户端实现
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
from urllib.parse import quote

try:
    import boto3
    from botocore.client import Config
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    raise ImportError("请安装boto3: pip install boto3 botocore")

from ..base.storage_base import StorageClientBase, StorageResult
from ...exceptions.storage_exceptions import R2StorageError
from ...utils.config_manager import ConfigManager


@dataclass
class R2Result(StorageResult):
    """R2存储操作结果"""
    raw_response: Optional[Any] = None


class R2Client(StorageClientBase):
    """Cloudflare R2存储客户端"""

    def __init__(
        self,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        bucket_name: Optional[str] = None,
        custom_domain: Optional[str] = None
    ):
        """
        初始化R2客户端

        Args:
            access_key_id: R2访问密钥ID
            secret_access_key: R2秘密访问密钥
            endpoint_url: R2端点URL
            bucket_name: 存储桶名称
            custom_domain: 自定义域名（用于公共访问）
        """
        super().__init__()

        # 获取配置
        config = ConfigManager.get_storage_config()
        self.access_key_id = access_key_id or config.get('r2_access_key_id')
        self.secret_access_key = secret_access_key or config.get('r2_secret_access_key')
        self.endpoint_url = endpoint_url or config.get('r2_endpoint')
        self.bucket_name = bucket_name or config.get('r2_bucket_name')
        self.custom_domain = custom_domain

        if not all([self.access_key_id, self.secret_access_key, self.endpoint_url, self.bucket_name]):
            raise R2StorageError("R2配置不完整，请检查环境变量")

        # 初始化boto3客户端
        try:
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )
            self.logger = logging.getLogger(__name__)
            self.logger.info("R2客户端初始化成功")
        except Exception as e:
            raise R2StorageError(f"R2客户端初始化失败: {str(e)}")

    def upload_file(
        self,
        file_path: Union[str, Path],
        object_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> R2Result:
        """
        上传文件到R2

        Args:
            file_path: 本地文件路径
            object_name: 远程对象名称，如果为None则使用文件名
            metadata: 文件元数据

        Returns:
            上传结果
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return R2Result(
                success=False,
                error=f"文件不存在: {file_path}"
            )

        # 设置对象名称
        if object_name is None:
            object_name = file_path.name

        try:
            # 准备额外参数
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata

            # 设置内容类型
            if file_path.suffix.lower() == '.pdf':
                extra_args['ContentType'] = 'application/pdf'

            # 设置公共读取权限
            extra_args['ACL'] = 'public-read'

            # 上传文件
            self.client.upload_file(
                str(file_path),
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )

            # 生成访问URL（24小时有效期）
            file_url = self.get_file_url(object_name, use_presigned=True, expires_in=86400)

            result = R2Result(
                success=True,
                file_url=file_url,
                file_key=object_name,
                metadata={
                    'bucket': self.bucket_name,
                    'object_name': object_name,
                    'file_size': file_path.stat().st_size,
                    'local_path': str(file_path)
                }
            )

            self.logger.info(f"文件上传成功: {object_name}")
            return result

        except ClientError as e:
            error_msg = f"上传文件失败: {str(e)}"
            self.logger.error(error_msg)
            return R2Result(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"上传文件时发生未知错误: {str(e)}"
            self.logger.error(error_msg)
            return R2Result(success=False, error=error_msg)

    def download_file(
        self,
        object_name: str,
        local_path: Union[str, Path]
    ) -> R2Result:
        """
        从R2下载文件

        Args:
            object_name: 远程对象名称
            local_path: 本地保存路径

        Returns:
            下载结果
        """
        local_path = Path(local_path)

        try:
            # 确保本地目录存在
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # 下载文件
            self.client.download_file(
                self.bucket_name,
                object_name,
                str(local_path)
            )

            result = R2Result(
                success=True,
                file_key=object_name,
                metadata={
                    'bucket': self.bucket_name,
                    'object_name': object_name,
                    'local_path': str(local_path),
                    'file_size': local_path.stat().st_size
                }
            )

            self.logger.info(f"文件下载成功: {object_name}")
            return result

        except ClientError as e:
            error_msg = f"下载文件失败: {str(e)}"
            self.logger.error(error_msg)
            return R2Result(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"下载文件时发生未知错误: {str(e)}"
            self.logger.error(error_msg)
            return R2Result(success=False, error=error_msg)

    def delete_file(self, object_name: str) -> R2Result:
        """
        删除R2中的文件

        Args:
            object_name: 远程对象名称

        Returns:
            删除结果
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )

            result = R2Result(
                success=True,
                file_key=object_name,
                metadata={
                    'bucket': self.bucket_name,
                    'object_name': object_name,
                    'operation': 'delete'
                }
            )

            self.logger.info(f"文件删除成功: {object_name}")
            return result

        except ClientError as e:
            error_msg = f"删除文件失败: {str(e)}"
            self.logger.error(error_msg)
            return R2Result(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"删除文件时发生未知错误: {str(e)}"
            self.logger.error(error_msg)
            return R2Result(success=False, error=error_msg)

    def get_file_url(self, object_name: str, use_presigned: bool = True, expires_in: int = 3600) -> str:
        """
        获取文件访问URL

        Args:
            object_name: 远程对象名称
            use_presigned: 是否使用预签名URL（解决公共访问权限问题）
            expires_in: 预签名URL过期时间（秒），默认1小时

        Returns:
            文件访问URL
        """
        # 对对象名称进行URL编码
        encoded_object_name = quote(object_name)

        # 如果设置了自定义域名，使用自定义域名
        if self.custom_domain:
            return f"{self.custom_domain}/{encoded_object_name}"

        # 如果使用预签名URL
        if use_presigned:
            try:
                presigned_url = self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': object_name},
                    ExpiresIn=expires_in
                )
                return presigned_url
            except Exception as e:
                self.logger.warning(f"生成预签名URL失败: {str(e)}，回退到直接URL")

        # 否则使用默认的R2 URL格式
        # 注意：实际的R2公共URL格式可能需要根据具体配置调整
        return f"{self.endpoint_url}/{self.bucket_name}/{encoded_object_name}"

    def list_files(self, prefix: Optional[str] = None) -> R2Result:
        """
        列出存储桶中的文件

        Args:
            prefix: 文件名前缀过滤

        Returns:
            文件列表结果
        """
        try:
            kwargs = {'Bucket': self.bucket_name}
            if prefix:
                kwargs['Prefix'] = prefix

            paginator = self.client.get_paginator('list_objects_v2')

            files = []
            for page in paginator.paginate(**kwargs):
                for obj in page.get('Contents', []):
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'url': self.get_file_url(obj['Key'])
                    })

            result = R2Result(
                success=True,
                metadata={
                    'bucket': self.bucket_name,
                    'prefix': prefix,
                    'file_count': len(files),
                    'files': files
                }
            )

            self.logger.info(f"文件列表获取成功，共 {len(files)} 个文件")
            return result

        except ClientError as e:
            error_msg = f"获取文件列表失败: {str(e)}"
            self.logger.error(error_msg)
            return R2Result(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"获取文件列表时发生未知错误: {str(e)}"
            self.logger.error(error_msg)
            return R2Result(success=False, error=error_msg)

    def file_exists(self, object_name: str) -> bool:
        """
        检查文件是否存在

        Args:
            object_name: 远程对象名称

        Returns:
            文件是否存在
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError:
            return False
        except Exception:
            return False

    @staticmethod
    def validate_r2_config() -> 'R2ValidationResult':
        """
        验证Cloudflare R2配置是否正确

        Returns:
            R2ValidationResult: 验证结果
        """

        @dataclass
        class R2ValidationResult:
            is_valid: bool
            access_key_exists: bool
            secret_key_exists: bool
            endpoint_exists: bool
            bucket_exists: bool
            can_initialize: bool
            can_connect: bool
            can_access_bucket: bool
            errors: List[str]
            warnings: List[str]

        errors = []
        warnings = []

        # 1. 检查所有必需的环境变量
        config = ConfigManager.get_storage_config()
        access_key = config.get('r2_access_key_id')
        secret_key = config.get('r2_secret_access_key')
        endpoint = config.get('r2_endpoint')
        bucket_name = config.get('r2_bucket_name')

        access_key_exists = access_key is not None and access_key.strip() != ""
        secret_key_exists = secret_key is not None and secret_key.strip() != ""
        endpoint_exists = endpoint is not None and endpoint.strip() != ""
        bucket_exists = bucket_name is not None and bucket_name.strip() != ""

        if not access_key_exists:
            errors.append("R2_ACCESS_KEY_ID环境变量未设置或为空")
        if not secret_key_exists:
            errors.append("R2_SECRET_ACCESS_KEY环境变量未设置或为空")
        if not endpoint_exists:
            errors.append("R2_ENDPOINT环境变量未设置或为空")
        if not bucket_exists:
            errors.append("R2_BUCKET_NAME环境变量未设置或为空")

        if not all([access_key_exists, secret_key_exists, endpoint_exists, bucket_exists]):
            return R2ValidationResult(
                is_valid=False,
                access_key_exists=access_key_exists,
                secret_key_exists=secret_key_exists,
                endpoint_exists=endpoint_exists,
                bucket_exists=bucket_exists,
                can_initialize=False,
                can_connect=False,
                can_access_bucket=False,
                errors=errors,
                warnings=warnings
            )

        # 2. 测试客户端初始化
        can_initialize = False
        can_connect = False
        can_access_bucket = False

        try:
            print(f"      🔄 正在初始化Cloudflare R2客户端...")
            client = boto3.client(
                's3',
                endpoint_url=endpoint.strip(),
                aws_access_key_id=access_key.strip(),
                aws_secret_access_key=secret_key.strip(),
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )
            can_initialize = True
            print(f"      ✅ R2客户端初始化成功")

            # 3. 测试连接和权限
            try:
                print(f"      🔄 正在测试R2 API连接和存储桶访问...")
                # 尝试列出存储桶中的对象（限制1个以减少开销）
                response = client.list_objects_v2(Bucket=bucket_name.strip(), MaxKeys=1)
                can_connect = True
                can_access_bucket = True

                object_count = response.get('KeyCount', 0)
                print(f"      ✅ R2连接成功，存储桶 '{bucket_name}' 可访问，包含 {object_count} 个对象")

                # 4. 测试基本操作权限（尝试创建一个测试对象）
                try:
                    print(f"      🔄 正在测试写入权限...")
                    test_key = "config-validation-test.txt"
                    test_content = "This is a configuration validation test file."

                    # 上传测试文件
                    client.put_object(
                        Bucket=bucket_name.strip(),
                        Key=test_key,
                        Body=test_content.encode('utf-8'),
                        ContentType='text/plain'
                    )
                    print(f"      ✅ 写入权限测试成功，已创建测试文件: {test_key}")

                    # 清理测试文件
                    try:
                        client.delete_object(Bucket=bucket_name.strip(), Key=test_key)
                        print(f"      ✅ 删除权限测试成功，已清理测试文件")
                    except Exception as cleanup_error:
                        warnings.append(f"测试文件清理失败: {str(cleanup_error)}")
                        print(f"      ⚠️ 测试文件清理失败: {str(cleanup_error)}")

                except ClientError as write_error:
                    error_code = write_error.response.get('Error', {}).get('Code', 'Unknown')
                    if error_code == 'AccessDenied':
                        warnings.append("存储桶可访问但写入权限受限")
                        print(f"      ⚠️ 存储桶可访问但写入权限受限")
                    else:
                        warnings.append(f"写入权限测试失败: {str(write_error)}")
                        print(f"      ⚠️ 写入权限测试失败: {str(write_error)}")

            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                if error_code == 'NoSuchBucket':
                    errors.append(f"存储桶 '{bucket_name}' 不存在")
                    print(f"      ❌ 存储桶 '{bucket_name}' 不存在")
                elif error_code == 'AccessDenied':
                    errors.append(f"无权限访问存储桶 '{bucket_name}'")
                    print(f"      ❌ 无权限访问存储桶 '{bucket_name}'")
                else:
                    errors.append(f"R2连接测试失败: {str(e)}")
                    print(f"      ❌ R2连接测试失败: {str(e)}")
            except Exception as e:
                errors.append(f"R2连接测试失败: {str(e)}")
                print(f"      ❌ R2连接测试失败: {str(e)}")

        except Exception as e:
            errors.append(f"R2客户端初始化失败: {str(e)}")
            print(f"      ❌ R2客户端初始化失败: {str(e)}")

        # 5. 综合验证结果
        is_valid = (
            access_key_exists and
            secret_key_exists and
            endpoint_exists and
            bucket_exists and
            can_initialize and
            can_connect and
            can_access_bucket
        )

        return R2ValidationResult(
            is_valid=is_valid,
            access_key_exists=access_key_exists,
            secret_key_exists=secret_key_exists,
            endpoint_exists=endpoint_exists,
            bucket_exists=bucket_exists,
            can_initialize=can_initialize,
            can_connect=can_connect,
            can_access_bucket=can_access_bucket,
            errors=errors,
            warnings=warnings
        )