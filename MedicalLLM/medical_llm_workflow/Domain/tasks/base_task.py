"""基础任务抽象实现。

该模块提供默认任务执行流程：
1) 从工作流上下文收集输入消息；
2) 调用 Poe 客户端获取模型输出；
3) 组装 TaskRecord 并写回工作流上下文。
"""
from typing import List, Dict

from medical_llm_workflow.Infrastructure import BaseLLMClient, ClientFactory
from medical_llm_workflow.schemas.models import (
    ConversationMessageStatus,
    ConversationMessageRole,
    ConversationMessage,
)
from medical_llm_workflow.Domain.tasks.models import (
    TaskConfig,
    TaskContext,
    TaskRecord,
)
from medical_llm_workflow.Domain.workflow_context.models import (
    WorkflowContextPort,
)


class BaseTask:
    """原子任务，表示一个可执行的工作流步骤。"""

    PROMPT_TEMPLATE: str = ""

    def __init__(
        self,
        config: TaskConfig,
    ):
        """
        初始化任务。

        Args:
            config: 任务配置
            poe_client: LLM API 客户端
            context_manager: 上下文管理器
        """
        self.config = config
        self.llm_client: BaseLLMClient = ClientFactory.get_client_instance(self.config.chatbot_config.chatbot_type)
        self.prompt = self.build_prompt(
            args_map=self.config.prompt_args_map,
        )
        
    def build_prompt(self, args_map: Dict) -> str:
        """根据任务模板和参数构建 prompt 文本。"""
        # 允许任务配置中直接指定 prompt 模板，也允许使用默认模板。
        prompt = self.config.prompt_template.text if self.config.prompt_template else self.PROMPT_TEMPLATE

        # 通过占位符替换把运行时参数注入到 prompt 模板中。
        for key, value in args_map.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        return prompt
    
    def get_messages_for_llm_call(
        self,
        workflow_context_port: WorkflowContextPort, # TODO：之后可能可以不通过 workflow_context 传入，而是 TaskConfig 包含或者使用类似单例的方法
    ) -> List[ConversationMessage]:
        """收集当前任务所需输入消息。

        基础策略是把上次任务输出当成本任务输入。
        """
        messages: List[ConversationMessage] = []
        
        # 获取上下文
        prev_task_record = workflow_context_port.get_last_task_record() # TODO：先假设所有消息都是单线性且不重复的
        prev_task_output = prev_task_record.task_context.output if prev_task_record else []
        messages.extend(prev_task_output)

        return messages
    
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
        # 先根据工作流状态准备输入消息。
        messages = self.get_messages_for_llm_call(workflow_context_port)
            
        # 进行问答
        try:
            # TODO：更好地适配起始的 question
            # 委托基础设施层与 Poe API 通信。
            response = await self.llm_client.call_chatbot(
                messages,
                self.config.chatbot_config,
            )
            res_message = ConversationMessage(
                role=ConversationMessageRole.ASSISTANT,
                content=response,
                status=ConversationMessageStatus.COMPLETED,
            )
        except Exception as e:
            # 让上层处理异常
            res_message = ConversationMessage(
                role=ConversationMessageRole.ASSISTANT,
                content=f"Error: {str(e)}",
                status=ConversationMessageStatus.FAILED,
            )
        
        # 组织输出并保存记录
        context = TaskContext(
            input=messages, # TODO: 之后可以再仅保存 id 来节省空间
            output=[res_message],
        )
        # 记录 task 配置与其输入输出，便于后续任务消费。
        record = TaskRecord(
            task_config=self.config,
            task_context=context,
        )
        workflow_context_port.append_task_record(record)
        
        return record
