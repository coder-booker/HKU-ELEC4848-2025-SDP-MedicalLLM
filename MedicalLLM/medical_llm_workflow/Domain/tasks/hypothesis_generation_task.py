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


class HypothesisGenerationTask(Task):
    """假设生成任务，基于问题表示结果生成诊断假设。"""
    
    def get_required_prompt(self) -> str:
        """获取任务所需的提示词模板。"""
        # TODO: 之后可以根据任务类型动态获取
        prompt = '''
You are the “Hypothesis Generation” agent in a clinical reasoning workflow. Based on the previous Problem Representation result, you must propose 3–6 plausible diagnostic/mechanistic hypotheses and provide key supporting and contradicting evidence for each, producing a candidate list for downstream evaluation.
You can find the input patient case and Problem Representation result in previous messages'''
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
