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

    PROMPT_TEMPLATE = '''You are the “Clue Representation” agent in a clinical reasoning workflow. Your job is not to answer the question directly, but to convert the input patient case (in form of medical question) into a structured clinical clue representation for downstream agents.
{{QUESTION}}'''
    
    def get_messages_for_llm_call(
        self,
        workflow_context_port: WorkflowContextPort, # TODO：之后可能可以不通过 workflow_context 传入，而是 TaskConfig 包含或者使用类似单例的方法
    ) -> List[ConversationMessage]:
        """拼接历史输出并附加本阶段提示词。"""
        messages: List[ConversationMessage] = []
        
        # 获取上下文：问题，也就是上一次任务的输出，作为本次任务的输入。
        question_messages = super().get_messages_for_llm_call(workflow_context_port)
        messages.extend(question_messages)
        
        # 获取提示词
        task_prompt = self.prompt
        new_message = ConversationMessage(
            role=ConversationMessageRole.ASSISTANT,
            content=task_prompt,
        )
        messages.append(new_message)

        return messages
