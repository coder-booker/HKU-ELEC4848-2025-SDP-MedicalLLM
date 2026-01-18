"""任务模块，定义可执行的原子任务。"""

from medical_llm_workflow.Infrastructure import PoeClient, get_client_instance
from medical_llm_workflow.schemas import (
    ConversationMessage,
    TaskConfig,
    TaskContext,
    TaskRecord,
)
from medical_llm_workflow.Domain.workflow_context import WorkflowContext
# from ..prompts import PromptTemplate, prompt_factory

"""
1. 组装 prompt
2. 调用 Poe API
3. 处理结果，生成 TaskContext 并记录
"""
class Task:
    """原子任务，表示一个可执行的工作流步骤。"""

    def __init__(
        self,
        task_config: TaskConfig,
    ):
        """
        初始化任务。

        Args:
            task_config: 任务配置
            poe_client: Poe API 客户端
            context_manager: 上下文管理器
        """
        self.task_config = task_config
        self.poe_client: PoeClient = get_client_instance()

    async def execute(
        self,
        workflow_context: WorkflowContext, # TODO：之后可能可以不通过 workflow_context 传入，而是 TaskConfig 包含或者使用类似单例的方法
    ) -> TaskRecord:
        """
        执行任务。

        Args:
            workflow_context: 工作流上下文
            task_input: 任务输入文本

        Returns:
            任务上下文，包含执行结果
        """
        # 1. 看下需不需要预处理
        # 2. 制作提示词
        # 3. 开始运行
        # 4. 制作上下文记录
        # 5. 返回记录

        # 制作输入提示词
        prev_task_record = workflow_context.get_previous_task_record(self.task_config.id)
        prev_context = prev_task_record.task_context
        # prompt_template = prompt_factory(self.task_config.type) # TODO：要如何获取合适的 template 呢？不一定需要一个 factory ，原本用 factory 是为了组装 prompt，但现在看来应该可以放在 Task 内进行
        # prompt = self._fill_in_prompt(prompt_template, prev_context)
        prompt = prev_context
        input_msg = ConversationMessage(role="user", content=prompt)

        # 进行问答
        try:
            response = await self.poe_client.call_chatbot(
                [input_msg], self.task_config.chatbot_config
            )
        except Exception as e:
            # 让上层处理异常
            response = ConversationMessage(role="error", content=f"Error: {str(e)}")
        
        context_for_workflow = TaskContext(
            input=[input_msg],
            output=[response],
        )
        
        record = TaskRecord(
            task_config=self.task_config,
            task_context=context_for_workflow,
        )
        
        workflow_context.append_task_record(record)
        
        return record

        # # 更新工作流上下文
        # assistant_msg = ConversationMessage(
        #     role="assistant", content=response
        # )
        # self.context_manager.add_message(
        #     workflow_context, assistant_msg.role, assistant_msg.content
        # )
        # workflow_context.task_results[task_context.task_id] = task_context

        # return task_context

    # TODO
    # def _fill_in_prompt(
    #     self,
    #     prompt_template: PromptTemplate,
    #     context: TaskContext,
    # ) -> str:
    #     """
    #     填充用户提示词模板，以制作 message 。

    #     Args:
    #         user_input: 用户输入
    #         variables: 模板变量字典

    #     Returns:
    #         渲染后的提示词
    #     """
    #     template = self.task_config.prompt_template.user
    #     # 简单的字符串替换
    #     try:
    #         # 先替换 input
    #         rendered = template.replace("{input}", user_input)
    #         # 再替换其他变量
    #         for key, value in variables.items():
    #             rendered = rendered.replace(f"{{{key}}}", str(value))
    #         return rendered
    #     except Exception as e:
    #         # 如果替换失败，返回原始模板 + 输入
    #         return f"{template}\n\n{user_input}"
    
    # TODO
    # def _prepare_artifact(
    #     self,
    #     previous_artefact: TaskArtifact,
    #     task_output: TaskOutput
    # ) -> TaskArtifact:
    #     """
    #     准备任务产物，供下游任务使用。

    #     Args:
    #         task_output: 任务输出

    #     Returns:
    #         任务产物
    #     """
    #     # 根据任务类型准备不同的 artifact
    #     if self.task_config.task_type == "ordinary":
    #         return TaskArtifact.ORDINARY(CASE=task_output.output or "")
    #     elif self.task_config.task_type == "self_refine":
    #         # 这里假设 output 格式为 "INITIAL_ANSWER\nCRITIQUE\nFINAL_ANSWER"
    #         parts = (task_output.output or "").split("\n", 2)
    #         initial_answer = parts[0] if len(parts) > 0 else ""
    #         critique = parts[1] if len(parts) > 1 else ""
    #         final_answer = parts[2] if len(parts) > 2 else ""
    #         return TaskArtifact.SELF_REFINE_THIRD(
    #             CASE=task_output.output or "",
    #             INITIAL_ANSWER=initial_answer,
    #             CRITIQUE=critique,
    #         )
    #     else:
    #         raise ValueError(f"Unknown task type: {self.task_config.task_type}")