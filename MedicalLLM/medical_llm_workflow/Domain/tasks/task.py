"""任务模块，定义可执行的原子任务。"""
from typing import List

from medical_llm_workflow.Infrastructure import PoeClient, get_client_instance
from medical_llm_workflow.schemas import (
    ConversationMessageRole,
    ConversationMessage,
    TaskConfig,
    TaskContext,
    TaskRecord,
    WorkflowContextPort,
)


class Task:
    """原子任务，表示一个可执行的工作流步骤。"""

    def __init__(
        self,
        config: TaskConfig,
    ):
        """
        初始化任务。

        Args:
            config: 任务配置
            poe_client: Poe API 客户端
            context_manager: 上下文管理器
        """
        self.config = config
        self.poe_client: PoeClient = get_client_instance()

    async def execute(
        self,
        workflow_context_port: WorkflowContextPort, # TODO：之后可能可以不通过 workflow_context 传入，而是 TaskConfig 包含或者使用类似单例的方法
    ) -> TaskRecord:
        """
        执行任务。
            - 制作输入提示词
            - 访问 api
            - 处理响应，保存为 TaskContext
            - 保存到工作流上下文

        Args:
            workflow_context_port: 工作流上下文接口

        Returns:
            任务上下文，包含执行结果
        """
        messages: List[ConversationMessage] = []
        
        # 获取上下文
        prev_task_record = workflow_context_port.get_previous_task_record(self.config.id)
        if prev_task_record:
            prev_context = prev_task_record.task_context
            # 编排 prompt 与上下文
            # prompt_template = prompt_factory(self.config.type) # TODO：要如何获取合适的 template 呢？不一定需要一个 factory ，原本用 factory 是为了组装 prompt，但现在看来应该可以放在 Task 内进行
            # prompt = self._fill_in_prompt(prompt_template, prev_context)
            
            for prev_output in prev_context.output:
                prompt = prev_output # TODO：先简单处理，直接用上一个任务的输出作为 prompt，之后还得考虑怎么告诉 AI 之前做过什么
                # 组合好，给 chatbot 看
                messages.append(ConversationMessage(role=ConversationMessageRole.USER, content=prompt)) # TODO：system prompt 要怎么处理？分为一个额外的 message 还是嵌入 user message？
            
        # 进行问答
        try:
            response = await self.poe_client.call_chatbot(  # TODO: 我们应该把 message 清洗好再传进去，因为 role 在不同供应商下有不同的规范
                messages, self.config.chatbot_config
            )
            res_message = ConversationMessage(role=ConversationMessageRole.ASSISTANT, content=response)
        except Exception as e:
            # 让上层处理异常
            res_message = ConversationMessage(role=ConversationMessageRole.ERROR, content=f"Error: {str(e)}")
        
        # 组织输出并保存记录
        context_for_workflow = TaskContext(
            input=messages,
            output=[res_message],
        )
        record = TaskRecord(
            task_config=self.config,
            task_context=context_for_workflow,
        )
        workflow_context_port.append_task_record(record)
        
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
    #     template = self.config.prompt_template.user
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
    #     if self.config.task_type == "ordinary":
    #         return TaskArtifact.ORDINARY(CASE=task_output.output or "")
    #     elif self.config.task_type == "self_refine":
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
    #         raise ValueError(f"Unknown task type: {self.config.task_type}")