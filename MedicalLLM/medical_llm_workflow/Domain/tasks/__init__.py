"""任务模块，导出 Task。"""
from .task import Task
from .plain_text_task import PlainTextTask, get_placeholder_task_config
from .task_factory import TaskFactory

__all__ = [
    "Task",
    "PlainTextTask",
    "TaskFactory",
]

