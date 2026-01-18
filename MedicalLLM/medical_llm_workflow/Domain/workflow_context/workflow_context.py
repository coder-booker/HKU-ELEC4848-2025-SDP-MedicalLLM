"""上下文管理器，负责管理工作流中的对话历史。"""
from typing import List, Dict

from medical_llm_workflow.schemas import TaskContext, TaskRecord
from medical_llm_workflow.Infrastructure import LinkedHashList



class WorkflowContext:
    """上下文管理器，同时提供用于操作对话历史的工具。"""
    
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.conversation_history = LinkedHashList()

    def get_previous_task_record(self, task_id: str) -> TaskRecord:
        """
        获取当前对话历史（返回拷贝）。

        Args:
            context: 工作流上下文

        Returns:
            对话消息列表的拷贝
        """
        prev_task_context = self.conversation_history.get_prev(task_id)
        return prev_task_context

    def append_task_record(self, record: TaskRecord) -> None:
        """
        向工作流上下文添加一条对话消息。

        Args:
            context: 工作流上下文
            role: 消息角色（"system", "user", "assistant"）
            content: 消息内容
        """
        self.conversation_history.append(record.task_config.id, record)

    def get_task_record(self, task_id: str) -> TaskRecord:
        return self.conversation_history.get(task_id)
    
    def get_all_records(self) -> List[TaskRecord]:
        return self.conversation_history.values()

    # @staticmethod
    # def truncate_history(
    #     context: WorkflowContext, max_messages: int = 20
    # ) -> None:
    #     """
    #     截断对话历史，只保留最近的 N 条消息。

    #     Args:
    #         context: 工作流上下文
    #         max_messages: 保留的最大消息数量
    #     """
    #     if len(context.conversation_history) > max_messages:
    #         context.conversation_history = context.conversation_history[
    #             -max_messages:
    #         ]

