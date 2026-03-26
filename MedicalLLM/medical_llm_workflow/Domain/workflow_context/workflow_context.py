"""工作流上下文容器。

该模块维护任务执行历史，并提供查询/追加接口，
供任务执行器在不同步骤之间共享消息与结果。
"""
from typing import List, Dict

from medical_llm_workflow.Domain.tasks.models import TaskRecord
from medical_llm_workflow.Infrastructure import LinkedHashList


class WorkflowContext:
    """上下文管理器，同时提供用于操作对话历史的工具。"""
    
    def __init__(self, workflow_id):
        """初始化工作流上下文与有序历史容器。"""
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
        # 基于链表索引定位指定任务的上一个记录。
        prev_task_context = self.conversation_history.get_prev(task_id)
        return prev_task_context
    
    def last_task_record(self) -> TaskRecord:
        """获取最后一条记录（返回拷贝）。"""
        return self.conversation_history.get_tail()
    
    # def get_all_prev_task_records(self, task_id: str) -> List[TaskRecord]:
    #     """
    #     获取当前对话历史（返回拷贝）。

    #     Args:
    #         context: 工作流上下文

    #     Returns:
    #         对话消息列表的拷贝
    #     """
    #     all_prev_task_contexts = []
    #     all_records: List[TaskRecord] = self.conversation_history.get_all()
    #     for record in all_records:    # TODO：先假设所有消息都是单线性且不重复的
    #         if record.task_config.id == task_id:
    #             break
    #         all_prev_task_contexts.append(record)
    #     return all_prev_task_contexts

    def append_task_record(self, record: TaskRecord) -> None:
        """
        向工作流上下文添加一条对话消息。

        Args:
            context: 工作流上下文
            role: 消息角色
            content: 消息内容
        """
        # 以任务 id 为键写入，既保序也支持 O(1) 索引。
        self.conversation_history.append(record.task_config.id, record)

    def get_task_record(self, task_id: str) -> TaskRecord:
        """按任务 id 获取单条记录。"""
        return self.conversation_history.get(task_id)
    
    def get_all_records(self) -> List[TaskRecord]:
        """按执行顺序返回所有任务记录。"""
        return self.conversation_history.get_all()

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

