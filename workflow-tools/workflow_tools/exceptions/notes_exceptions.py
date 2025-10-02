"""
笔记相关异常定义
"""


class NotesClientError(Exception):
    """笔记客户端基础异常"""
    pass


class NotionAPIError(NotesClientError):
    """Notion API异常"""
    pass


class ObsidianError(NotesClientError):
    """Obsidian异常"""
    pass