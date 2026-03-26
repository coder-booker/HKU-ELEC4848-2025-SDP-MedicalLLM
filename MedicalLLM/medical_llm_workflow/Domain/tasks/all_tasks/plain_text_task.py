"""纯文本占位任务。

该任务不调用模型，仅把给定文本包装成 `TaskRecord`，
常用于把 benchmark 问题注入工作流上下文。
"""
from __future__ import annotations
from typing import Dict, Any

from ..base_task import BaseTask
from medical_llm_workflow.schemas.models import (
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


# 占位符 Task，没有实际功能，只有 BaseTask Record 的生成，用于特殊情况的文本指定，例如 initial benchmark input 等
class PlainTextTask(BaseTask):
    """将预置文本写入上下文的轻量任务。"""
    
    async def execute(
        self,
        workflow_context_port: WorkflowContextPort,
    ) -> TaskRecord:
        """
        执行纯文本任务，目的是直接生成 task record 给下游消费，同时跳过基类执行行为（跳过 llm 运行）。

        Args:
            workflow_context_port: 工作流上下文接口

        Returns:
            任务记录，包含输入消息作为输出
        """
        # 使用配置中的 prompt_template.text 作为输出文本。
        prompt_text = self.config.prompt_template.text if self.config.prompt_template else ""
        if not prompt_text:
            # 返回 fail 状态的 record 以示警告，但不抛异常中断流程。
            task_context = TaskContext(
                input=[],
                output=[ConversationMessage(
                    role=ConversationMessageRole.ASSISTANT,
                    content="Error: No question text provided.",
                    status="FAILED",
                )],
            )
            task_record = TaskRecord(
                task_config=self.config,
                task_context=task_context,
            )
            workflow_context_port.append_task_record(task_record)
            return task_record
        
        
        msg = ConversationMessage(
            role=ConversationMessageRole.USER,
            content=prompt_text,
        )
        # 直接使用输入消息作为输出
        task_context = TaskContext(
            input=[],
            output=[msg],
        )

        task_record = TaskRecord(
            task_config=self.config,
            task_context=task_context,
        )
        
        workflow_context_port.append_task_record(task_record)

        return task_record