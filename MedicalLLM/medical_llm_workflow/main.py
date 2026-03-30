"""示例入口脚本。

该文件用于演示如何拼装一个最小可运行的医疗推理工作流：
1) 构建任务链配置；
2) 构建 benchmark 配置；
3) 创建并执行 Workflow；
4) 打印每个任务的输入输出记录。
"""
import asyncio
from typing import List
from .Domain.recipes import RecipeFactory, RecipeType
from .Service.workflow import Workflow
from .Infrastructure.LLM_client.models import PoeChatbotConfig, PoeChatbotModel
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

def _temp_get_evaluator() -> List[EvaluatorType]:
    """构建 demo 用评测器配置。"""
    # hard code for demo
    return [EvaluatorType.ACCURACY]


async def _temp_create_and_run_workflow():
    """组装配置并执行工作流，然后打印完整任务记录。"""

    # 1) 任务链配置
    chatbot_config = PoeChatbotConfig(
        model=PoeChatbotModel.GPT_5_1,
    )
    
    recipe = RecipeFactory.get_recipe(RecipeType.MEDICAL_REASONING_3_STEPS)
    
    task_config_list = recipe.build_task_configs(chatbot_config)
    
    # 2) benchmark 配置
    dataset_config_list = _temp_get_dataset_config()
    evaluator_list = _temp_get_evaluator()
    
    # 4) 创建工作流实例
    workflow = Workflow(
        name="Medical Reasoning Workflow Demo",
        task_config_list=task_config_list,
        dataset_config_list=dataset_config_list,
        evaluator_list=evaluator_list,
    )

    try:
        # 运行工作流
        all_workflow_context = await workflow.run()

        # 打印结果
        for workflow_context in all_workflow_context:
            for task_record in workflow_context.get_all_records():
                task_config = task_record.task_config
                task_context = task_record.task_context
                print(f"Task Config: {task_config}")
                print(f"Task Context: {task_context}")
                print("-" * 60)

    except Exception as e:
        print(f"Error occurred: {e}")
        raise


async def main():
    """程序主入口：运行 demo 工作流。"""
    await _temp_create_and_run_workflow()


if __name__ == "__main__":
    asyncio.run(main())
