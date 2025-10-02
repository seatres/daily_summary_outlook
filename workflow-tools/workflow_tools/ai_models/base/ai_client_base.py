"""
AI客户端基类定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable, Union
from pathlib import Path

# 进度回调类型定义
ProgressCallback = Callable[[str, int, int], None]


@dataclass
class AIResult:
    """AI分析结果基类"""
    success: bool = True
    content: Optional[str] = None
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class AIClientBase(ABC):
    """AI客户端抽象基类"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化AI客户端

        Args:
            api_key: API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key

    @abstractmethod
    def analyze_document(
        self,
        file_path: Union[str, Path],
        prompt: str,
        progress_callback: Optional[ProgressCallback] = None
    ) -> AIResult:
        """
        分析文档

        Args:
            file_path: 文档文件路径
            prompt: 分析提示
            progress_callback: 进度回调函数

        Returns:
            分析结果
        """
        pass

    @abstractmethod
    def generate_content(self, prompt: str) -> AIResult:
        """
        生成内容

        Args:
            prompt: 生成提示

        Returns:
            生成结果
        """
        pass

    def default_progress_callback(self, message: str, current: int, total: int) -> None:
        """默认进度回调函数"""
        print(f"[{current}/{total}] {message}")

    def _get_progress_callback(self, callback: Optional[ProgressCallback]) -> ProgressCallback:
        """获取进度回调函数"""
        return callback or self.default_progress_callback