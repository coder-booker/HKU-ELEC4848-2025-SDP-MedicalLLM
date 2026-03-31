"""工作流编排器。

该模块负责把 `WorkflowConfig` 转换为实际执行流程：
1) 从 benchmark 获取问题；
2) 构建初始问题记录；
3) 依次创建并执行任务；
4) 汇总并打印 benchmark 结果。
"""
from typing import Any, Dict, List
import uuid

from pydantic import BaseModel, Field

from medical_llm_workflow.schemas.models import (
    ConversationMessageStatus,
)
from medical_llm_workflow.Domain.tasks.models import (
    PlainTextTaskConfig,
    SmartExtractorTaskConfig,
    TaskConfig,
)
from medical_llm_workflow.Domain.prompts.models import PromptTemplate
from medical_llm_workflow.Domain.tasks import TaskFactory
from medical_llm_workflow.Domain.workflow_context import WorkflowContext
from medical_llm_workflow.Domain.benchmark.Dataset import DatasetFactory
from medical_llm_workflow.Domain.benchmark.Evaluator import (
    EvaluationSample,
    EvaluatorFactory,
)
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType
from medical_llm_workflow.Domain.benchmark.Dataset.models import DatasetConfig, DatasetType
from medical_llm_workflow.Domain.benchmark.EvaluatorAdaptor.evaluator_adaptor import EvaluatorAdaptor


class DatasetInletItem(BaseModel):
    """
    - dataset_type: DatasetType - 数据集类型，供后续 evaluator 识别题目格式
    - text_question: str - 传给工作流的文本题目
    - json_question: Dict[str, Any] - 传给 evaluator 的结构化题目
    """

    dataset_type: DatasetType
    text_question: str
    json_question: Dict[str, Any]


