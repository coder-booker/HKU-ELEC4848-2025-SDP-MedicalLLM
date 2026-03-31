"""示例入口脚本。

该文件用于演示如何拼装一个最小可运行的医疗推理工作流：
1) 构建任务链配置；
2) 构建 benchmark 配置；
3) 创建并执行 Workflow；
4) 打印每个任务的输入输出记录。
"""
import asyncio
from typing import List
import json

from medical_llm_workflow.Domain.tasks.models import TaskConfig, TaskContext
from .Domain.recipes import RecipeFactory, RecipeType
from .Service.workflow import Workflow
from .Infrastructure.LLM_client import PoeChatbotConfig, PoeChatbotModel, ChatbotType
from .Domain.benchmark.Dataset import DatasetType, DatasetConfig
from .Domain.benchmark.Evaluator import EvaluatorType


def _temp_get_dataset_config() -> List[DatasetConfig]:
    """构建 demo 用数据集配置。"""
    # hard code for demo
    config = DatasetConfig(
        dataset_type=DatasetType.MED_QA,
        num_of_questions=1,
    )
    
    return [config]

def _temp_get_evaluator_type_list() -> List[EvaluatorType]:
    """构建 demo 用评测器配置。"""
    # hard code for demo
    return [EvaluatorType.ACCURACY]


async def _temp_create_and_run_workflow():
    """组装配置并执行工作流，然后打印完整任务记录。"""
    # 1) 任务链配置：通过 RecipeFactory 获取 Recipe 实例，生成 TaskConfig 列表
    chatbot_config: PoeChatbotConfig = {
        "chatbot_type": ChatbotType.POE,
        "model": PoeChatbotModel.GPT_5_1,
        "temperature": 0.7,
        "max_tokens": 2048,
    }
    print(f"Using chatbot config: {json.dumps(chatbot_config, ensure_ascii=False, indent=2)}")
    recipe = RecipeFactory.get_recipe(
        recipe_type=RecipeType.MEDICAL_REASONING_3_STEPS,
        chatbot_config=chatbot_config,
    )
    task_config_list = recipe.build_task_configs()
    
    # 2) benchmark 配置
    dataset_config_list = _temp_get_dataset_config()
    evaluator_type_list = _temp_get_evaluator_type_list()
    
    # 3) 创建工作流实例
    workflow = Workflow(
        name="Medical Reasoning Workflow Demo",
        task_config_list=task_config_list,
        dataset_config_list=dataset_config_list,
        evaluator_type_list=evaluator_type_list,
    )

    try:
        # 运行工作流
        all_workflow_context = await workflow.run()

        # 打印结果
        print("\n=== Workflow Execution Records ===")
        for workflow_context in all_workflow_context:
            print(f"=== Workflow '{workflow_context.workflow_id}' Execution Records ===")
            for task_record in workflow_context.get_all_records():
                task_config: TaskConfig = task_record["task_config"]
                task_context: TaskContext = task_record["task_context"]
                
                print("-" * 60)
                print(f"Task Config: {json.dumps(task_config.to_dict(), ensure_ascii=False, indent=2)}")
                print(f"Task Context: {json.dumps(task_context, ensure_ascii=False, indent=2)}")

    except Exception as e:
        print(f"Error occurred: {e}")
        raise


async def main():
    """程序主入口：运行 demo 工作流。"""
    await _temp_create_and_run_workflow()


if __name__ == "__main__":
    asyncio.run(main())
