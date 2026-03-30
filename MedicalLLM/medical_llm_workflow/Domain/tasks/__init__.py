"""任务模块，导出 Task。"""
from .base_task import BaseTask
from .all_tasks.plain_text_task import PlainTextTask
from .all_tasks.problem_representation_task import ProblemRepresentationTask
from .all_tasks.hypothesis_generation_task import HypothesisGenerationTask
from .all_tasks.hypothesis_evaluation_task import HypothesisEvaluationTask
from .all_tasks.evaluation_task import EvaluationTask
from .all_tasks.smart_extractor_task import SmartExtractorTask
from .task_factory import TaskFactory
from .models import (
    TaskType,
    MedicalType,
    TaskContext,
    TaskConfig,
    PlainTextTaskConfig,
    EvaluationTaskConfig,
    SmartExtractorTaskConfig,
    TaskRecord,
)


# 向上层统一暴露可实例化任务与工厂。
__all__ = [
    "BaseTask",
    "PlainTextTask",
    "ProblemRepresentationTask",
    "HypothesisGenerationTask",
    "HypothesisEvaluationTask",
    "EvaluationTask",
    "SmartExtractorTask",
    "TaskFactory",
    "TaskType",
    "MedicalType",
    "TaskContext",
    "TaskConfig",
    "PlainTextTaskConfig",
    "SmartExtractorTaskConfig",
    "TaskRecord",
]