class Workflow:
    """工作流执行器。"""

    def __init__(
        self,
        id: uuid.UUID = Field(default_factory=uuid.uuid4),
        name: str = "Default Workflow Name",
        task_config_list: List[TaskConfig] = Field(default_factory=list),
        dataset_config_list: List[DatasetConfig] = Field(default_factory=list),
        evaluator_type_list: List[EvaluatorType] = Field(default_factory=list),
        # language: LanguageType = LanguageType.EN # 整条工作流的语言
    ):
        """保存工作流配置并初始化上下文容器。"""
        self.id = id
        self.name = name

        # 避免外部列表引用导致运行中被意外修改。
        self.task_config_list = list(task_config_list)
        self.dataset_config_list = list(dataset_config_list)
        self.evaluator_type_list = list(evaluator_type_list)

        self.workflow_context = WorkflowContext(
            workflow_id=self.id,
        )

        # self.dataset_inlet: = None
        self.core_tasks: List[TaskConfig] = []
        self.output_tasks = None

    def init_dataset_inlet(self) -> List[DatasetInletItem]:
        """
        初始化 dataset 入口。

        Returns:
            每个元素包含：
            - question_text: 传给工作流的文本题目
            - question_payload: 传给 evaluator 的结构化题目
        """
        if not self.dataset_config_list:
            raise ValueError("dataset_config_list is empty, cannot initialize dataset inlet.")

        dataset_inlet_item_list: List[DatasetInletItem] = []

        # 目前支持多个 dataset，结果直接按顺序展开。
        for dataset_config in self.dataset_config_list:
            dataset = DatasetFactory.create(dataset_config)
            text_selected_formatted_questions = dataset.get_text_selected_formatted_questions()
            selected_formatted_questions = dataset.get_selected_formatted_questions()

            for i in range(dataset.num_of_questions):
                text_formatted_question = text_selected_formatted_questions[i]
                formatted_question = selected_formatted_questions[i]

                dataset_inlet_item_list.append(
                    DatasetInletItem(
                        dataset_type=dataset_config.dataset_type,
                        text_question=text_formatted_question,
                        json_question=formatted_question,
                    ),
                )

        return dataset_inlet_item_list

    def init_extractor(self) -> SmartExtractorTaskConfig:
        """初始化 SmartExtractor 任务配置。"""
        extractor_chatbot_config = None

        # extractor 本身也要调用 LLM，因此复用主任务链中的任一可用 chatbot_config。
        for task_config in self.task_config_list:
            if getattr(task_config, "chatbot_config", None) is not None:
                extractor_chatbot_config = task_config.chatbot_config
                break

        extractor_task_config = SmartExtractorTaskConfig(
            chatbot_config=extractor_chatbot_config,
            evaluator_type_list=self.evaluator_type_list.copy(),
        )

        return extractor_task_config

    def init_evaluator(
        self,
        all_workflow_contexts: List[WorkflowContext],
        dataset_inlet_item_list: List[DatasetInletItem],
    ) -> Dict[str, Any]:
        """执行全部 evaluator，并在最后融合输出一份统一报告。"""
        print("=== Evaluation Results ===")
        evaluation_schema = EvaluatorAdaptor.build_expected_schema(self.evaluator_type_list)

        evaluation_sample_list: List[EvaluationSample] = []
        # 从 extractor 的结构化输出读取 prediction，再组评测样本。
        for index, workflow_context in enumerate(all_workflow_contexts):
            # 收集 dataset 的结构化题目并适配到当前 evaluator 需要的格式
            dataset_inlet_item = dataset_inlet_item_list[index]
            dataset_ground_truth_dict = EvaluatorAdaptor.parse_dataset_question_to_evaluator_schema(
                dataset_type=dataset_inlet_item.dataset_type,
                dataset_json_question=dataset_inlet_item.json_question,
                evaluator_type_list=self.evaluator_type_list,
            )

            # 收集 llm 的结构化输出并适配到当前 evaluator 需要的格式
            # 最后一个 task record 应该是 SmartExtractorTask，读取其结构化输出作为 prediction。
            final_task_record = workflow_context.get_last_task_record()
            final_output_message_content = final_task_record["task_context"]["output"][-1]["content"]
            llm_output_dict = EvaluatorAdaptor.parse_extracted_data_to_evaluator_schema(
                text_json_response=final_output_message_content,
                expected_schema=evaluation_schema,
            )

            evaluation_sample_list.append({
                "llm_output_dict": llm_output_dict,
                "dataset_ground_truth_dict": dataset_ground_truth_dict,
            })

        # 先执行全部 evaluator，只保留内存中的评测结果，最后统一融合写报告。
        evaluation_result_list: List[Dict[str, Any]] = []
        for evaluator_type in self.evaluator_type_list:
            evaluator = EvaluatorFactory.create(
                evaluator_type=evaluator_type,
            )
            evaluation_result = evaluator.evaluate_batch(
                sample_list=evaluation_sample_list,
            )
            chart_text = evaluator.build_chart_mermaid(
                evaluation_result,
            ).rstrip()

            evaluation_result_list.append(
                {
                    "evaluator_name": evaluator_type.value,
                    "result": evaluation_result,
                    "chart_text": chart_text,
                },
            )

            print(f"  Evaluator: {evaluator_type.value}")
            print(f"  Average Score: {evaluation_result['average_score']:.4f}")
            print(f"  Summary: {evaluation_result['summary']}")

        # 所有 evaluator 都结束后，再融合成一份总报告。
        merged_report_lines: List[str] = []
        merged_report_lines.append("# Evaluation Report")
        merged_report_lines.append("")
        merged_report_lines.append(f"- Total Evaluators: {len(evaluation_result_list)}")
        merged_report_lines.append(f"- Total Samples: {len(evaluation_sample_list)}")
        merged_report_lines.append("")

        for evaluation_item in evaluation_result_list:
            evaluator_name = evaluation_item["evaluator_name"]
            evaluation_result = evaluation_item["result"]
            chart_text = evaluation_item["chart_text"]

            merged_report_lines.append(f"## Evaluator: {evaluator_name}")
            merged_report_lines.append("")
            merged_report_lines.append(f"- Metric: {evaluation_result['metric_name']}")
            merged_report_lines.append(f"- Total Samples: {evaluation_result['total_samples']}")
            merged_report_lines.append(f"- Average Score: {evaluation_result['average_score']:.4f}")
            merged_report_lines.append(f"- Min Score: {evaluation_result['min_score']:.4f}")
            merged_report_lines.append(f"- Max Score: {evaluation_result['max_score']:.4f}")
            merged_report_lines.append("")

            merged_report_lines.append("### Summary")
            merged_report_lines.append("")
            for summary_key, summary_value in evaluation_result["summary"].items():
                merged_report_lines.append(f"- {summary_key}: {summary_value}")
            merged_report_lines.append("")

            merged_report_lines.append("### Score Distribution")
            merged_report_lines.append("")
            merged_report_lines.append("```mermaid")
            merged_report_lines.append(chart_text)
            merged_report_lines.append("```")
            merged_report_lines.append("")

        merged_report_path = "evaluation_report.md"
        with open(merged_report_path, "w", encoding="utf-8") as report_file:
            report_file.write("\n".join(merged_report_lines))

        return {
            "report_path": merged_report_path,
            "results": evaluation_result_list,
        }

    async def fire_tasks_execution(
        self,
        inlet_tasks: List[TaskConfig] = [],
        outlet_tasks: List[TaskConfig] = [],
    ) -> WorkflowContext:
        """
        执行单道题工作流并返回对应上下文。

        Args:
            inlet_tasks: 题目注入任务配置列表，会被顺序接在工作流头
            outlet_tasks: 题目输出任务配置列表，会被顺序接在工作流尾中

        Returns:
            工作流上下文，包含本次 fire_tasks_execution 的全部对话记录和结果。
        """
        workflow_context = WorkflowContext(
            workflow_id=self.id,
        )

        # core task 只保留用户配置，不在成员变量上原地 insert，避免多轮 fire_tasks_execution 污染配置。
        core_task_config_list = list(self.task_config_list)

        # 执行链：题目注入 -> 核心推理任务 -> 智能数据提取器。
        execution_task_config_list: List[TaskConfig] = []
        execution_task_config_list.extend(inlet_tasks)
        execution_task_config_list.extend(core_task_config_list)
        execution_task_config_list.extend(outlet_tasks)

        # 根据每个任务配置创建并执行任务，任务内部会把结果写回 workflow_context。
        for task_config in execution_task_config_list:
            task = TaskFactory.create(task_config)
            task_record = await task.execute(workflow_context)

            for task_output_msg in task_record["task_context"]["output"]:
                # 一旦任何任务输出标记为 FAILED，直接中止整个流程。
                if task_output_msg["status"] == ConversationMessageStatus.FAILED:
                    raise Exception(
                        f"Task {task.config.id} failed with error: {task_output_msg['content']}",
                    )

        return workflow_context

    async def run(self) -> List[WorkflowContext]:
        """初始化 dataset 与 evaluator，执行全量工作流并返回全部上下文。"""
        all_workflow_contexts: List[WorkflowContext] = []

        # question_item_list 和 all_workflow_contexts 使用相同索引对齐。
        dataset_inlet_item_list = self.init_dataset_inlet()

        inlet_tasks: List[TaskConfig] = []
        for dataset_inlet_item in dataset_inlet_item_list:
            inlet_task = PlainTextTaskConfig(
                prompt_template=PromptTemplate(
                    text=dataset_inlet_item.text_question,
                ),
            )
            inlet_tasks.append(inlet_task)

        smart_extractor_task_config = self.init_extractor()

        # 逐题执行 fire，收集每题上下文。
        for i in range(len(dataset_inlet_item_list)):
            workflow_context = await self.fire_tasks_execution(
                inlet_tasks=[inlet_tasks[i]],
                outlet_tasks=[smart_extractor_task_config],
            )
            all_workflow_contexts.append(workflow_context)

        result = self.init_evaluator(
            all_workflow_contexts=all_workflow_contexts,
            dataset_inlet_item_list=dataset_inlet_item_list,
        )

        return all_workflow_contexts
