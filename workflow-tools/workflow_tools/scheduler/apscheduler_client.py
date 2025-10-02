"""
APScheduler调度器实现
适合Docker容器环境，支持Cron表达式
"""

import logging
from typing import Callable, Optional

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.date import DateTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

from .base.scheduler_base import SchedulerBase


class APSchedulerClient(SchedulerBase):
    """
    APScheduler调度器客户端
    
    适用于Docker容器环境，程序常驻运行
    支持Cron表达式、间隔触发、单次触发等多种方式
    """

    def __init__(self, timezone: str = "Asia/Shanghai"):
        """
        初始化APScheduler客户端

        Args:
            timezone: 时区设置，默认为东八区 (Asia/Shanghai)
        """
        super().__init__()

        if not APSCHEDULER_AVAILABLE:
            raise ImportError("请安装APScheduler: pip install apscheduler")

        self.scheduler = BackgroundScheduler(timezone=timezone)
        self.logger = logging.getLogger(__name__)

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
            trigger: 触发器类型 ('cron', 'interval', 'date')
            job_id: 任务ID
            **trigger_args: 触发器参数
                - cron触发器: hour, minute, second, day, month, day_of_week等
                - interval触发器: weeks, days, hours, minutes, seconds
                - date触发器: run_date

        示例:
            # 每天22点执行
            scheduler.add_job(my_func, 'cron', hour=22, minute=0)
            
            # 每隔1小时执行
            scheduler.add_job(my_func, 'interval', hours=1)
            
            # 指定时间执行一次
            scheduler.add_job(my_func, 'date', run_date='2025-10-01 22:00:00')
        """
        try:
            if trigger == 'cron':
                trigger_obj = CronTrigger(**trigger_args, timezone=self.scheduler.timezone)
            elif trigger == 'interval':
                trigger_obj = IntervalTrigger(**trigger_args, timezone=self.scheduler.timezone)
            elif trigger == 'date':
                trigger_obj = DateTrigger(**trigger_args, timezone=self.scheduler.timezone)
            else:
                raise ValueError(f"不支持的触发器类型: {trigger}")

            self.scheduler.add_job(
                func,
                trigger=trigger_obj,
                id=job_id,
                replace_existing=True
            )

            self.logger.info(f"成功添加任务: {job_id or func.__name__} (触发器: {trigger})")

        except Exception as e:
            self.logger.error(f"添加任务失败: {str(e)}")
            raise

    def start(self) -> None:
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("调度器已启动")
        else:
            self.logger.warning("调度器已经在运行中")

    def shutdown(self, wait: bool = True) -> None:
        """
        关闭调度器

        Args:
            wait: 是否等待所有任务完成
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            self.logger.info("调度器已关闭")
        else:
            self.logger.warning("调度器未运行")

    def is_running(self) -> bool:
        """
        检查调度器是否运行中

        Returns:
            是否运行中
        """
        return self.scheduler.running

    def get_jobs(self):
        """
        获取所有任务列表

        Returns:
            任务列表
        """
        return self.scheduler.get_jobs()

    def remove_job(self, job_id: str) -> None:
        """
        移除指定任务

        Args:
            job_id: 任务ID
        """
        try:
            self.scheduler.remove_job(job_id)
            self.logger.info(f"已移除任务: {job_id}")
        except Exception as e:
            self.logger.error(f"移除任务失败: {str(e)}")
            raise


