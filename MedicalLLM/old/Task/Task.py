from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
from Prompt import PromptTemplate
from Poe import PoeAPIClient, PoeChatbotConfig
from Context import ContextManager, ConversationMessage
from WorkflowEngine import WorkflowContext


class TaskType(Enum):
    """枚举：任务类型"""
    SINGLE_AGENT = "single_agent"
    SELF_REFINE = "self_refine"
    SELF_CONSISTENCY = "self_consistency"
    MULTI_AGENT = "multi_agent"

@dataclass
class TaskConfig:
    """单个任务的配置"""
    task_id: str
    task_type: TaskType
    prompt_template: PromptTemplate
    chatbot_config: PoeChatbotConfig
    # 可扩展字段
    max_retries: int = 3
    timeout: int = 60
    
@dataclass
class TaskContext:
    """单个任务执行时的上下文"""
    task_id: str
    input_text: str  # 当前任务的输入
    variables: Dict[str, Any] = field(default_factory=dict)  # 模板变量
    output: Optional[str] = None  # 任务输出结果


# ============================================================================
# 4. TASK（单个任务的执行）
# ============================================================================

class Task:
    """
    代表工作流中的单个原子任务
    """

    def __init__(
        self,
        config: TaskConfig,
        poe_client: PoeAPIClient,
        context_manager: ContextManager,
    ):
        self.config = config
        self.poe_client = poe_client
        self.context_manager = context_manager

    async def execute(
        self,
        workflow_context: WorkflowContext,
        task_input: str,
    ) -> TaskContext:
        """
        执行任务

        Args:
            workflow_context: 工作流全局上下文
            task_input: 当前任务的输入文本

        Returns:
            TaskContext，包含输入和输出
        """
        task_ctx = TaskContext(task_id=self.config.task_id, input_text=task_input)

        # 1. 渲染 prompt 模板
        rendered_prompt = self._render_prompt(task_input, task_ctx.variables)

        # 2. 准备消息（历史 + 新消息）
        messages = self.context_manager.get_messages(workflow_context)
        messages.append(ConversationMessage(role="user", content=rendered_prompt))

        # 3. 调用 Poe
        output = await self.poe_client.call_chatbot(messages, self.config.chatbot_config)
        task_ctx.output = output

        # 4. 更新工作流上下文（历史 + 本轮对话）
        self.context_manager.add_message(workflow_context, "user", rendered_prompt)
        self.context_manager.add_message(workflow_context, "assistant", output)

        # 5. 记录该任务的结果
        workflow_context.task_results[self.config.task_id] = task_ctx

        return task_ctx

    def _render_prompt(self, user_input: str, variables: Dict[str, Any]) -> str:
        """
        渲染 prompt 模板（简单实现，可扩展）
        """
        prompt = self.config.prompt_template.user
        # 替换模板变量
        prompt = prompt.format(input=user_input, **variables)
        return prompt