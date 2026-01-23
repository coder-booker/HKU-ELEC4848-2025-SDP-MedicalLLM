"""工作流引擎，负责执行工作流配置。"""
from typing import Dict, List
import re

from medical_llm_workflow.schemas import (
    WorkflowConfig,
    ConversationMessageStatus,
    TaskContext,
    TaskRecord,
    TaskConfig,
    ConversationMessage,
    ConversationMessageRole,
)
from medical_llm_workflow.Domain.tasks import TaskFactory
from medical_llm_workflow.Domain.workflow_context import WorkflowContext
from medical_llm_workflow.Domain.benchmark.benchmark_manager import BenchmarkManager


class Workflow:

    def __init__(
        self,
        config: WorkflowConfig,
    ):
        self.config = config
        self.context = WorkflowContext(self.config.id)
    
    async def fire(self) -> WorkflowContext:
        # benchamrk
        benchmark_configs = self.config.benchamrk_config_list
        benchmark_questions_map: Dict[str, str] = {}    # 用键值对，方便后续任务调用
        for benchmark_config in benchmark_configs:
            questions = BenchmarkManager.get_text_questions(
                benchmark_id=benchmark_config.id,
                random=benchmark_config.select_random,
                num=benchmark_config.num_of_questions,
            )
            benchmark_questions_map[benchmark_config.id] = questions
        
        # workflow context
        workflow_context = WorkflowContext(
            workflow_id=self.config.id,
        )
        
        # 遍历，解析，执行所有任务
        # TODO: demo 目前只支持单一 benchmark 和单一 question
        question = list(benchmark_questions_map.values())[0][0]
        message = ConversationMessage(
            role=ConversationMessageRole.BOT,
            content=question,
            status=ConversationMessageStatus.NORMAL,
        )
        # 组织输出并保存记录
        plaintext_task_context_for_question = TaskContext(
            input=[],
            output=[message],
        )
        plaintext_task_config_for_question = TaskFactory.create_plain_task_config(text=question)
        record = TaskRecord(
            task_config=plaintext_task_config_for_question,
            task_context=plaintext_task_context_for_question,
        )
        workflow_context.append_task_record(record)
        
        # 执行任务
        for task_config in self.config.task_config_list:
            await self._create_and_execute_task(
                task_config=task_config,
                workflow_context=workflow_context,
            )
        
        # TODO：这里暂时把打印benchamrk结果放在 workflow 里，之后可以考虑更好的设计
        print("Benchmark Results ===")
        for record in workflow_context.get_all_records():
            output: List[ConversationMessage] = record.task_context.output
            for mesagge in output:
                if message.status == ConversationMessageStatus.COMPLETED:
                    print(f"{mesagge.content}")
                    # TODO: 暂时 hard code 为 MedQA 的结果打印，之后需要更通用的设计
                    # 正则表达式提取 Final Answer
                    answer_match = re.search(r"Final Answer:\s*\{([A-Z])\}", mesagge.content)
                    if answer_match:
                        final_answer = answer_match.group(1)
                        print(f"Extracted Final Answer: {final_answer}")
                        if final_answer == 'E': # 第一题正确答案是 E
                            print("The final answer is correct!")
                        else:
                            print("The final answer is incorrect.")
                    else:
                        print("No Final Answer found in the response.")
        
        return workflow_context

    async def _create_and_execute_task(
        self,
        task_config,
        workflow_context: WorkflowContext,
    ) -> TaskContext:
        task = TaskFactory.create_task(task_config)

        task_record = await task.execute(workflow_context)
        
        for task_output in task_record.task_context.output:
            if task_output.status == ConversationMessageStatus.FAILED:
                raise Exception(f"Task {task.config.id} failed with error: {task_output.content}") # TODO：之后再详细处理
