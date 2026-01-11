
from dataclasses import dataclass
from typing import List
from WorkflowEngine import WorkflowContext



@dataclass
class ConversationMessage:
    """单条对话消息"""
    role: str  # "user" / "assistant" / "system"
    content: str



# ============================================================================
# 3. CONTEXT MANAGER (上下文管理)
# ============================================================================

class ContextManager:
    """
    管理 WorkflowContext 中的对话历史。
    目前实现：简单的历史消息拼接（无优化）
    """

    @staticmethod
    def add_message(
        context: WorkflowContext,
        role: str,
        content: str,
    ) -> None:
        """向上下文中添加一条消息"""
        context.conversation_history.append(
            ConversationMessage(role=role, content=content)
        )

    @staticmethod
    def get_messages(context: WorkflowContext) -> List[ConversationMessage]:
        """获取当前上下文的所有消息"""
        return context.conversation_history.copy()

    @staticmethod
    def truncate_history(
        context: WorkflowContext,
        max_messages: int = 20,
    ) -> None:
        """
        截断历史消息，只保留最近的 N 条
        可选实现：保留 system prompt、最近 N-1 条
        """
        if len(context.conversation_history) > max_messages:
            # 保留最后 max_messages 条
            context.conversation_history = context.conversation_history[-max_messages:]