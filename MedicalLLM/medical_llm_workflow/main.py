"""示例入口脚本。

该文件用于演示如何拼装一个最小可运行的医疗推理工作流：
1) 构建任务链配置；
2) 构建 benchmark 配置；
3) 创建并执行 Workflow；
4) 打印每个任务的输入输出记录。
"""
import asyncio
from typing import List
from .schemas import (
    TaskConfig,
    TaskContext,
    BenchmarkConfig,
    BenchmarkType,
    WorkflowConfig,
)
from .Domain.recipes import RecipeFactory, RecipeType
from .Service.workflow import Workflow
from .Infrastructure.LLM_client.models import PoeChatbotConfig, PoeChatbotModel


def _temp_get_benchmark_config() -> List[BenchmarkConfig]:
    """构建 demo 用 benchmark 配置。"""
    
    # hard code for demo
    benchmark_id = BenchmarkType.MED_QA
    num_of_questions = 5
    config = BenchmarkConfig(
        id=benchmark_id,
        name="Sample Benchamrk",
        num_of_questions=num_of_questions,
    )
    
    return [config]

# TODO
def _temp_get_workflow_config() -> WorkflowConfig:
    """构建 demo 用工作流基础配置。"""
    # hard code for demo
    config = WorkflowConfig(
        name="Example Medical QA Workflow",
    )
    
    return config


async def _temp_create_and_run_workflow():
    """组装配置并执行工作流，然后打印完整任务记录。"""

    # 1) 任务链配置
    chatbot_config = PoeChatbotConfig(
        model=PoeChatbotModel.GPT_5_1,
    )
    
    recipe = RecipeFactory.get_recipe(RecipeType.MEDICAL_REASONING_3_STEPS)
    
    task_config_list = recipe.build_task_configs(chatbot_config)
    
    # 2) benchmark 配置
    benchamrk_config_list = _temp_get_benchmark_config()

    # 3) 工作流配置合并
    workflow_config = _temp_get_workflow_config()
    workflow_config.task_config_list.extend(task_config_list)
    workflow_config.benchamrk_config_list.extend(benchamrk_config_list)
    
    # 4) 创建工作流实例
    workflow = Workflow(workflow_config)

    try:
        # 运行工作流
        workflow_context = await workflow.fire()

        # 打印结果
        for task_record in workflow_context.get_all_records():
            task_config: TaskConfig = task_record.task_config
            task_context: TaskContext = task_record.task_context
            
            print(f"\nTask ID: {task_config.id} (Type: {task_config.type.value})")
            print(f"Input:")
            for msg in task_context.input:
                print(f"{msg}")
        
            print(f"output:")
            for msg in task_context.output:
                print(f"{msg}")
            print("-" * 60)

    except Exception as e:
        print(f"Error occurred: {e}")
        raise


async def main():
    """程序主入口：运行 demo 工作流。"""
    await _temp_create_and_run_workflow()
    


if __name__ == "__main__":
    asyncio.run(main())
