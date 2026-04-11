"""基础任务抽象实现。

该模块提供默认任务执行流程：
1) 从工作流上下文收集输入消息；
2) 调用 Poe 客户端获取模型输出；
3) 组装 TaskRecord 并写回工作流上下文。
"""
from typing import List, Dict
import re

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
from medical_llm_workflow.utils import emit_event


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
        """
        self.config = config
        
    def build_prompt(self, workflow_context_port: WorkflowContextPort) -> str:
        """根据任务模板和运行时上下文获取 prompt 文本。

        自动提取 {{tag}}（即 task_id）并从 workflow context 获取内容进行替换。
        """
        
        # 获取模板文本
        prompt = self.config.prompt_template.text if self.config.prompt_template else self.PROMPT_TEMPLATE

        # 匹配形如 {{task_id}} 的所有 tag（忽略包含额外大括号的情况）
        tags = set(re.findall(r"\{\{([^}]+)\}\}", prompt))
        for tag in tags:
            record = workflow_context_port.get_task_record(tag)
            if record and record["task_context"]["output"]:
                # 获取该任务最后一条回答的内容
                output_content = str(record["task_context"]["output"][-1]["content"])
                prompt = prompt.replace(f"{{{{{tag}}}}}", output_content)

        return prompt
    
    def get_messages_for_llm_call(
        self,
        workflow_context_port: WorkflowContextPort, 
    ) -> List[ConversationMessage]:
        """收集当前任务所需输入消息。

        通过 input_msg_sources 将其指定的上游任务记录直接提取，并按顺序附在最终提示词前。
        注意：这与 Prompt 注入是相互独立的过程。
        """
        messages: List[ConversationMessage] = []
        
        # 1. 遍历 input_msg_sources，将这些 task 的输出消息直接加入列表
        for source_task_id in self.config.input_msg_sources:
            record = workflow_context_port.get_task_record(source_task_id)
            if record and record["task_context"]["output"]:
                # 将该 task 所有的输出作为上文信息插入
                messages.extend(record["task_context"]["output"])
        
        # 2. 构建最后一条带有已替换好上下文字段的提示词
        task_prompt = self.build_prompt(workflow_context_port)
        new_message: ConversationMessage = {
            "role": ConversationMessageRole.USER,
            "content": task_prompt,
            "status": ConversationMessageStatus.NORMAL,
        }
        messages.append(new_message)

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
        # 发出任务开始事件
        emit_event(
            "TASK_START",
            {
                "task_id": self.config.id,
                "task_type": self.config.type,
            },
        )
            
        # 进行问答
        try:
            # 委托基础设施层与 Poe API 通信。
            llm_client = ClientFactory.get_client_instance(self.config.chatbot_config["chatbot_type"])
            response = await llm_client.call_chatbot(
                messages,
                self.config.chatbot_config,
            )

            res_message: ConversationMessage = {
                "role": ConversationMessageRole.USER,
                "content": response,
                "status": ConversationMessageStatus.COMPLETED,
            }
                
        except Exception as e:
            # 让上层处理异常
            res_message: ConversationMessage = {
                "role": ConversationMessageRole.USER,
                "content": f"Error: {str(e)}",
                "status": ConversationMessageStatus.FAILED,
            }
        
        # 组织输出并保存记录
        context: TaskContext = {
            "input": messages, # TODO: 之后可以再仅保存 id 来节省空间
            "output": [res_message],
        }
        # 记录 task 配置与其输入输出，便于后续任务消费。

        record: TaskRecord = {
            "task_config": self.config,
            "task_context": context,
        }
        workflow_context_port.append_task_record(record)
        
        # 发送任务结束事件连同结果返回给前端
        # 这里转换 dict 因为前端不识别 Pydantic 模型，并且需要过滤内部消息内容。
        emit_event(
            "TASK_END",
            {
                "task_id": self.config.id,
                "status": res_message["status"],
                "content": res_message["content"],
            },
        )
        
        return record
