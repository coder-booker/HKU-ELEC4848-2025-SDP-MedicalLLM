"""任务模块，定义可执行的原子任务。"""
from typing import List
from .task import Task
from medical_llm_workflow.Infrastructure import PoeClient, get_client_instance
from medical_llm_workflow.schemas import (
    ConversationMessageStatus,
    ConversationMessageRole,
    ConversationMessage,
    TaskConfig,
    TaskContext,
    TaskRecord,
    WorkflowContextPort,
)


class HypothesisEvaluationTask(Task):
    """假设评估任务，基于假设生成结果生成诊断假设。"""
    
    def get_required_prompt(self) -> str:
        """获取任务所需的提示词模板。"""
        # TODO: 之后可以根据任务类型动态获取
        prompt = '''
You are the “Hypothesis Evaluation” agent in a clinical reasoning workflow. Your job is to compare and evaluate the candidate hypotheses and map them to the provided answer options, then select the final best answer.
You can find the input patient case, the Problem Representation result, and Hypothesis Generation result in previous messages
Output the final answer as the following format:
Final Answer: {<your selected answer option letter>}'''
        return prompt
    
    def get_required_messages(
        self,
        workflow_context_port: WorkflowContextPort, # TODO：之后可能可以不通过 workflow_context 传入，而是 TaskConfig 包含或者使用类似单例的方法
    ) -> List[ConversationMessage]:
        """解析任务上下文中的消息列表为 poe 能看懂的 message。"""
        messages: List[ConversationMessage] = []
        
        # 获取上下文
        all_task_record = workflow_context_port.get_all_records() # TODO：先假设所有消息都是单线性且不重复的
        if all_task_record:
            for record in all_task_record: # TODO：先假设所有消息都是单线性且不重复的
                # 编排 prompt 与上下文
                # prompt_template = prompt_factory(self.config.type) # TODO：要如何获取合适的 template 呢？不一定需要一个 factory ，原本用 factory 是为了组装 prompt，但现在看来应该可以放在 Task 内进行
                # prompt = self._fill_in_prompt(prompt_template, prev_context)
                
                for prev_output in record.task_context.output:
                    # TODO：先简单处理，直接用所有此前的输出作为 prompt，之后还得考虑怎么告诉 AI 之前做过什么，
                    #   例如 system prompt 之类的是狗分为一个额外的 message 还是嵌入 user message
                    messages.append(prev_output)
        
        # 制作任务所需的提示词，嵌入到 messages 中
        task_prompt = self.get_required_prompt()
        system_message = ConversationMessage(
            role=ConversationMessageRole.SYSTEM,
            content=task_prompt,
        )
        messages.append(system_message)

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
        messages = self.get_required_messages(workflow_context_port)
            
        # 进行问答
        try:
            # TODO：更好地适配起始的 question
            response = await self.poe_client.call_chatbot(
                messages, self.config.chatbot_config
            )
            res_message = ConversationMessage(
                role=ConversationMessageRole.BOT,
                content=response,
                status=ConversationMessageStatus.COMPLETED, # TODO: 目前假设评估任务成功即为完成
            )
        except Exception as e:
            # 让上层处理异常
            res_message = ConversationMessage(
                role=ConversationMessageRole.BOT,
                content=f"Error: {str(e)}",
                status=ConversationMessageStatus.FAILED,
            )
        
        # 组织输出并保存记录
        context_for_workflow = TaskContext(
            input=messages, # TODO: 应该是把所有之前的消息都传进去，还是只传当前任务的输入消息？都传进去就行，因为 messages 只包含 output，之后可以再仅保存 id 来节省空间
            output=[res_message],
        )
        record = TaskRecord(
            task_config=self.config,
            task_context=context_for_workflow,
        )
        workflow_context_port.append_task_record(record)
        
        return record
