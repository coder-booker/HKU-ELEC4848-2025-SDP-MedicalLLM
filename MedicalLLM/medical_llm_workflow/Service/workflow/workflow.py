"""工作流编排器。

该模块负责把 `WorkflowConfig` 转换为实际执行流程：
1) 从 benchmark 获取问题；
2) 构建初始问题记录；
3) 依次创建并执行任务；
4) 汇总并打印 benchmark 结果。
"""
import asyncio
import uuid
from collections import defaultdict
from typing import Any, Dict, List, Tuple
from typing_extensions import TypedDict

from pydantic import BaseModel

from medical_llm_workflow.schemas import (
    ConversationMessageStatus,
)
from medical_llm_workflow.schemas.models import (
    ConversationMessage,
    ConversationMessageRole,
)
from medical_llm_workflow.Domain.tasks.models import (
    TaskRecord,
)
from medical_llm_workflow.Domain.prompts.models import PromptTemplate
from medical_llm_workflow.Domain.benchmark.Evaluator.base_evaluator import (
    BaseEvaluator,
)
from medical_llm_workflow.Domain.tasks import (
    PlainTextTaskConfig,
    SmartExtractorTaskConfig,
    TaskConfig,
)
from medical_llm_workflow.Domain.tasks.all_tasks.smart_extractor_task import SmartExtractorTask
from medical_llm_workflow.Domain.prompts import PromptTemplate
from medical_llm_workflow.Domain.tasks import TaskFactory
from medical_llm_workflow.Domain.workflow_context import WorkflowContext
from medical_llm_workflow.Domain.benchmark.Dataset import DatasetFactory
from medical_llm_workflow.Domain.benchmark.Evaluator import (
    EvaluationSample,
    EvaluatorFactory,
)
from medical_llm_workflow.Domain.benchmark.Evaluator import EvaluatorType
from medical_llm_workflow.Domain.benchmark.Dataset import DatasetConfig, DatasetType
from medical_llm_workflow.Domain.benchmark.EvaluatorAdaptor.evaluator_adaptor import EvaluatorAdaptor
from medical_llm_workflow.Infrastructure.logger import WorkflowLogger
from medical_llm_workflow.utils import print_log, emit_event, get_run_dir
from medical_llm_workflow.Domain.benchmark.Evaluator import EvluationBatchResult



class DatasetInletItem(BaseModel):
    """
    - dataset_type: DatasetType - 数据集类型，供后续 evaluator 识别题目格式
    - text_question: str - 传给工作流的文本题目
    - json_question: Dict[str, Any] - 传给 evaluator 的结构化题目
    """

    dataset_type: DatasetType
    text_question: str
    json_question: Dict[str, Any]

class EvaluationResultItemForReport(TypedDict):
    """
    - dataset_type: str - 数据集类型
    - evaluator_name: str - 评测器名称
    - result: Dict[str, Any] - 评测结果数据
    - chart_data: Dict[str, Any] - 提供给前端直接可用的图形图表数据结构
    - report_text: str - 评测器自身生成的报告内容
    """

    dataset_type: str
    evaluator_name: str
    result: EvluationBatchResult
    chart_data: Dict[str, Any]
    report_text: str


