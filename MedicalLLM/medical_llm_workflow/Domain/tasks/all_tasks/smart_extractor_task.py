"""SmartExtractor 任务。

该任务通过 evaluator 协议动态生成结构化输出格式，
并调用 LLM 把上游最终推理结果抽取为可评测的标准化字段。
"""

from typing import List
import json
import re

from medical_llm_workflow.schemas.models import (
    ConversationMessageStatus,
    ConversationMessageRole,
    ConversationMessage,
)
from medical_llm_workflow.Domain.tasks.models import (
    TaskContext,
    TaskRecord,
)
from medical_llm_workflow.Domain.workflow_context.models import (
    WorkflowContextPort,
)
from medical_llm_workflow.Infrastructure import ClientFactory
from medical_llm_workflow.Infrastructure.llm_json_utils import call_llm_with_json_retry
from medical_llm_workflow.utils import emit_event
from medical_llm_workflow.Domain.tasks.base_task import BaseTask
from medical_llm_workflow.Domain.benchmark.EvaluatorAdaptor import EvaluatorAdaptor
from medical_llm_workflow.Domain.tasks import SmartExtractorTaskConfig


class SmartExtractorTask(BaseTask):
    """Evaluator 驱动的结构化抽取任务。"""

    PROMPT_TEMPLATE = (
        "Extract the required information (such as final answer, reasoning process, etc.) from the previous assistant response based on the following JSON schema."
        "Output ONLY valid JSON without markdown and without additional text.\n"
        "Expected JSON schema:\n"
        "{{SCHEMA}}\n"
    )

    def build_prompt(self, *args, **kwargs) -> str:
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
        
        prompt = self.config.prompt_template.text if self.config.prompt_template else self.PROMPT_TEMPLATE
        tags = set(re.findall(r"\{\{([^}]+)\}\}", prompt))
        for tag in tags:
            if tag == "SCHEMA":
                prompt = prompt.replace(f"{{{{{tag}}}}}", schema_text)
            else:
                prompt = prompt.replace(f"{{{{{tag}}}}}", f"[ERROR] Unsupported placeholder {tag} for SmartExtractor")

        return prompt

    async def execute(
        self,
        workflow_context_port: WorkflowContextPort,
    ) -> TaskRecord:
        """执行结构化抽取并把标准化结果写回上下文。如果大模型输出非法 JSON 会自动重试。"""
        config: SmartExtractorTaskConfig = self.config
        messages = self.get_messages_for_llm_call(workflow_context_port)
        
        emit_event(
            "TASK_START",
            {
                "task_id": self.config.id,
                "task_type": self.config.type,
            },
        )
        
        try:
            llm_client = ClientFactory.get_client_instance(self.config.chatbot_config["chatbot_type"])
            
            parsed_data = await call_llm_with_json_retry(
                client=llm_client,
                messages=messages,
                chatbot_config=self.config.chatbot_config,
                max_retries=1,
            )
            
            if "error" in parsed_data:
                # 兜底返回，前端可感知错误并保障进程不崩溃
                res_message: ConversationMessage = {
                    "role": ConversationMessageRole.BOT,
                    "content": f"[JSON_PARSE_ERROR] {parsed_data['error']}",
                    "status": ConversationMessageStatus.FAILED,
                }
            else:
                res_message: ConversationMessage = {
                    "role": ConversationMessageRole.BOT,
                    # 强转为标准的 json 字符串，因为最后还要交给 EvaluatorAdaptor 判断
                    "content": json.dumps(parsed_data, ensure_ascii=False),
                    "status": ConversationMessageStatus.COMPLETED,
                }

        except Exception as e:
            # 同样保持 COMPLETED，通过向内容中写入标记来通知下层 Evaluator
            res_message: ConversationMessage = {
                "role": ConversationMessageRole.BOT,
                "content": f"[ERROR] Unexpected extractor failure: {str(e)}",
                "status": ConversationMessageStatus.COMPLETED,
            }

        context: TaskContext = {
            "input": messages,
            "output": [res_message],
        }

        record: TaskRecord = {
            "task_config": self.config,
            "task_context": context,
        }
        workflow_context_port.append_task_record(record)

        emit_event(
            "TASK_END",
            {
                "task_id": self.config.id,
                "status": res_message["status"],
                "content": res_message["content"],
            },
        )
        
        return record
