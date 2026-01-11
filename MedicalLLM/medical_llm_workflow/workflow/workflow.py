"""工作流引擎，负责执行工作流配置。"""
import uuid
from typing import Optional

from ..api import PoeAPIClient
from ..config import (
    TaskConfig,
    TaskContext,
    TaskType,
    WorkflowConfig,
    WorkflowContext,
)
from ..context import ContextManager
from ..tasks import Task


class Workflow:
    """工作流引擎，负责 预处理 和 启动 engine"""

    def __init__(
        self,
        workflow_config: WorkflowConfig,
        poe_client: PoeAPIClient,
        tasks: Optional[list] = None,
    ):
        """
        初始化工作流引擎。
        """
        self.workflow_config = workflow_config
        self.poe_client = poe_client
        self.tasks = tasks or []  # 预加载的任务列表
    
    def preprocess(self):
        """准备工作流引擎，例如预处理任务等。"""
        for task_config in self.workflow_config.task_config_list:
            task = Task(task_config, self.poe_client)
            self.tasks.append(task)

    async def fire_engine(
        self,
        user_input: str,
        workflow_context: Optional[WorkflowContext] = None, # 之后可以看看要不要支持传入已有上下文
    ) -> WorkflowContext:
        # 如果没有提供上下文，创建新的
        if workflow_context is None:
            workflow_context = WorkflowContext(
                workflow_id=workflow_config.workflow_id,
                session_id=str(uuid.uuid4()),
            )

        # 遍历，解析，执行所有任务
        for task_config in workflow_config.tasks:
            if task_config.task_type == TaskType.SINGLE_AGENT:
                # 单 agent 任务：直接执行
                task = Task(task_config, self.poe_client, self.context_manager)
                await task.execute(workflow_context, user_input)

            elif task_config.task_type == TaskType.SELF_REFINE:
                # Self-refine 任务：执行三步流程
                await self._run_self_refine(
                    task_config, workflow_context, user_input
                )

            else:
                # 未知任务类型，跳过或抛出异常
                print(
                    f"Warning: Unknown task type {task_config.task_type} for task {task_config.task_id}"
                )

        return workflow_context
