"""
文件处理工具
"""

import re
import hashlib
from pathlib import Path
from typing import Union


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    安全化文件名，支持中文

    Args:
        filename: 原始文件名
        max_length: 最大长度限制

    Returns:
        安全的文件名
    """
    # 移除危险字符，保留中文
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # 限制长度
    if len(safe_name) > max_length:
        path = Path(safe_name)
        name, ext = path.stem, path.suffix
        allowed_base = max_length - len(ext)
        if allowed_base > 0:
            safe_name = name[:allowed_base] + ext
        else:
            # 如果扩展名长度大于等于max_length，返回扩展名的最后max_length个字符
            safe_name = ext[-max_length:] if len(ext) >= max_length else safe_name[-max_length:]

    return safe_name


def get_file_hash(file_path: Union[str, Path]) -> str:
    """
    基于文件内容生成MD5哈希值

    Args:
        file_path: 文件路径

    Returns:
        文件内容的MD5哈希值
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_cache_key(file_path: Union[str, Path], prompt: str) -> str:
    """
    生成缓存键

    Args:
        file_path: 文件路径
        prompt: 提示文本

    Returns:
        缓存键
    """
    file_hash = get_file_hash(file_path)
    prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
    return f"{file_hash}_{prompt_hash}"