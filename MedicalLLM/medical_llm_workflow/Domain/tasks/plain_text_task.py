
from .task import Task
from medical_llm_workflow.schemas import (
    ConversationMessageRole,
    ConversationMessage,
    TaskContext,
    TaskRecord,
    WorkflowContextPort,
)


# 占位符 Task，没有实际功能，只有 Task Record 的生成，用于特殊情况的文本指定，例如 initial benchmark input 等
class PlainTextTask(Task):
    
    # def __init__(self, text: str):
    #     placeholder_task_config = get_placeholder_task_config(text)
    #     super().__init__(placeholder_task_config)
    
    async def execute(
        self,
        workflow_context_port: WorkflowContextPort,
    ) -> TaskRecord:
        """
        执行纯文本任务，直接生成 Task Record。

        Args:
            workflow_context: 工作流上下文
            input_message: 来自前一个任务的输入消息

        Returns:
            任务记录，包含输入消息作为输出
        """
        msg = ConversationMessage(
            role=ConversationMessageRole.QUESTION,
            content=self.config.prompt_template.text,
        )
        # 直接使用输入消息作为输出
        task_context = TaskContext(
            input=[],
            output=[msg]
        )

        task_record = TaskRecord(
            task_config=self.config,
            task_context=task_context
        )
        
        workflow_context_port.append_task_record(task_record)

        return task_record