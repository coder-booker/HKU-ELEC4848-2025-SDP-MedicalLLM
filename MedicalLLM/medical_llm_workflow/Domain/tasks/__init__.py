"""任务模块，导出 Task。"""

from .models import (
    TaskType,
    TaskContext,
    TaskConfig,
    PlainTextTaskConfig,
    EvaluationTaskConfig,
    SmartExtractorTaskConfig,
    TaskRecord,
)

from .base_task import BaseTask
from .all_tasks.plain_text_task import PlainTextTask
from .all_tasks.evaluation_task import EvaluationTask
from .all_tasks.smart_extractor_task import SmartExtractorTask
from .task_factory import TaskFactory


# 向上层统一暴露可实例化任务与工厂。
__all__ = [
    "TaskType",
    "TaskContext",
    "TaskConfig",
    "PlainTextTaskConfig",
    "EvaluationTaskConfig",
    "SmartExtractorTaskConfig",
    "TaskRecord",
    "BaseTask",
    "PlainTextTask",
    "EvaluationTask",
    "SmartExtractorTask",
    "TaskFactory",
]

