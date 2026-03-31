"""SmartExtractor 任务。

该任务通过 evaluator 协议动态生成结构化输出格式，
并调用 LLM 把上游最终推理结果抽取为可评测的标准化字段。
"""

import json
from typing import Dict

from medical_llm_workflow.Domain.benchmark.EvaluatorAdaptor import EvaluatorAdaptor
from medical_llm_workflow.Domain.tasks.base_task import BaseTask
from medical_llm_workflow.Domain.tasks.models import SmartExtractorTaskConfig


class SmartExtractorTask(BaseTask):
    """Evaluator 驱动的结构化抽取任务。"""

    PROMPT_TEMPLATE = (
        "Extract the final answer from the previous assistant response. "
        "Output ONLY valid JSON without markdown and without additional text.\n"
        "Expected JSON schema:\n"
        "{{SCHEMA}}\n"
    )

    def build_prompt(self, args_map: Dict) -> str:
        """根据 evaluator 列表动态构建结构化抽取 prompt。"""
        config: SmartExtractorTaskConfig = self.config
        expected_schema = EvaluatorAdaptor.build_expected_schema(
            config.evaluator_type_list,
        )

        schema_text = json.dumps(
            expected_schema,
            ensure_ascii=False,
            indent=2,
        )

        return super().build_prompt(
            args_map={
                "SCHEMA": schema_text,
            },
        )

    # async def execute(
    #     self,
    #     workflow_context_port: WorkflowContextPort,
    # ) -> TaskRecord:
    #     """执行结构化抽取并把标准化结果写回上下文。"""
    #     config: SmartExtractorTaskConfig = self.config

    #     # 复用 BaseTask 的消息拼装与 LLM 调用链路。
    #     record = await super().execute(workflow_context_port)
        
    #     # 对每个输出消息进行状态检查，确保上游推理成功后才进行抽取，否则直接返回失败状态。
    #     for output in record.task_context.output:
    #         if output.status == ConversationMessageStatus.FAILED:
    #             return record
        
    #     output_message = record.task_context.output[-1]

    #     expected_schema = SmartExtractorFactory.build_expected_schema(
    #         config.evaluator_type_list,
    #     )
    #     extraction_result = SmartExtractorFactory.parse_result(
    #         raw_response=str(output_message.content),
    #         expected_schema=expected_schema,
    #     )

    #     # 直接覆盖为结构化 dict，供 evaluator 与 run 消费。
    #     output_message.content = extraction_result.model_dump()

    #     return record
