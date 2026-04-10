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
    
    def build_prompt(self, workflow_context_port: WorkflowContextPort) -> str:
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
        
        # 执行原本针对 tag 的提取逻辑（如果是通用 task_id 变量也支持替换）
        task_prompt = super().build_prompt(workflow_context_port)
        task_prompt += evaluator_prompt
        
        return task_prompt
