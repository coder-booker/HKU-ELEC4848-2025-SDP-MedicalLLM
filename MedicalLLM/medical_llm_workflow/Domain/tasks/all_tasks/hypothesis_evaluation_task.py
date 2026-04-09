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
        "You are the “Hypothesis Evaluation” agent in a clinical reasoning workflow. "
        "Your job is to compare and evaluate the candidate hypotheses and map them to the provided answer options, then select the final best answer. "
        "Make sure that the final answer you output strictly follows the provided answer options text. "
        # "Option tag should be ignored in the final answer. "
        "You can find the Problem Representation result and Hypothesis Generation result in previous messages. "
    )
    
    def get_messages_for_llm_call(
        self,
        workflow_context_port: WorkflowContextPort,
    ) -> List[ConversationMessage]:
        """拼接历史消息并附加本阶段提示词。"""
        messages: List[ConversationMessage] = []

        # 获得问题表述和假设生成的消息，作为评估阶段的输入。
        messages = super().get_messages_for_llm_call(workflow_context_port) # 这里会返回 上一次输出（假设生成） + prompt
        all_records = workflow_context_port.get_all_records()
        question_representation_messages = all_records[-2]["task_context"]['output'][0] # TODO: 这里必须 hardcode 先, 包括[-2]和['output'][0]
        messages.insert(0, question_representation_messages)

        return messages
