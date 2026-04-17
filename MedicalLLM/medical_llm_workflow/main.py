"""医疗推理工作流主入口。

该文件被重构为支持外部配置注入的形式，为后续改为后端微服务接口做准备。
全局维护了一套默认配置，确保在无任何输入的情况下依然能按原有的行为运行此脚本。
"""
import asyncio
import traceback
import os
from typing import Any, Dict, List, Tuple


from medical_llm_workflow.Domain.tasks import TaskConfig, TaskContext, SmartExtractorTaskConfig
from medical_llm_workflow.Domain.workflow_context.workflow_context import WorkflowContext
from medical_llm_workflow.Domain.recipes import RecipeFactory, RecipeType
from medical_llm_workflow.Domain.benchmark.Dataset import DatasetType, DatasetConfig
from medical_llm_workflow.Domain.benchmark.Evaluator import EvaluatorType
from medical_llm_workflow.Infrastructure.LLM_client import PoeChatbotConfig, PoeChatbotModel, ChatbotType
from medical_llm_workflow.Service.workflow import Workflow
from medical_llm_workflow.app_settings import AppSettings
from medical_llm_workflow.utils import print_log, run_dir_var



# 全局默认配置：作为以后后端服务的默认回退参数，各函数直接在此取值
DEFAULT_DATASET_CONFIG = [
    # DatasetConfig(
    #     dataset_type=DatasetType.MED_QA,
    #     num_of_questions=1,
    #     evaluator_type_list=[
    #         EvaluatorType.ACCURACY,
    #         EvaluatorType.PRECISION,
    #     ],
    # ),
    DatasetConfig(
        dataset_type=DatasetType.PUBMED,
        num_of_questions=1,
        evaluator_type_list=[
            EvaluatorType.ACCURACY,
            # EvaluatorType.PRECISION,
            EvaluatorType.CONSISTENCY,
            # EvaluatorType.CLARITY,
        ],
    ),
]

# 全局默认配置：大语言模型请求配置
DEFAULT_CHATBOT_CONFIG = {
    "chatbot_type": ChatbotType.POE,
    "model": PoeChatbotModel.GPT_5_4_NANO,
    "temperature": 0.7,
    "max_tokens": 2048,
}

# 全局默认配置：执行的流程配方
DEFAULT_RECIPE_TYPE = RecipeType.TWO_STAGE_VERIFICATION
# DEFAULT_RECIPE_TYPE = RecipeType.MEDICAL_REASONING_3_STEPS

async def run_core_workflow(
    task_config_list: List[TaskConfig],
    dataset_config_list: List[DatasetConfig],
) -> Tuple[List[WorkflowContext], Dict[str, Any]]:
    """
    工作流核心执行函数。
    只接收预处理后的纯数据，不再处理依赖外部的配置逻辑。
    """

    # 1. 创建工作流实例
    workflow = Workflow(
        name="Medical Reasoning Workflow Demo",
        task_config_list=task_config_list,
        dataset_config_list=dataset_config_list,
    )

    # 直接包裹主执行与日志输出逻辑，不需要过度抓取边界异常
    try:
        # 执行工作流全流程
        print_log("Running workflow...", prefix="[WORKFLOW]", debug=True)
        return await workflow.run_batch()
    except Exception as e:
        print_log(f"Error occurred: {e}\n{traceback.print_exc()}", prefix="[WORKFLOW]", debug=True)
        raise


async def main():
    """程序主入口：提供服务化前最后一次以脚本运行的方式。"""
    
    # 作为脚本直接运行时，单独在这里组装一套默认配方任务与数据参数
    recipe = RecipeFactory.get_recipe(
        recipe_type=DEFAULT_RECIPE_TYPE,
        chatbot_config=DEFAULT_CHATBOT_CONFIG,
    )
    
    task_config_list = recipe.build_task_configs()
    
    # 提取所有使用到的 evaluator type
    all_evaluator_types = set()
    for dataset_config in DEFAULT_DATASET_CONFIG:
        all_evaluator_types.update(dataset_config.evaluator_type_list)
        
    # 添加 SmartExtractor 作为最后的结构化提取和评估节点
    # 它的输入来源为前面的所有核心任务的 ID，以及原始问题
    input_sources = ["question_task"] + [t.id for t in task_config_list]
    extractor_config = SmartExtractorTaskConfig(
        id="smart_extractor",
        chatbot_config=DEFAULT_CHATBOT_CONFIG,
        evaluator_type_list=list(all_evaluator_types),
        input_msg_sources=input_sources,
    )
    task_config_list.append(extractor_config)
    
    # 统一使用最新覆写模式的工作流目录
    from medical_llm_workflow.Service.storage_service import StorageService
    run_dir = StorageService.init_run_dir()
    dir_token = run_dir_var.set(run_dir)
    
    try:
        # 组装完整数据后传给统一的执行函数
        await run_core_workflow(
            task_config_list=task_config_list,
            dataset_config_list=DEFAULT_DATASET_CONFIG,
        )
    finally:
        run_dir_var.reset(dir_token)


if __name__ == "__main__":
    asyncio.run(main())