class Workflow:
    """工作流执行器。"""

    def __init__(
        self,
        id: uuid.UUID = uuid.uuid4(),
        name: str = "Default Workflow Name",
        task_config_list: List[TaskConfig] = [],
        dataset_config_list: List[DatasetConfig] = [],
        # language: LanguageType = LanguageType.EN # 整条工作流的语言
    ):
        """保存工作流配置并初始化上下文容器。"""
        self.id = id
        self.name = name

        # 避免外部列表引用导致运行中被意外修改。
        self.task_config_list = list(task_config_list)
        self.dataset_config_list = list(dataset_config_list)

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
        """根据类中的 evaluator 初始化 SmartExtractor 任务配置。"""
        extractor_chatbot_config = None

        # TODO
        # extractor 本身也要调用 LLM，因此复用主任务链中的任一可用 chatbot_config。
        for task_config in self.task_config_list:
            if getattr(task_config, "chatbot_config", None) is not None:
                extractor_chatbot_config = task_config.chatbot_config
                break

        all_evaluator_types = set()
        for dataset_config in self.dataset_config_list:
            all_evaluator_types.update(dataset_config.evaluator_type_list)
            
        # 收集前面所有核心任务的ID作为 SmartExtractor 的上下文来源，否则 extractor 只能看到最原始题目
        input_sources = ["question_task"] + [t.id for t in self.task_config_list]

        extractor_task_config = SmartExtractorTaskConfig(
            id="smart_extractor",
            chatbot_config=extractor_chatbot_config,
            evaluator_type_list=list(all_evaluator_types),
            input_msg_sources=input_sources,
        )

        return extractor_task_config

    def _group_contexts_by_dataset(
        self,
        all_workflow_contexts: List[WorkflowContext],
        dataset_inlet_item_list: List[DatasetInletItem],
    ) -> Dict[DatasetType, List[Tuple[WorkflowContext, DatasetInletItem]]]:
        """按 dataset 划分 contexts。"""
        dataset_context_map: Dict[DatasetType, List[Tuple[WorkflowContext, DatasetInletItem]]] = defaultdict(list)
        for idx, ctx in enumerate(all_workflow_contexts):
            inlet_item: DatasetInletItem = dataset_inlet_item_list[idx]
            dataset_context_map[inlet_item.dataset_type].append((ctx, inlet_item))
        return dataset_context_map

    def _prepare_evaluation_samples(
        self,
        ctx_items: List[Tuple[WorkflowContext, DatasetInletItem]],
        evaluation_schema: Dict[str, Any],
        current_evaluator_type_list: List[EvaluatorType],
    ) -> List[EvaluationSample]:
        """准各待评估的样本集。"""
        evaluation_sample_list: List[EvaluationSample] = []
        for ctx, inlet_item in ctx_items:
            dataset_ground_truth_dict: Dict[str, Any] = EvaluatorAdaptor.parse_dataset_question_to_evaluator_schema(
                dataset_type=inlet_item.dataset_type,
                dataset_json_question=inlet_item.json_question,
                evaluator_type_list=current_evaluator_type_list,
            )

            final_task_record: TaskRecord = ctx.get_last_task_record()
            final_output_message: ConversationMessage = final_task_record["task_context"]["output"][-1]
            final_output_message_content: str = final_output_message["content"] if isinstance(final_output_message, dict) else final_output_message.content

            llm_output_dict: Dict[str, Any] = EvaluatorAdaptor.parse_extracted_data_to_evaluator_schema(
                text_json_response=final_output_message_content,
                expected_schema=evaluation_schema,
            )

            evaluation_sample_list.append({
                "workflow_context_id": ctx.get_workflow_id(),
                "llm_output_dict": llm_output_dict,
                "dataset_ground_truth_dict": dataset_ground_truth_dict,
            })
        return evaluation_sample_list

    def _inject_llm_judge_records(
        self,
        target_ctx: WorkflowContext,
        ev_record: Dict[str, Any],
        evaluator_type: EvaluatorType,
    ) -> None:
        """只要 evaluator 返回了 llm as judge 相关的记录，就作为虚拟任务注入到任务历史上下文中。"""
        if not ev_record.get("llm_prompt") and not ev_record.get("llm_response"):
            return

        judge_msg_input = []
        if ev_record.get("llm_prompt"):
            judge_msg_input.append({
                "role": ConversationMessageRole.USER.value,
                "content": str(ev_record.get("llm_prompt")),
                "status": ConversationMessageStatus.NORMAL.value,
            })
        
        judge_msg_output = []
        if ev_record.get("llm_response"):
            judge_msg_output.append({
                "role": ConversationMessageRole.BOT.value,
                "content": str(ev_record.get("llm_response")),
                "status": ConversationMessageStatus.NORMAL.value,
            })
        
        target_ctx.append_task_record({
            "task_config": PlainTextTaskConfig(
                id=f"evaluator_{evaluator_type.value}",
                prompt_template=PromptTemplate(text=""),
            ),
            "task_context": {
                "input": judge_msg_input,
                "output": judge_msg_output,
            },
        })

    def _append_evaluation_log(
        self,
        dataset_type: DatasetType,
        question_index: int,
        evaluator_type: EvaluatorType,
        ev_record: Dict[str, Any],
    ) -> None:
        """追加记录此评估器使用的大模型作为裁判过程的日志到底层文件。"""
        # print("Appending LLM judge log for evaluator:", evaluator_type.value)
        # print("LLM judge prompt:", ev_record)
        if not ev_record.get("llm_prompt") and not ev_record.get("llm_response"):
            # print("====================================")
            # print("No LLM judge log found in evaluation record, skipping append.")
            return
        
            
        judge_msg_input = []
        if ev_record.get("llm_prompt"):
            judge_msg_input.append({
                "role": ConversationMessageRole.USER.value,
                "content": str(ev_record.get("llm_prompt")),
                "status": ConversationMessageStatus.NORMAL.value,
            })
            
        judge_msg_output = []
        if ev_record.get("llm_response"):
            judge_msg_output.append({
                "role": ConversationMessageRole.BOT.value,
                "content": str(ev_record.get("llm_response")),
                "status": ConversationMessageStatus.NORMAL.value,
            })
            
        WorkflowLogger.append_evaluation_log(
            dataset_type=dataset_type.value if hasattr(dataset_type, "value") else str(dataset_type),
            question_index=question_index,
            evaluator_name=evaluator_type.value,
            input_msgs=judge_msg_input,
            output_msgs=judge_msg_output,
        )

    async def evaluate(
        self,
        all_workflow_contexts: List[WorkflowContext],
        dataset_inlet_item_list: List[DatasetInletItem],
    ) -> List[EvaluationResultItemForReport]:
        """执行每个数据集对应的 evaluator，并在最后融合输出统一报告。"""
        # print("Starting evaluation of all workflow contexts...")
        evaluation_result_list: List[EvaluationResultItemForReport] = []
        dataset_context_map = self._group_contexts_by_dataset(
            all_workflow_contexts=all_workflow_contexts,
            dataset_inlet_item_list=dataset_inlet_item_list,
        )

        for dataset_config in self.dataset_config_list:
            dataset_type: DatasetType = dataset_config.dataset_type
            ctx_items: List[Tuple[WorkflowContext, DatasetInletItem]] = dataset_context_map.get(dataset_type, [])
            if not ctx_items:
                continue

            current_evaluator_type_list: List[EvaluatorType] = dataset_config.evaluator_type_list
            if not current_evaluator_type_list:
                continue

            evaluation_schema: Dict[str, Any] = EvaluatorAdaptor.build_expected_schema(current_evaluator_type_list)
            evaluation_sample_list = self._prepare_evaluation_samples(
                ctx_items=ctx_items,
                evaluation_schema=evaluation_schema,
                current_evaluator_type_list=current_evaluator_type_list,
            )

            for evaluator_type in current_evaluator_type_list:
                # 给每个 evaluator 提取可能的前端自定义 LLM 配置 (可选)
                evaluator_configs_map = getattr(dataset_config, "evaluator_configs", {})
                chatbot_config = evaluator_configs_map.get(evaluator_type.value)

                evaluator: BaseEvaluator = EvaluatorFactory.create(
                    evaluator_type=evaluator_type,
                    chatbot_config=chatbot_config,
                )

                if evaluator is None:
                    continue  # 工厂卫语句触发兜底，跳过不存在的评测器

                evaluation_result: EvluationBatchResult = await evaluator.evaluate_batch(sample_list=evaluation_sample_list)
                
                # 把 Evaluator 评测中的 log 追加回所属的题目的 WorkflowContext 历史中
                for idx, ev_record in enumerate(evaluation_result["records"]):
                    ctx_id = evaluation_sample_list[idx]["workflow_context_id"]
                    
                    target_ctx_item_tuple = next(t for t in ctx_items if t[0].get_workflow_id() == ctx_id)
                    target_ctx = target_ctx_item_tuple[0]
                    inlet_item = target_ctx_item_tuple[1]
                    
                    self._inject_llm_judge_records(
                        target_ctx=target_ctx,
                        ev_record=ev_record,
                        evaluator_type=evaluator_type,
                    )
                    
                    display_index = dataset_inlet_item_list.index(inlet_item) + 1
                    
                    self._append_evaluation_log(
                        dataset_type=dataset_type,
                        question_index=display_index,
                        evaluator_type=evaluator_type,
                        ev_record=ev_record,
                    )

                chart_data: Dict[str, Any] = evaluator.build_chart_data(evaluation_result)
                report_text: str = evaluator.build_report_markdown(evaluation_result)

                evaluation_result_list.append({
                    "dataset_type": dataset_type.value if hasattr(dataset_type, "value") else str(dataset_type),
                    "evaluator_name": evaluator_type.value,
                    "result": evaluation_result,
                    "chart_data": chart_data,
                    "report_text": report_text,
                })

        return evaluation_result_list


    async def fire_tasks_execution(
        self,
        workflow_context: WorkflowContext,
        inlet_tasks: List[TaskConfig] = [],
        outlet_tasks: List[TaskConfig] = [],
    ) -> WorkflowContext:
        """
        执行单道题工作流并返回对应上下文。

        Args:
            workflow_context: 工作流上下文实例
            inlet_tasks: 题目注入任务配置列表，会被顺序接在工作流头
            outlet_tasks: 题目输出任务配置列表，会被顺序接在工作流尾中

        Returns:
            工作流上下文，包含本次 fire_tasks_execution 的全部对话记录和结果。
        """

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

    async def run_single(
        self,
        index: int,
        dataset_inlet_item: DatasetInletItem,
        inlet_task: TaskConfig,
        total_questions: int,
        semaphore: asyncio.Semaphore,
        progress_state: Dict[str, int],
    ) -> WorkflowContext:
        """
        执行单道题目的完整工作流封装。
        
        参数:
        - index: 原始列表索引,
        - dataset_inlet_item: 当前题目的输入数据,
        - inlet_task: 注入任务配置,
        - smart_extractor_task_config: 智能提取器配置,
        - total_questions: 总题目数量,
        - semaphore: 并发控制信号量,
        - progress_state: 用于记录和同步完成进度的可变字典,
        """
        # 使用基于 1 索引的友好题目标号进行界面展示传递
        current_dataset = dataset_inlet_item.dataset_type
        display_index = index + 1
        
        # 在单题执行前发送“题目开始”事件，携带所属数据集类型
        emit_event(
            "QUESTION_STARTED",
            {
                "question_index": display_index,
                "dataset_type": current_dataset.value if hasattr(current_dataset, "value") else current_dataset,
            },
        )
        
        async with semaphore:
            context = WorkflowContext(workflow_id=self.id)
            try:
                # 触发每题的单线程任务
                await self.fire_tasks_execution(
                    workflow_context=context,
                    inlet_tasks=[inlet_task],

                )
                # 每跑完一道题就立刻生成独立日志存入独立文件
                WorkflowLogger.log_question(
                    dataset_type=current_dataset.value if hasattr(current_dataset, "value") else current_dataset,
                    question_index=display_index,
                    workflow_context=context,
                )
                
                progress_state["completed"] += 1
                
                # 检查 context 中的所有 task record，有没有 error 或者包含 "error" 的情况
                has_error = False
                for record in context.get_all_records():
                    for task_output in record.get("task_context", {}).get("output", []):
                        if isinstance(task_output.get("content"), str) and "error" in task_output["content"].lower():
                            has_error = True
                            break
                    if has_error:
                        break

                # 向前端抛出题目完成进度以及该题的基本信息（包含是否发生内部错误）
                if has_error:
                    emit_event(
                        "QUESTION_FAILED",
                        {
                            "completed_questions": progress_state["completed"],
                            "total_questions": total_questions,
                            "question_index": display_index,
                            "dataset_type": current_dataset.value if hasattr(current_dataset, "value") else current_dataset,
                            "error": "A task reported an error during execution."
                        },
                    )
                else:
                    emit_event(
                        "QUESTION_COMPLETED",
                        {
                            "completed_questions": progress_state["completed"],
                            "total_questions": total_questions,
                            "question_index": display_index,
                            "dataset_type": current_dataset.value if hasattr(current_dataset, "value") else current_dataset,
                        },
                    )
                return context
            except Exception as e:
                print_log(f"Error processing question {display_index}: {e}", prefix="[ERROR]")
                
                # Even if there's an error, save the partial context and the error
                WorkflowLogger.log_question(
                    dataset_type=current_dataset.value if hasattr(current_dataset, "value") else current_dataset,
                    question_index=display_index,
                    workflow_context=context,
                    error=str(e),
                )
                
                emit_event(
                    "QUESTION_FAILED",
                    {
                        "question_index": display_index,
                        "dataset_type": current_dataset.value if hasattr(current_dataset, "value") else current_dataset,
                        "error": str(e),
                    },
                )
                return e

    async def run_batch(self) -> Tuple[List[WorkflowContext], Dict[str, Any]]:
        """初始化 dataset 与 evaluator，全量执行批量工作流并返回全部上下文。"""
        all_workflow_contexts: List[WorkflowContext] = []

        # ---- dataset ----
        # question_item_list 和 all_workflow_contexts 使用相同索引对齐。
        emit_event(
            "PHASE_START",
            {
                "phase": "dataset",
                "message": "Processing dataset",
            },
        )
        print_log("Initializing dataset inlet...", prefix="[WORKFLOW]", debug=True)
        dataset_inlet_item_list = self.init_dataset_inlet()
        inlet_tasks: List[TaskConfig] = []
        for dataset_inlet_item in dataset_inlet_item_list:
            inlet_task = PlainTextTaskConfig(
                id="question_task",
                prompt_template=PromptTemplate(
                    text=dataset_inlet_item.text_question,
                ),
            )
            inlet_tasks.append(inlet_task)

        # 智能抽取器现在由前端配置并作为普通任务传递进来，此处移除写死附加
        
        total_questions = len(dataset_inlet_item_list)
        
        # 逐题执行 fire，使用信号量控制并发数。
        emit_event(
            "PHASE_START",
            {
                "phase": "execution",
                "message": "Running tasks concurrently",
                "total_questions": total_questions,
            },
        )
        print_log("Executing workflows for each question concurrently...", prefix="[WORKFLOW]", debug=True)
        
        semaphore = asyncio.Semaphore(5)
        progress_state = {"completed": 0}
                    
        # 并发执行所有题目并保持顺序
        tasks_to_run = [
            self.run_single(
        # smart_extractor 已作为配置中的最后一项传入 tasks_config_list 中，此处移除特权传递
                index=i,
                dataset_inlet_item=dataset_inlet_item_list[i],
                inlet_task=inlet_tasks[i],
                total_questions=total_questions,
                semaphore=semaphore,
                progress_state=progress_state,
            )
            for i in range(total_questions)
        ]
        gathered_results = await asyncio.gather(*tasks_to_run, return_exceptions=True)
        
        all_workflow_contexts: List[WorkflowContext] = []
        successful_inlet_items: List[DatasetInletItem] = []
        for idx, result in enumerate(gathered_results):
            if isinstance(result, Exception):
                # We skip evaluating contexts that failed
                continue
            all_workflow_contexts.append(result)
            successful_inlet_items.append(dataset_inlet_item_list[idx])

        emit_event(
            "PHASE_START",
            {
                "phase": "evaluation",
                "message": "Evaluating results",
            },
        )
        print_log("All workflows executed. Starting evaluation...", prefix="[WORKFLOW]", debug=True)
        
        if len(all_workflow_contexts) == 0:
            print_log("No questions completed successfully. Skipping evaluation.", prefix="[WORKFLOW]")
            return [], {"error": "[SKIPPED] No questions completed successfully, evaluation aborted."}

        evaluation_result_list = await self.evaluate(
            all_workflow_contexts=all_workflow_contexts,
            dataset_inlet_item_list=successful_inlet_items,
        )
        
        report_info = WorkflowLogger.log_evaluation_report(
            evaluation_result_list=evaluation_result_list,
            dataset_inlet_item_list=successful_inlet_items,
        )
        print_log(f"Final evaluation report generated: {report_info['report_path']}", prefix="[WORKFLOW]", debug=True)

        return all_workflow_contexts, report_info
        