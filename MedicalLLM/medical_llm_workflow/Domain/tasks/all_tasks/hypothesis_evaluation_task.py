"""假设评估任务。

该任务负责对候选假设进行比较，映射到选项并给出最终答案。
与基础任务不同的是：成功输出会被标记为 `COMPLETED`。
"""
from typing import List

from ..base_task import BaseTask
from medical_llm_workflow.schemas.models import (
    ConversationMessage,
)
from medical_llm_workflow.Domain.workflow_context.models import (
    WorkflowContextPort,
)


class HypothesisEvaluationTask(BaseTask):
    """假设评估任务，基于假设生成结果生成诊断假设。"""

    PROMPT_TEMPLATE = (
        "You are the “Hypothesis Evaluation” agent in a clinical reasoning workflow. \n"
        "Your job is to compare and evaluate the candidate hypotheses and map them to the provided answer options, then select the final best answer. \n"
        "Make sure that the final answer you output strictly follows the provided answer options text. \n"
        "Problem Representation: \n{{Problem Representation Task}}\n\n"
        "Hypothesis Generation: \n{{Hypothesis Generation Task}}\n"
    )
