"""主程序示例，演示如何使用医疗 LLM 工作流框架。"""
import asyncio
from typing import List
import os
print(os.getcwd())

from .schemas import (
    PoeChatbotModel,
    PoeChatbotConfig,
    TaskType,
    TaskConfig,
    TaskContext,
    BenchmarkConfig,
    BenchmarkType,
    WorkflowConfig,
)
from .Service.workflow import Workflow



# TODO: 理论上是从前端传入的
# 示例：定义任务配置（使用 SELF_REFINE 模式）
def _temp_get_task_config() -> List[TaskConfig]:
    
    chatbot_config = PoeChatbotConfig(
        model=PoeChatbotModel.GPT_5_1,
    )
    
    return [
        TaskConfig(
            id="single_agent_1",
            type=TaskType.SINGLE_AGENT,
            chatbot_config=chatbot_config,
            connect_to=["single_agent_2"],
        ),
        TaskConfig(
            id="single_agent_2",
            type=TaskType.SINGLE_AGENT,
            chatbot_config=chatbot_config,
        ),
    ]

# TODO
def _temp_get_benchmark_config() -> List[BenchmarkConfig]:
    
    # hard code for demo
    benchmark_id = BenchmarkType.MED_QA
    num_of_questions = 1
    config = BenchmarkConfig(
        id=benchmark_id,
        name="Sample Benchamrk",
        num_of_questions=num_of_questions,
    )
    
    return [config]

# TODO
def _temp_get_workflow_config() -> WorkflowConfig:
    # hard code for demo
    config = WorkflowConfig(
        name="Example Medical QA Workflow",
    )
    
    return config


async def _temp_create_and_run_workflow():

    task_config_list = _temp_get_task_config()
    
    benchamrk_config_list = _temp_get_benchmark_config()

    workflow_config = _temp_get_workflow_config()
    workflow_config.task_config_list.extend(task_config_list)
    workflow_config.benchamrk_config_list.extend(benchamrk_config_list)
    
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
    await _temp_create_and_run_workflow()
    


if __name__ == "__main__":
    asyncio.run(main())
