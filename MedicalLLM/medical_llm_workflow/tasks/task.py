"""任务模块，定义可执行的原子任务。"""
from typing import Dict, Any, Optional

from ..api import PoeAPIClient
from ..config import (
    ConversationMessage,
    TaskConfig,
    TaskContext,
    WorkflowContext,
    TaskOutput,
    TaskArtifact,
)
from ..prompts import PromptTemplate, prompt_factory

"""
只负责把输入渲染成提示词，调用 PoeAPIClient，并返回结果。结果怎么编排由工作流引擎负责。
不处理上下文管理，上下文管理交给 ContextManager 和 workflow engine
"""
class Task:
    """原子任务，表示一个可执行的工作流步骤。"""

    def __init__(
        self,
        task_config: TaskConfig,
        poe_client: PoeAPIClient,
        prompt_template: Optional[PromptTemplate] = None,
    ):
        """
        初始化任务。

        Args:
            task_config: 任务配置
            poe_client: Poe API 客户端
            context_manager: 上下文管理器
        """
        self.task_config = task_config
        self.poe_client = poe_client
        self.prompt_template = prompt_template or prompt_factory(task_config.prompt_type_list)

    async def execute(
        self,
        task_artifact: TaskArtifact, # artifact 必须传入而非上层处理好，因为上层不会处理 prompt_template
        workflow_context: WorkflowContext, # 在同一 workflow 优化方法内不需要使用，这里留一个接口方便处理多个 workflow 优化方法的扩展
    ) -> TaskOutput:
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
        # 2. 开始运行
        # 3. 记录结果
        # 4. 返回 （对话记录由外部处理）

        # 根据模板制作提示词
        prompt = self._fill_in_prompt(
            task_artifact
        )
        
        # 判断是否需要其余上下文，但其实未必需要
        # workflow_context
        
        task_output = TaskOutput(
            task_id=self.task_config.task_id,
            input_text=prompt,
            output=None,
            artifact=None,
        )

        # 制作问答 msg
        msg = ConversationMessage(role="user", content=prompt)
        task_output.input_text = prompt

        # 进行问答
        try:
            response = await self.poe_client.call_chatbot(
                [msg], self.task_config.chatbot_config
            )
            task_output.output = response
            task_output.artifact = response # 先简单处理，后续可以更复杂一些
        except Exception as e:
            # 让上层处理异常
            task_output.output = f"Error: {str(e)}"
        
        return task_output
            

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
    def _fill_in_prompt(
        self,
        task_artifact: TaskArtifact
    ) -> str:
        """
        填充用户提示词模板，以制作 message 。

        Args:
            user_input: 用户输入
            variables: 模板变量字典

        Returns:
            渲染后的提示词
        """
        # template = self.task_config.prompt_template.user
        # # 简单的字符串替换
        # try:
        #     # 先替换 input
        #     rendered = template.replace("{input}", user_input)
        #     # 再替换其他变量
        #     for key, value in variables.items():
        #         rendered = rendered.replace(f"{{{key}}}", str(value))
        #     return rendered
        # except Exception as e:
        #     # 如果替换失败，返回原始模板 + 输入
        #     return f"{template}\n\n{user_input}"
    
    # TODO
    def _prepare_artifact(
        self,
        previous_artefact: TaskArtifact,
        task_output: TaskOutput
    ) -> TaskArtifact:
        """
        准备任务产物，供下游任务使用。

        Args:
            task_output: 任务输出

        Returns:
            任务产物
        """
        # # 根据任务类型准备不同的 artifact
        # if self.task_config.task_type == "ordinary":
        #     return TaskArtifact.ORDINARY(CASE=task_output.output or "")
        # elif self.task_config.task_type == "self_refine":
        #     # 这里假设 output 格式为 "INITIAL_ANSWER\nCRITIQUE\nFINAL_ANSWER"
        #     parts = (task_output.output or "").split("\n", 2)
        #     initial_answer = parts[0] if len(parts) > 0 else ""
        #     critique = parts[1] if len(parts) > 1 else ""
        #     final_answer = parts[2] if len(parts) > 2 else ""
        #     return TaskArtifact.SELF_REFINE_THIRD(
        #         CASE=task_output.output or "",
        #         INITIAL_ANSWER=initial_answer,
        #         CRITIQUE=critique,
        #     )
        # else:
        #     raise ValueError(f"Unknown task type: {self.task_config.task_type}")