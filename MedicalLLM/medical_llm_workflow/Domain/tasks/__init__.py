"""任务模块，导出 Task。"""
from .task import Task
from .plain_text_task import PlainTextTask
from .problem_representation_task import ProblemRepresentationTask
from .hypothesis_generation_task import HypothesisGenerationTask
from .hypothesis_evaluation_task import HypothesisEvaluationTask
from .task_factory import TaskFactory


__all__ = [
    "Task",
    "PlainTextTask",
    "ProblemRepresentationTask",
    "HypothesisGenerationTask",
    "HypothesisEvaluationTask",
    "TaskFactory",
]

