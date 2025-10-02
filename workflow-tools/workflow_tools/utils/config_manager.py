"""
配置管理器
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class ConfigManager:
    """配置管理器，支持环境变量和.env文件"""
    
    _env_loaded = False
    
    @classmethod
    def _load_env_file(cls) -> None:
        """
        加载.env文件（如果存在）
        只加载一次，避免重复加载
        """
        if cls._env_loaded or not DOTENV_AVAILABLE:
            return
            
        # 查找.env文件的位置
        env_paths = [
            Path.cwd() / '.env',  # 当前工作目录
            Path(__file__).parent.parent.parent.parent / '.env',  # 项目根目录
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break
                
        cls._env_loaded = True

    @classmethod
    def get_env(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取环境变量值（自动加载.env文件）

        Args:
            key: 环境变量键
            default: 默认值

        Returns:
            环境变量值
        """
        cls._load_env_file()
        return os.getenv(key, default)

    @classmethod
    def get_required_env(cls, key: str) -> str:
        """
        获取必需的环境变量值（自动加载.env文件）

        Args:
            key: 环境变量键

        Returns:
            环境变量值

        Raises:
            ValueError: 如果环境变量不存在
        """
        cls._load_env_file()
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"必需的环境变量 {key} 未设置")
        return value

    @classmethod
    def get_ai_config(cls) -> Dict[str, Any]:
        """获取AI配置"""
        return {
            'gemini_api_key': cls.get_env('GEMINI_API_KEY'),
            'openai_api_key': cls.get_env('OPENAI_API_KEY'),
            'anthropic_api_key': cls.get_env('ANTHROPIC_API_KEY'),
        }

    @classmethod
    def get_notes_config(cls) -> Dict[str, Any]:
        """获取笔记配置"""
        return {
            'notion_token': cls.get_env('NOTION_TOKEN'),
            'notion_database_id': cls.get_env('NOTION_DATABASE_ID'),
        }

    @classmethod
    def get_storage_config(cls) -> Dict[str, Any]:
        """获取存储配置"""
        return {
            'r2_access_key_id': cls.get_env('R2_ACCESS_KEY_ID'),
            'r2_secret_access_key': cls.get_env('R2_SECRET_ACCESS_KEY'),
            'r2_endpoint': cls.get_env('R2_ENDPOINT'),
            'r2_bucket_name': cls.get_env('R2_BUCKET_NAME'),
            'aws_access_key_id': cls.get_env('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': cls.get_env('AWS_SECRET_ACCESS_KEY'),
            'aws_region': cls.get_env('AWS_REGION', 'us-east-1'),
        }