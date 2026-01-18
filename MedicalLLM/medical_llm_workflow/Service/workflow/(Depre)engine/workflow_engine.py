"""工作流引擎，负责执行工作流配置。"""
from typing import List

from ...config import (
    WorkflowContext,
)
from ...context import ContextManager
from ...tasks import Task


class WorkflowEngine:
    """
    编排 tasks
    上下文管理交给 ContextManager。
    Prompt 渲染交给 Task。
    """

    def __init__(
        self,
    ):
        pass

    async def fire(
        self,
        user_input: str,
        tasks: List[Task],
        workflow_context: WorkflowContext,
        context_manager: ContextManager, # 每个 workflow 都有自己的 context manager
    ) -> None:
        """
        运行工作流。

        Args:
            workflow_config: 工作流配置
            user_input: 用户输入
            workflow_context: 可选的工作流上下文（如果为 None 则创建新的）

        Returns:
            工作流上下文，包含执行结果
        """

        task_artifact = user_input
        # 遍历，解析，执行所有任务
        for task in tasks:
            # 1. 运行 task。传入 artifact 和 workflow_context
            task_output = await task.execute(task_artifact, workflow_context)
            
            # 处理异常
            if task_output.output and task_output.output.startswith("Error:"):
                raise Exception(f"Task {task.task_config.task_id} failed with error: {task_output.output}") # 之后再详细处理
            
            # 3. 记录结果（对话历史，主要是整个 workflow 的）
            context_manager.record_task_output(workflow_context, task_output)
            
            # 4. 传递 artifact 给下一个任务
            task_artifact = task_output.artifact



#     async def _run_self_refine(
#         self,
#         task: Task,
#         workflow_context: WorkflowContext,
#         user_input: str,
#     ) -> None:
#         """
#         执行 self-refine 任务流程。

#         Args:
#             task_config: 任务配置
#             workflow_context: 工作流上下文
#             user_input: 用户输入
#         """
#         print(f"[Self-Refine] Starting task: {task_config.task_id}")

#         # 步骤 1: 生成初稿
#         print("[Self-Refine] Step 1: Generating initial draft...")
#         initial_task = Task(task_config, self.poe_client, self.context_manager)
#         initial_context = await initial_task.execute(workflow_context, user_input)
#         initial_output = initial_context.output

#         # 步骤 2: 生成批评
#         print("[Self-Refine] Step 2: Generating critique...")
#         critique_prompt = f"""Please review and critique the following answer to the medical question.

# Original Question: {user_input}

# Initial Answer:
# {initial_output}

# Please provide constructive criticism, pointing out any inaccuracies, missing information, or areas that need improvement."""

#         critique_task_config = TaskConfig(
#             task_id=f"{task_config.task_id}_critique",
#             task_type=TaskType.SINGLE_AGENT,
#             prompt_template=task_config.prompt_template,
#             chatbot_config=task_config.chatbot_config,
#         )
#         critique_task = Task(
#             critique_task_config, self.poe_client, self.context_manager
#         )
#         critique_context = await critique_task.execute(
#             workflow_context, critique_prompt
#         )
#         critique_output = critique_context.output

#         # 步骤 3: 生成改进版答案
#         print("[Self-Refine] Step 3: Generating refined answer...")
#         refine_prompt = f"""Based on the critique provided, please refine your answer to the original medical question.

# Original Question: {user_input}

# Initial Answer:
# {initial_output}

# Critique:
# {critique_output}

# Please provide an improved answer that addresses the critique."""

#         refine_task_config = TaskConfig(
#             task_id=f"{task_config.task_id}_refined",
#             task_type=TaskType.SINGLE_AGENT,
#             prompt_template=task_config.prompt_template,
#             chatbot_config=task_config.chatbot_config,
#         )
#         refine_task = Task(
#             refine_task_config, self.poe_client, self.context_manager
#         )
#         refine_context = await refine_task.execute(workflow_context, refine_prompt)
#         refine_output = refine_context.output

#         print(f"[Self-Refine] Completed task: {task_config.task_id}")