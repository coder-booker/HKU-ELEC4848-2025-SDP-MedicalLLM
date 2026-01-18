"""工作流引擎，负责执行工作流配置。"""
import uuid

from medical_llm_workflow.schemas import WorkflowConfig, ConversationMessageRole, TaskContext
from medical_llm_workflow.Domain.tasks import Task
from medical_llm_workflow.Domain.workflow_context import WorkflowContext


class Workflow:

    def __init__(
        self,
        config: WorkflowConfig,
    ):
        self.config = config
        self.context = WorkflowContext(self.config.id)
    
    async def fire(self) -> WorkflowContext:
        workflow_context = WorkflowContext(
            workflow_id=self.config.id,
        )

        # 遍历，解析，执行所有任务
        for task_config in self.config.task_config_list:
            task = Task(task_config)

            task_record = await task.execute(workflow_context)

            task_output = task_record.task_context.output
            if task_output[0].role == ConversationMessageRole.ERROR:
                raise Exception(f"Task {task.task_config.task_id} failed with error: {task_output[0].content}") # 之后再详细处理


        return workflow_context
