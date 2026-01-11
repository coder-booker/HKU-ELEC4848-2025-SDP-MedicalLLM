from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from Task import Task, TaskConfig, TaskContext, TaskType
from Context import ContextManager, ConversationMessage
from Poe import PoeAPIClient



@dataclass
class WorkflowConfig:
    """整个工作流的配置"""
    workflow_id: str
    name: str
    tasks: List[TaskConfig]  # 任务序列


@dataclass
class WorkflowContext:
    """整个工作流的共享上下文"""
    workflow_id: str
    session_id: str  # 会话ID（用户可指定）
    conversation_history: List[ConversationMessage] = field(default_factory=list)
    task_results: Dict[str, TaskContext] = field(default_factory=dict)  # key: task_id
    metadata: Dict[str, Any] = field(default_factory=dict)  # 其他元数据


# ============================================================================
# 5. ENGINE（工作流执行引擎）
# ============================================================================

class WorkflowEngine:
    """
    工作流执行引擎
    目前支持：单 agent + self-refine 两种任务类型
    """

    def __init__(
        self,
        poe_client: PoeAPIClient,
        context_manager: ContextManager,
    ):
        self.poe_client = poe_client
        self.context_manager = context_manager
        self.tasks: Dict[str, Task] = {}

    def register_task(self, task: Task) -> None:
        """注册任务"""
        self.tasks[task.config.task_id] = task

    async def run_workflow(
        self,
        workflow_config: WorkflowConfig,
        user_input: str,
        workflow_context: Optional[WorkflowContext] = None,
    ) -> WorkflowContext:
        """
        执行完整工作流

        Args:
            workflow_config: 工作流配置
            user_input: 用户输入
            workflow_context: 可选的既有上下文（用于多轮对话）

        Returns:
            完整的工作流上下文（包含所有任务结果）
        """
        # 初始化或使用既有上下文
        if workflow_context is None:
            workflow_context = WorkflowContext(
                workflow_id=workflow_config.workflow_id,
                session_id=workflow_config.workflow_id,  # 简化实现
            )

        # 按顺序执行工作流中的任务
        current_input = user_input
        for task_config in workflow_config.tasks:
            task = Task(task_config, self.poe_client, self.context_manager)

            if task_config.task_type == TaskType.SINGLE_AGENT:
                # 简单的单 agent 调用
                await task.execute(workflow_context, current_input)

            elif task_config.task_type == TaskType.SELF_REFINE:
                # self-refine 工作流：初稿 → 批评 → 改写
                await self._run_self_refine(task, workflow_context, current_input)

            # 可扩展：其他任务类型
            # elif task_config.task_type == TaskType.SELF_CONSISTENCY:
            #     ...

        return workflow_context

    async def _run_self_refine(
        self,
        task: Task,
        workflow_context: WorkflowContext,
        user_input: str,
    ) -> None:
        """
        执行 self-refine 工作流（三步）
        """
        # 步骤 1：生成初稿
        print(f"[Self-Refine] Step 1: Generating initial draft...")
        initial_ctx = await task.execute(workflow_context, user_input)
        initial_answer = initial_ctx.output

        # 步骤 2：生成批评
        print(f"[Self-Refine] Step 2: Generating critique...")
        critique_prompt = f"""
You are an expert reviewer. Please critique the following answer:

**Original Question:** {user_input}

**Initial Answer:** {initial_answer}

**Your Task:** Provide a detailed critique, pointing out:
1. What is good about this answer?
2. What are the main issues or missing points?
3. How could it be improved?
"""
        critique_ctx = TaskContext(
            task_id=f"{task.config.task_id}_critique",
            input_text=critique_prompt,
        )
        messages = self.context_manager.get_messages(workflow_context)
        messages.append(ConversationMessage(role="user", content=critique_prompt))
        critique_output = await self.poe_client.call_chatbot(
            messages, task.config.chatbot_config
        )
        critique_ctx.output = critique_output
        self.context_manager.add_message(workflow_context, "user", critique_prompt)
        self.context_manager.add_message(workflow_context, "assistant", critique_output)

        # 步骤 3：生成改进版答案
        print(f"[Self-Refine] Step 3: Refining answer...")
        refine_prompt = f"""
You just received the following critique:

{critique_output}

Now, please rewrite your answer to address these critiques:

{user_input}
"""
        refine_ctx = TaskContext(
            task_id=f"{task.config.task_id}_refine",
            input_text=refine_prompt,
        )
        messages = self.context_manager.get_messages(workflow_context)
        messages.append(ConversationMessage(role="user", content=refine_prompt))
        refine_output = await self.poe_client.call_chatbot(
            messages, task.config.chatbot_config
        )
        refine_ctx.output = refine_output
        self.context_manager.add_message(workflow_context, "user", refine_prompt)
        self.context_manager.add_message(workflow_context, "assistant", refine_output)

        # 记录各步骤结果
        workflow_context.task_results[f"{task.config.task_id}_draft"] = initial_ctx
        workflow_context.task_results[f"{task.config.task_id}_critique"] = critique_ctx
        workflow_context.task_results[f"{task.config.task_id}_refine"] = refine_ctx

