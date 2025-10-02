"""
调度器基类定义
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional


class SchedulerBase(ABC):
    """调度器抽象基类"""

    def __init__(self):
        """初始化调度器"""
        pass

    @abstractmethod
    def add_job(
        self,
        func: Callable,
        trigger: str,
        job_id: Optional[str] = None,
        **trigger_args
    ) -> None:
        """
        添加定时任务

        Args:
            func: 要执行的函数
            trigger: 触发器类型 (如: 'cron', 'interval', 'date')
            job_id: 任务ID
            **trigger_args: 触发器参数
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """启动调度器"""
        pass

    @abstractmethod
    def shutdown(self, wait: bool = True) -> None:
        """
        关闭调度器

        Args:
            wait: 是否等待所有任务完成
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        检查调度器是否运行中

        Returns:
            是否运行中
        """
        pass


