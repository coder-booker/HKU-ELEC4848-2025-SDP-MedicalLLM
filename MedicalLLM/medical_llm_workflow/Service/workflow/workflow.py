"""工作流引擎，负责执行工作流配置。"""
from typing import Dict

from os import getcwd
print(getcwd())

from medical_llm_workflow.schemas import WorkflowConfig, ConversationMessageRole, TaskContext
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
        plaintext_task_config_for_question = TaskFactory.create_plain_task_config(text=question)

        self.config.task_config_list.insert(0, plaintext_task_config_for_question)  # # 用 PlainTextTask 把 question 放入工作流上下文
        
        # 执行任务
        for task_config in self.config.task_config_list:
            await self._create_and_execute_task(
                task_config=task_config,
                workflow_context=workflow_context,
            )
            
        return workflow_context

    async def _create_and_execute_task(
        self,
        task_config,
        workflow_context: WorkflowContext,
    ) -> TaskContext:
        task = TaskFactory.create_task(task_config)

        task_record = await task.execute(workflow_context)
        
        for task_output in task_record.task_context.output:
            if task_output.role == ConversationMessageRole.ERROR:
                raise Exception(f"Task {task.config.id} failed with error: {task_output.content}") # TODO：之后再详细处理
