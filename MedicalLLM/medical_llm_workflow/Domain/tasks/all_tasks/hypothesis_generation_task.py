"""假设生成任务。

该任务基于问题表征结果，生成候选诊断/机制假设，
并输出支持与反证信息，供后续评估阶段筛选。
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


class HypothesisGenerationTask(BaseTask):
    """假设生成任务，基于问题表示结果生成诊断假设。"""

    PROMPT_TEMPLATE = '''You are the “Hypothesis Generation” agent in a clinical reasoning workflow. Based on the previous Problem Representation result, you must propose 3–6 plausible diagnostic/mechanistic hypotheses and provide key supporting and contradicting evidence for each, producing a candidate list for downstream evaluation.
You can find the input patient case and Problem Representation result in previous messages'''
    
    def get_messages_for_llm_call(
        self,
        workflow_context_port: WorkflowContextPort, # TODO：之后可能可以不通过 workflow_context 传入，而是 TaskConfig 包含或者使用类似单例的方法
    ) -> List[ConversationMessage]:
        """拼接历史消息并附加本阶段提示词。"""
        messages: List[ConversationMessage] = []

        # 获取上下文：问题表述，也就是上一次任务的输出，作为本次任务的输入。
        question_representation_messages = super().get_messages_for_llm_call(workflow_context_port)
        messages.extend(question_representation_messages)
        
        # 获取提示词
        task_prompt = self.prompt
        new_message = ConversationMessage(
            role=ConversationMessageRole.ASSISTANT,
            content=task_prompt,
        )
        messages.append(new_message)

        return messages
