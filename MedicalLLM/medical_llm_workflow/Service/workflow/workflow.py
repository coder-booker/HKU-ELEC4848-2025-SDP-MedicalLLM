"""工作流编排器。

该模块负责把 `WorkflowConfig` 转换为实际执行流程：
1) 从 benchmark 获取问题；
2) 构建初始问题记录；
3) 依次创建并执行任务；
4) 汇总并打印 benchmark 结果。
"""
from typing import Dict, List
import re

from medical_llm_workflow.Service.workflow.models import WorkflowConfig
from medical_llm_workflow.schemas.models import (
    ConversationMessageStatus,
    ConversationMessage,
    ConversationMessageRole,
)
from medical_llm_workflow.Domain.tasks.models import (
    TaskContext,
    TaskRecord,
    TaskConfig,
    PlainTextTaskConfig,
    EvaluationTaskConfig,
)
from medical_llm_workflow.Domain.prompts.models import PromptTemplate
from medical_llm_workflow.Domain.tasks import TaskFactory
from medical_llm_workflow.Domain.workflow_context import WorkflowContext
from medical_llm_workflow.Domain.benchmark.Dataset import DatasetFactory


class Workflow:
    """医疗推理工作流执行器。"""

    def __init__(
        self,
        config: WorkflowConfig,
    ):
        """保存工作流配置并初始化上下文容器。"""
        self.config = config
        self.workflow_context = WorkflowContext(
            workflow_id=self.config.id,
        )
    
    async def fire(self) -> WorkflowContext:
        '''执行工作流并返回最终上下文。'''
        # Benchmark
        # 解析 dataset 和 evaluator 配置
        benchmark_config = self.config.benchamrk_config
        dataset_config_list = benchmark_config.dataset_list

        benchmark_question_list: List[str] = []
        
        # 解析 dataset。
        # TODO 目前其实只会有一个 dataset
        for dataset_config in dataset_config_list:
            dataset = DatasetFactory.create(dataset_config)
            benchmark_question_list.append(dataset.get_text_questions())
        # 用文本节点接入 benchmark 问题到工作流，之后的任务可以根据需要消费这个问题文本。
        # TODO: 可能可以用 dataset task 来替换这段逻辑，但 dataset 的大文件让整个逻辑有些复杂，可能无法保证性能的情况下分到一个个 task 里去执行
        # TODO: 第一题作为 demo 输入。
        question_text = benchmark_question_list[0][0]
        task_config = PlainTextTaskConfig(
            prompt_template=PromptTemplate(text=question_text),
        )
        self.config.task_config_list.insert(0, task_config)
        
        
        # TO CONTINUE: 解析 evaluator
        evaluator_group_list = benchmark_config.evaluator_group_list
        # TODO 目前其实只会有一个 evaluator group，之后再支持多组 evaluator 的情况
        # 1. 得到每个 evaluator 的要求结构，组合成 prompt
        evaluator_group = evaluator_group_list[0]
        evaluation_task_config = EvaluationTaskConfig(
            evaluator_list=evaluator_group,
        )
        self.config.task_config_list.append(evaluation_task_config)
        
        # BaseTask
        # 根据每个任务配置创建并执行任务，任务内部会把结果写回 workflow_context。任何任务失败都会抛出异常中止流程。
        for task_config in self.config.task_config_list:
            await self._create_and_execute_task(
                task_config=task_config,
                workflow_context=self.workflow_context,
            )
        
        # TODO：这里暂时把打印 benchamrk 结果放在 workflow 里，之后可以考虑更好的设计
        print("Benchmark Results ===")
        for task_record in self.workflow_context.get_all_records():
            # 逐条扫描任务输出，寻找最终答案并做简单正确性判断。
            task_output: List[ConversationMessage] = task_record.task_context.output
            for message in task_output:
                if message.status == ConversationMessageStatus.COMPLETED:
                    print(f"{message.content}")
                    # TODO: 暂时 hard code 为 MedQA 的结果打印，之后需要更通用的设计
                    # 正则表达式提取 Final Answer
                    answer_match = re.search(r"Final Answer:\s*\{([A-Z])\}", message.content)
                    if answer_match:
                        final_answer = answer_match.group(1)
                        print(f"Extracted Final Answer: {final_answer}")
                        if final_answer == 'E': # 第一题正确答案是 E
                            print("The final answer is correct!")
                        else:
                            print("The final answer is incorrect.")
                    else:
                        print("No Final Answer found in the response.")
        
        return self.workflow_context

    async def _create_and_execute_task(
        self,
        task_config: TaskConfig,
        workflow_context: WorkflowContext,
    ) -> TaskContext:
        """根据配置创建任务并执行，失败时抛出异常中断工作流。"""
        task = TaskFactory.create(task_config)
        
        task_record = await task.execute(workflow_context)
        
        for task_output in task_record.task_context.output:
            # 一旦任何任务输出标记为 FAILED，直接中止整个流程。
            if task_output.status == ConversationMessageStatus.FAILED:
                raise Exception(f"Task {task.config.id} failed with error: {task_output.content}") # TODO：之后再详细处理
