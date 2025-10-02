"""
缓存管理器
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional


class CacheManager:
    """基于文件的缓存管理器"""

    def __init__(self, cache_dir: str = ".cache", ttl: int = 3600):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
            ttl: 缓存生存时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_file(self, key: str) -> Path:
        """
        获取缓存文件路径
        
        使用SHA-256哈希来安全地处理缓存键，防止路径遍历攻击
        """
        # 计算key的SHA-256哈希
        key_hash = hashlib.sha256(key.encode('utf-8')).hexdigest()
        
        # 确保文件名安全且确定性
        safe_filename = f"{key_hash}.json"
        
        return self.cache_dir / safe_filename

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或过期则返回None
        """
        cache_file = self._get_cache_file(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            if time.time() - cache_data['timestamp'] > self.ttl:
                cache_file.unlink()  # 删除过期缓存
                return None

            return cache_data['value']

        except (json.JSONDecodeError, KeyError, OSError):
            # 缓存文件损坏，删除它
            if cache_file.exists():
                cache_file.unlink()
            return None

    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        cache_file = self._get_cache_file(key)

        cache_data = {
            'timestamp': time.time(),
            'value': value
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            # 缓存写入失败，记录但不影响主流程
            print(f"警告：缓存写入失败: {e}")

    def clear(self) -> None:
        """清除所有缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError:
                pass

    def exists(self, key: str) -> bool:
        """检查缓存是否存在且未过期"""
        return self.get(key) is not None