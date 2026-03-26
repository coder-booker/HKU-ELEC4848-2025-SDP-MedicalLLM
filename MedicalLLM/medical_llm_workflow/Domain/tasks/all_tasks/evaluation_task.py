"""测评任务

该任务用于在工作流末端结构化问题答案并执行评测
保持与其他任务一致的输入拼接与执行结构，方便统一编排。
"""
from typing import List, Dict

from ..base_task import BaseTask
from ..models import TaskContext, TaskRecord, EvaluationTaskConfig
from medical_llm_workflow.schemas.models import (
    ConversationMessage,
    ConversationMessageRole,
)
from medical_llm_workflow.Domain.workflow_context.models import (
    WorkflowContextPort,
)


'''You are the “Evaluation” agent in a clinical reasoning workflow.
You should evaluate the previous response quality according to the configured rubric or criteria.
If no explicit rubric is provided, summarize strengths, weaknesses, and actionable improvements.
Output concise, structured evaluation results for downstream use.'''

'''Output the final answer as the following format:
Final Answer: {<your selected answer option letter>}'''


class EvaluationTask(BaseTask):
    """工作流评测任务。"""
    
    def build_prompt(self, args_map):
        config: EvaluationTaskConfig = self.config
        evaluator_list = config.evaluator_list
        # 如果这里必须要实例化了 evaluator 才能拿到 prompt 内容，那 dataset 为什么可以在外部实例化？
    
    def get_messages_for_llm_call(
        self,
        workflow_context_port: WorkflowContextPort,
    ) -> List[ConversationMessage]:
        """拼接历史消息并附加本阶段提示词。"""
        messages: List[ConversationMessage] = []

        # 获取上下文：LLM 的最终答案，也就是上一个任务的输出，作为本次任务的输入。
        llm_answer_messages = super().get_messages_for_llm_call(workflow_context_port)
        messages.extend(llm_answer_messages)
        
        # 获取提示词
        task_prompt = self.prompt
        new_message = ConversationMessage(
            role=ConversationMessageRole.ASSISTANT,
            content=task_prompt,
        )
        messages.append(new_message)

        return messages

    async def execute(
        self,
        workflow_context_port: WorkflowContextPort,
    ) -> TaskRecord:
        """
        执行评估任务，跳过基类执行行为（跳过 llm 运行）。

        Args:
            workflow_context_port: 工作流上下文接口

        Returns:
            任务记录，包含输入消息作为输出
        """
        # steps
        # 1. 获取 LLM 对问题的最终答案，也就是上一个任务的输出。
        final_task_messages = self.get_messages_for_llm_call(workflow_context_port)[0]
        # llm_answer_messages = final_task_record.task_context.output
        llm_answer = llm_answer_messages[0].content # TODO: 先假设第一条就是最终答案，之后需要更健壮的设计
        
        # 2. 叫 LLM 结构化，直接取 prompt 就行
        
        
        # 3. 启动 evaluator 进行评测，得到评测结果。
            # 创建测评器
            # 注入 compareFn
            # 获取评测输入（question, answer, rubric）
            # 生成评测结果
        # 3. 用什么方式放出去？Dict就行
        
        
        # prompt_text = self.config.prompt_template.text if self.config.prompt_template else ""
        # if not prompt_text:
        #     # 返回 fail 状态的 record 以示警告，但不抛异常中断流程。
        #     task_context = TaskContext(
        #         input=[],
        #         output=[ConversationMessage(
        #             role=ConversationMessageRole.ASSISTANT,
        #             content="Error: No question text provided.",
        #             status="FAILED",
        #         )],
        #     )
        #     task_record = TaskRecord(
        #         task_config=self.config,
        #         task_context=task_context,
        #     )
        #     workflow_context_port.append_task_record(task_record)
        #     return task_record
        
        
        # msg = ConversationMessage(
        #     role=ConversationMessageRole.USER,
        #     content=prompt_text,
        # )
        # # 直接使用输入消息作为输出
        # task_context = TaskContext(
        #     input=[],
        #     output=[msg],
        # )

        # task_record = TaskRecord(
        #     task_config=self.config,
        #     task_context=task_context,
        # )
        
        # workflow_context_port.append_task_record(task_record)

        # return task_record