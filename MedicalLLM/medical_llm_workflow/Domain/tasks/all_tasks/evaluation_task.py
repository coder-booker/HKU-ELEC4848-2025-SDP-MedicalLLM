"""测评任务

该任务用于在工作流末端结构化问题答案并执行评测
保持与其他任务一致的输入拼接与执行结构，方便统一编排。
"""
from typing import Dict
import json

from ..base_task import BaseTask
from ..models import EvaluationTaskConfig, TaskContext, TaskRecord
from medical_llm_workflow.schemas.models import (
    ConversationMessage,
    ConversationMessageRole,
    ConversationMessageStatus,
)
from medical_llm_workflow.Domain.workflow_context.models import (
    WorkflowContextPort,
)
from medical_llm_workflow.Domain.benchmark.Evaluator.evaluator_factory import EvaluatorFactory


'''You are the “Evaluation” agent in a clinical reasoning workflow.
You should evaluate the previous response quality according to the configured rubric or criteria.
If no explicit rubric is provided, summarize strengths, weaknesses, and actionable improvements.
Output concise, structured evaluation results for downstream use.'''




class EvaluationTask(BaseTask):
    """工作流评测任务。"""
    PROMPT_TEMPLATE = '''Output the final answer as the following JSON format. Do not output any other text outside the JSON format.:
'''
    
    def build_prompt(self) -> str:
        """构建 evaluator 的结构化输出提示词。"""
        config: EvaluationTaskConfig = self.config
        evaluator_type_list = config.evaluator_type_list
        evaluator_prompt_structure = {}
        for evaluator_type in evaluator_type_list:
            # 获取评测器的结构化输出提示词
            evaluator_prompt_structure |= EvaluatorFactory.get_evaluator_llm_protocol(evaluator_type)
        
        # jsonify
        evaluator_prompt = json.dumps(
            evaluator_prompt_structure,
            ensure_ascii=False,  # 保留中文，不转 \uXXXX
            indent=2,            # 美化缩进
        )
        
        # build_prompt 在 __init__ 阶段调用，此时 self.prompt 尚未赋值。
        task_prompt = self.PROMPT_TEMPLATE
        task_prompt += evaluator_prompt 
        
        return task_prompt

    # async def execute(
    #     self,
    #     workflow_context_port: WorkflowContextPort,
    # ) -> TaskRecord:
    #     """
    #     执行评估任务，跳过基类执行行为（跳过 llm 运行）。

    #     Args:
    #         workflow_context_port: 工作流上下文接口

    #     Returns:
    #         任务记录，包含输入消息作为输出
    #     """
    #     # steps
    #     # 1. 获取 LLM 对问题的最终答案，也就是上一个任务的输出。
    #     messages = self.get_messages_for_llm_call(workflow_context_port)
        
    #     # 2. 叫 LLM 结构化，直接取 prompt 就行
        
        
    #     # 3. 启动 evaluator 进行评测，得到评测结果。
    #         # 创建测评器
    #         # 注入 compareFn
    #         # 获取评测输入（question, answer, rubric）
    #         # 生成评测结果
    #     # 3. 用什么方式放出去？Dict就行
        
    #     # 进行问答
    #     try:
    #         # TODO：更好地适配起始的 question
    #         # 委托基础设施层与 Poe API 通信。
    #         response = await self.llm_client.call_chatbot(
    #             messages,
    #             self.config.chatbot_config,
    #         )
    #         res_message = ConversationMessage(
    #             role=ConversationMessageRole.USER,
    #             content=response,
    #             status=ConversationMessageStatus.COMPLETED,
    #         )
    #     except Exception as e:
    #         # 让上层处理异常
    #         res_message = ConversationMessage(
    #             role=ConversationMessageRole.USER,
    #             content=f"Error: {str(e)}",
    #             status=ConversationMessageStatus.FAILED,
    #         )
        
    #     # 组织输出并保存记录
    #     context = TaskContext(
    #         input=messages, # TODO: 之后可以再仅保存 id 来节省空间
    #         output=[res_message],
    #     )
    #     # 记录 task 配置与其输入输出，便于后续任务消费。
    #     record = TaskRecord(
    #         task_config=self.config,
    #         task_context=context,
    #     )
    #     workflow_context_port.append_task_record(record)
        
    #     return record