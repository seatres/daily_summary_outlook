"""
Notion客户端实现
"""

import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

try:
    from notion_client import Client
except ImportError:
    raise ImportError("请安装notion-client: pip install notion-client")

from ..base.notes_base import NotesClientBase, NotesResult
from ...exceptions.notes_exceptions import NotionAPIError
from ...utils.config_manager import ConfigManager


@dataclass
class NotionResult(NotesResult):
    """Notion操作结果"""
    raw_response: Optional[Any] = None


class NotionClient(NotesClientBase):
    """Notion客户端"""

    def __init__(
        self,
        token: Optional[str] = None,
        database_id: Optional[str] = None
    ):
        """
        初始化Notion客户端

        Args:
            token: Notion集成令牌，如果为None则从环境变量获取
            database_id: 默认数据库ID
        """
        super().__init__(token)

        # 获取配置
        if self.token is None:
            self.token = ConfigManager.get_required_env('NOTION_TOKEN')

        if database_id is None:
            database_id = ConfigManager.get_env('NOTION_DATABASE_ID')

        self.database_id = database_id

        # 初始化Notion客户端
        try:
            self.client = Client(auth=self.token)
            self.logger = logging.getLogger(__name__)
            self.logger.info("Notion客户端初始化成功")
        except Exception as e:
            raise NotionAPIError(f"Notion客户端初始化失败: {str(e)}")

    def create_page(
        self,
        title: str,
        content: str,
        pdf_url: Optional[str] = None,
        database_id: Optional[str] = None
    ) -> NotionResult:
        """
        创建页面

        Args:
            title: 页面标题
            content: 页面内容
            pdf_url: PDF文件链接
            database_id: 数据库ID，如果为None则使用默认值

        Returns:
            创建结果
        """
        try:
            # 使用指定的数据库ID或默认值
            target_database_id = database_id or self.database_id
            if not target_database_id:
                return NotionResult(
                    success=False,
                    error="未提供数据库ID，且未设置默认数据库ID"
                )

            # 分割内容为块
            content_blocks = self._split_content_to_blocks(content)

            # 添加PDF链接（如果提供且有效）
            if pdf_url and self._is_valid_url(pdf_url):
                pdf_block = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "PDF文件: "},
                            },
                            {
                                "type": "text",
                                "text": {"content": "link", "link": {"url": pdf_url}}
                            }
                        ]
                    }
                }
                content_blocks.append(pdf_block)

            # 设置页面属性
            # 创建东八区时区对象
            china_tz = timezone(timedelta(hours=8))
            # 获取东八区当前时间
            china_time = datetime.now(china_tz)
            
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
                "Create Time": {"date": {"start": china_time.isoformat()}}
            }

            # 添加PDF链接属性（如果提供且有效）
            if pdf_url and self._is_valid_url(pdf_url):
                properties["PDF Link"] = {"url": pdf_url}

            # 创建页面
            response = self.client.pages.create(
                parent={"database_id": target_database_id},
                properties=properties,
                children=content_blocks
            )

            # 构建页面URL
            page_id = response.get('id', '').replace('-', '')
            page_url = f"https://www.notion.so/{page_id}" if page_id else None

            result = NotionResult(
                success=True,
                page_id=response.get('id'),
                page_url=page_url,
                metadata={
                    'database_id': target_database_id,
                    'title': title,
                    'has_pdf_link': bool(pdf_url and self._is_valid_url(pdf_url))
                },
                raw_response=response
            )

            self.logger.info(f"Notion页面创建成功: {title}")
            return result

        except Exception as e:
            error_msg = f"创建Notion页面失败: {str(e)}"
            self.logger.error(error_msg)
            return NotionResult(success=False, error=error_msg)

    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> NotionResult:
        """
        更新页面

        Args:
            page_id: 页面ID
            title: 新标题
            content: 新内容

        Returns:
            更新结果
        """
        try:
            properties = {}

            # 更新标题
            if title:
                properties["Title"] = {"title": [{"text": {"content": title}}]}

            # 更新页面属性
            if properties:
                self.client.pages.update(page_id=page_id, properties=properties)

            # 更新内容（如果提供）
            if content:
                # 首先删除现有内容 - 使用分页处理所有子块
                start_cursor = None
                while True:
                    # 获取当前页的子块
                    children_response = self.client.blocks.children.list(
                        block_id=page_id,
                        start_cursor=start_cursor,
                        page_size=100
                    )
                    # 删除当前页的所有子块
                    for block in children_response.get('results', []):
                        self.client.blocks.delete(block_id=block['id'])
                    # 检查是否有更多页面
                    if not children_response.get('has_more', False):
                        break
                    # 更新游标获取下一页
                    start_cursor = children_response.get('next_cursor')

                # 添加新内容
                content_blocks = self._split_content_to_blocks(content)
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=content_blocks
                )

            result = NotionResult(
                success=True,
                page_id=page_id,
                metadata={
                    'updated_title': bool(title),
                    'updated_content': bool(content)
                }
            )

            self.logger.info(f"Notion页面更新成功: {page_id}")
            return result

        except Exception as e:
            error_msg = f"更新Notion页面失败: {str(e)}"
            self.logger.error(error_msg)
            return NotionResult(success=False, error=error_msg)

    def get_page(self, page_id: str) -> NotionResult:
        """
        获取页面

        Args:
            page_id: 页面ID

        Returns:
            页面信息
        """
        try:
            # 获取页面属性
            page = self.client.pages.retrieve(page_id=page_id)

            # 获取页面内容
            blocks = self.client.blocks.children.list(block_id=page_id)

            result = NotionResult(
                success=True,
                page_id=page_id,
                metadata={
                    'properties': page.get('properties', {}),
                    'blocks_count': len(blocks.get('results', []))
                },
                raw_response={'page': page, 'blocks': blocks}
            )

            self.logger.info(f"获取Notion页面成功: {page_id}")
            return result

        except Exception as e:
            error_msg = f"获取Notion页面失败: {str(e)}"
            self.logger.error(error_msg)
            return NotionResult(success=False, error=error_msg)

    def _split_content_to_blocks(self, content: str, max_block_size: int = 4000) -> List[Dict[str, Any]]:
        """
        将markdown内容分割为Notion块，支持markdown语法解析，智能控制块数量

        Args:
            content: 原始markdown内容
            max_block_size: 每个块的最大字符数

        Returns:
            Notion块列表（最多100个）
        """
        blocks = []
        lines = content.split('\n')
        current_paragraph = ""
        max_blocks = 95  # Notion限制100，设置安全缓冲区

        # 首先解析所有内容，然后优化块数量
        temp_blocks = []

        for line in lines:
            line = line.strip()

            # 如果是空行，结束当前段落
            if not line:
                if current_paragraph:
                    temp_blocks.extend(self._create_text_blocks(current_paragraph, max_block_size))
                    current_paragraph = ""
                continue

            # 检查是否是markdown特殊语法
            block = self._parse_markdown_line(line)

            if block:
                # 如果有累积的段落，先处理它
                if current_paragraph:
                    temp_blocks.extend(self._create_text_blocks(current_paragraph, max_block_size))
                    current_paragraph = ""

                # 添加特殊块
                temp_blocks.append(block)
            else:
                # 累积到当前段落，但不要让段落过长
                if current_paragraph:
                    # 如果添加这行会让段落过长，先处理当前段落
                    if len(current_paragraph) + len(line) + 1 > max_block_size:
                        temp_blocks.extend(self._create_text_blocks(current_paragraph, max_block_size))
                        current_paragraph = line
                    else:
                        current_paragraph += "\n" + line
                else:
                    current_paragraph = line

        # 处理最后的段落
        if current_paragraph:
            temp_blocks.extend(self._create_text_blocks(current_paragraph, max_block_size))

        # 如果块数超过限制，智能合并段落块
        if len(temp_blocks) > max_blocks:
            blocks = self._compress_blocks(temp_blocks, max_blocks, max_block_size)
        else:
            blocks = temp_blocks

        return blocks

    def _compress_blocks(self, blocks: List[Dict[str, Any]], max_blocks: int, max_block_size: int = 4000) -> List[Dict[str, Any]]:
        """
        智能压缩块列表，优先保留标题和列表，合并段落

        Args:
            blocks: 原始块列表
            max_blocks: 最大块数
            max_block_size: 每个块的最大字符数

        Returns:
            压缩后的块列表
        """
        if len(blocks) <= max_blocks:
            return blocks

        # 分类块：标题、列表、段落
        priority_blocks = []  # 标题和列表
        paragraph_blocks = []  # 段落块

        for block in blocks:
            block_type = block.get('type', '')
            if 'heading' in block_type or 'list_item' in block_type:
                priority_blocks.append(block)
            elif block_type == 'paragraph':
                paragraph_blocks.append(block)

        # 如果优先级块已经超过限制，只保留前max_blocks个
        if len(priority_blocks) >= max_blocks:
            return priority_blocks[:max_blocks]

        # 计算段落块可用空间
        available_for_paragraphs = max_blocks - len(priority_blocks)

        # 如果段落块数量在可用空间内，直接返回
        if len(paragraph_blocks) <= available_for_paragraphs:
            result = []
            # 按原始顺序重新排列
            for block in blocks:
                if block in priority_blocks or block in paragraph_blocks:
                    result.append(block)
            return result

        # 需要合并段落块
        merged_paragraphs = self._merge_paragraph_blocks(paragraph_blocks, available_for_paragraphs, max_block_size)

        # 重新按原始顺序排列所有块
        result = []
        merged_paragraph_added = False

        for block in blocks:
            block_type = block.get('type', '')
            if 'heading' in block_type or 'list_item' in block_type:
                result.append(block)
            elif block_type == 'paragraph' and not merged_paragraph_added:
                # 在第一个段落位置插入所有合并后的段落
                result.extend(merged_paragraphs)
                merged_paragraph_added = True

        return result[:max_blocks]

    def _merge_paragraph_blocks(self, paragraph_blocks: List[Dict[str, Any]], target_count: int, max_block_size: int = 4000) -> List[Dict[str, Any]]:
        """
        合并段落块以减少总数

        Args:
            paragraph_blocks: 段落块列表
            target_count: 目标段落块数量
            max_block_size: 每个块的最大字符数

        Returns:
            合并后的段落块列表
        """
        if len(paragraph_blocks) <= target_count:
            return paragraph_blocks

        if target_count <= 0:
            return []

        # 计算每个合并块应该包含多少个原始块
        blocks_per_merged = len(paragraph_blocks) // target_count
        remainder = len(paragraph_blocks) % target_count

        merged_blocks = []
        current_index = 0

        for i in range(target_count):
            # 确定当前合并块应该包含的块数
            blocks_to_merge = blocks_per_merged
            if i < remainder:
                blocks_to_merge += 1

            # 合并文本内容
            merged_content = []
            for _ in range(blocks_to_merge):
                if current_index < len(paragraph_blocks):
                    block = paragraph_blocks[current_index]
                    # 提取段落内容
                    rich_text = block.get('paragraph', {}).get('rich_text', [])
                    for text_item in rich_text:
                        content = text_item.get('text', {}).get('content', '')
                        if content.strip():
                            merged_content.append(content.strip())
                    current_index += 1

            # 创建合并后的段落块，确保不超过最大块大小
            if merged_content:
                merged_text = '\n\n'.join(merged_content)
                # 使用 _create_text_blocks 方法来处理可能超过最大大小的文本
                text_blocks = self._create_text_blocks(merged_text, max_block_size)
                merged_blocks.extend(text_blocks)

        return merged_blocks

    def _parse_markdown_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        解析markdown行，返回对应的Notion块

        Args:
            line: markdown行

        Returns:
            Notion块，如果不是特殊语法则返回None
        """
        import re

        # 标题语法：# ## ### #### ##### ######
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2)

            # Notion只支持3级标题
            if level <= 3:
                heading_type = f"heading_{level}"
            else:
                heading_type = "heading_3"

            return {
                "object": "block",
                "type": heading_type,
                heading_type: {
                    "rich_text": [{"type": "text", "text": {"content": title}}]
                }
            }

        # 无序列表：* -
        bullet_match = re.match(r'^[\*\-]\s+(.+)$', line)
        if bullet_match:
            text = bullet_match.group(1)
            return {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            }

        # 有序列表：1. 2. 3. 等
        numbered_match = re.match(r'^\d+\.\s+(.+)$', line)
        if numbered_match:
            text = numbered_match.group(1)
            return {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            }

        # 不是特殊语法
        return None

    def _create_text_blocks(self, text: str, max_block_size: int) -> List[Dict[str, Any]]:
        """
        创建文本块，如果文本过长则分割

        Args:
            text: 文本内容
            max_block_size: 最大块大小

        Returns:
            文本块列表
        """
        if len(text) <= max_block_size:
            return [self._create_paragraph_block(text)]

        # 文本过长，需要分割
        blocks = []
        for i in range(0, len(text), max_block_size):
            chunk = text[i:i + max_block_size]
            blocks.append(self._create_paragraph_block(chunk))

        return blocks

    def _create_paragraph_block(self, text: str) -> Dict[str, Any]:
        """创建段落块"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }

    def _is_valid_url(self, url: str) -> bool:
        """检查URL是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    @staticmethod
    def validate_notion_config() -> 'NotionValidationResult':
        """
        验证Notion配置是否正确

        Returns:
            NotionValidationResult: 验证结果
        """

        @dataclass
        class NotionValidationResult:
            is_valid: bool
            token_exists: bool
            database_id_exists: bool
            can_initialize: bool
            can_connect: bool
            can_access_database: bool
            errors: List[str]
            warnings: List[str]

        errors = []
        warnings = []

        # 1. 检查Token是否存在
        token = ConfigManager.get_env('NOTION_TOKEN')
        token_exists = token is not None and token.strip() != ""

        if not token_exists:
            errors.append("NOTION_TOKEN环境变量未设置或为空")
            return NotionValidationResult(
                is_valid=False,
                token_exists=False,
                database_id_exists=False,
                can_initialize=False,
                can_connect=False,
                can_access_database=False,
                errors=errors,
                warnings=warnings
            )

        # 2. 检查Database ID是否存在
        database_id = ConfigManager.get_env('NOTION_DATABASE_ID')
        database_id_exists = database_id is not None and database_id.strip() != ""

        if not database_id_exists:
            warnings.append("NOTION_DATABASE_ID环境变量未设置，部分功能可能受限")

        # 3. 测试客户端初始化
        can_initialize = False
        can_connect = False
        can_access_database = False

        try:
            print(f"      🔄 正在初始化Notion客户端...")
            client = Client(auth=token.strip())
            can_initialize = True
            print(f"      ✅ Notion客户端初始化成功")

            # 4. 测试API连接
            try:
                print(f"      🔄 正在测试Notion API连接...")
                # 获取当前用户信息来测试连接
                user_info = client.users.me()
                if user_info:
                    can_connect = True
                    print(f"      ✅ Notion API连接成功，用户: {user_info.get('name', 'Unknown')}")
                else:
                    warnings.append("API连接成功但用户信息为空")

                # 5. 测试数据库访问（如果提供了Database ID）
                if database_id_exists:
                    try:
                        print(f"      🔄 正在测试数据库访问权限...")
                        database_info = client.databases.retrieve(database_id.strip())
                        if database_info:
                            can_access_database = True
                            db_title = ""
                            if 'title' in database_info and database_info['title']:
                                db_title = database_info['title'][0]['text']['content'] if database_info['title'][0]['text'] else "未命名数据库"
                            print(f"      ✅ 数据库访问成功，数据库: {db_title}")
                        else:
                            warnings.append("数据库访问返回空结果")
                    except Exception as e:
                        errors.append(f"数据库访问失败: {str(e)}")
                        print(f"      ❌ 数据库访问失败: {str(e)}")

            except Exception as e:
                errors.append(f"Notion API连接测试失败: {str(e)}")
                print(f"      ❌ Notion API连接测试失败: {str(e)}")

        except Exception as e:
            errors.append(f"Notion客户端初始化失败: {str(e)}")
            print(f"      ❌ Notion客户端初始化失败: {str(e)}")

        # 6. 综合验证结果
        is_valid = (
            token_exists and
            can_initialize and
            can_connect and
            (can_access_database if database_id_exists else True)
        )

        return NotionValidationResult(
            is_valid=is_valid,
            token_exists=token_exists,
            database_id_exists=database_id_exists,
            can_initialize=can_initialize,
            can_connect=can_connect,
            can_access_database=can_access_database,
            errors=errors,
            warnings=warnings
        )