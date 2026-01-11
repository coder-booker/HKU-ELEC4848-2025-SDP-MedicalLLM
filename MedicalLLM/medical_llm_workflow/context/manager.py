"""上下文管理器，负责管理工作流中的对话历史。"""
from typing import List

from ..config import ConversationMessage, WorkflowContext


class ContextManager:
    """上下文管理器，用于管理 WorkflowContext 中的对话历史。"""
    """似乎不太必要"""
    
    @staticmethod
    def prepare_context(
        next_input: str,
    ) -> WorkflowContext:
        pass
    
    
    
    # @staticmethod
    # def add_message_from_task_context(
    #     workflow_context: WorkflowContext,
    #     task_context: TaskContext,
    # ) -> None:
    #     """
    #     向工作流上下文添加一条对话消息。

    #     Args:
    #         context: 工作流上下文
    #         role: 消息角色（"system", "user", "assistant"）
    #         content: 消息内容
    #     """
    #     message = ConversationMessage(role=role, content=content)
    #     context.conversation_history.append(message)


    # @staticmethod
    # def add_message(
    #     context: WorkflowContext,
    #     role: str,
    #     content: str
    # ) -> None:
    #     """
    #     向工作流上下文添加一条对话消息。

    #     Args:
    #         context: 工作流上下文
    #         role: 消息角色（"system", "user", "assistant"）
    #         content: 消息内容
    #     """
    #     message = ConversationMessage(role=role, content=content)
    #     context.conversation_history.append(message)

    # @staticmethod
    # def get_messages(context: WorkflowContext) -> List[ConversationMessage]:
    #     """
    #     获取当前对话历史（返回拷贝）。

    #     Args:
    #         context: 工作流上下文

    #     Returns:
    #         对话消息列表的拷贝
    #     """
    #     return context.conversation_history.copy()

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

