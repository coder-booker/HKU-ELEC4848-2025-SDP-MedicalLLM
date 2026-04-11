"""问题表征任务。

该任务把原始病例问题转换为结构化临床线索，
为后续“假设生成”提供可消费的中间表示。
"""
from typing import List

from ..base_task import BaseTask
from medical_llm_workflow.schemas.models import (
    ConversationMessageRole,
    ConversationMessage,
)
from medical_llm_workflow.Domain.workflow_context.models import (
    WorkflowContextPort,
)


class ProblemRepresentationTask(BaseTask):
    """问题表示任务，将输入的问题进行适当的格式化和表示。"""

    PROMPT_TEMPLATE = (
        "You are the “Clue Representation” agent in a clinical reasoning workflow.\n"
        "Your job is not to answer the question directly, but to convert the input patient case (in form of medical question) into a clear clinical clue representation for downstream agents.\n\n"
        "Patient Case:\n{{question_task}}\n"
    )
