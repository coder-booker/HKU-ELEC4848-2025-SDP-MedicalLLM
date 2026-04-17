"""任务工厂模块。

负责把 `TaskConfig` 映射为具体任务实现，集中管理任务实例化逻辑。
"""
from __future__ import annotations

from typing import Dict, Any, Optional

from medical_llm_workflow.Domain.tasks.base_task import BaseTask
from medical_llm_workflow.Domain.tasks.all_tasks.plain_text_task import PlainTextTask
from medical_llm_workflow.Domain.tasks.all_tasks.evaluation_task import EvaluationTask
from medical_llm_workflow.Domain.tasks.all_tasks.smart_extractor_task import SmartExtractorTask
from medical_llm_workflow.Domain.tasks.models import (
    TaskConfig,
    TaskType,
)


class TaskFactory:
    """根据任务类型/步骤类型创建任务对象。"""

    _task_registry: Dict[TaskType, type[BaseTask]] = {
        TaskType.SINGLE_AGENT: BaseTask,
        TaskType.PLAIN_TEXT: PlainTextTask,
        TaskType.EVALUATION: EvaluationTask,
        TaskType.SMART_EXTRACTOR: SmartExtractorTask,
    }

    @classmethod
    def create(
        cls,
        task_config: TaskConfig,
    ) -> BaseTask:
        """创建任务实例。"""
        # 按通用任务类型分发。
        task_cls = cls._task_registry.get(task_config.type)
        if task_cls is None:
            raise ValueError(f"Unsupported task type: {task_config.type}")

        return task_cls(config=task_config)

    # @classmethod
    # def create_empty_task_config(cls) -> PlainTextTaskConfig:
    #     """创建一个空的占位符任务配置。"""
    #     return PlainTextTaskConfig(
    #         type=TaskType.PLAIN_TEXT,
    #         chatbot_config=PoeChatbotConfig(model=PoeChatbotModel.EMPTY_MODEL),
    #         prompt_template=PromptTemplate(text=""),
    #     )

    # @classmethod
    # def create_plain_task_config(cls, text: str) -> PlainTextTaskConfig:
    #     """创建仅承载文本内容的占位任务配置。"""
    #     return PlainTextTaskConfig(
    #         type=TaskType.PLAIN_TEXT,
    #         chatbot_config=PoeChatbotConfig(model=PoeChatbotModel.EMPTY_MODEL),
    #         prompt_template=PromptTemplate(text=text),
    #     )
