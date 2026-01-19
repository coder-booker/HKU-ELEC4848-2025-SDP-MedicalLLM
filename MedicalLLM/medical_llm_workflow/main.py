"""主程序示例，演示如何使用医疗 LLM 工作流框架。"""
import asyncio
from typing import List, Optional

from .schemas import (
    PoeChatbotModel,
    PoeChatbotConfig,
    LanguageType,
    PromptType,
    PromptTemplate,
    ConversationMessageRole,
    ConversationMessage,
    TaskType,
    TaskConfig,
    TaskContext,
    BenchmarkConfig,
    BenchmarkType,
    MedQABenchmarkProtocal,
    WorkflowConfig,
)
from .Service.workflow import Workflow


# TODO: 理论上是从前端传入的
# 示例：定义任务配置（使用 SELF_REFINE 模式）
def _temp_get_task_config() -> List[TaskConfig]:
    
    # 获得聊天机器人配置
    chatbot_config = PoeChatbotConfig(
        model=PoeChatbotModel.GPT_5_1,
    )
    
    return [
        TaskConfig(
            id="medical_qa_task",
            type=TaskType.SINGLE_AGENT,
            chatbot_config=chatbot_config,
        )
    ]

# TODO
def _temp_get_benchmark_config(benchmark_id: BenchmarkType) -> List[BenchmarkConfig]:
    # hard code for demo
    config = BenchmarkConfig(
        id=benchmark_id,
        name="Sample Benchamrk",
        num_of_questions=10,
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
    
    benchamrk_config_list = _temp_get_benchmark_config(BenchmarkType.MED_QA)

    workflow_config = _temp_get_workflow_config()
    workflow_config.task_config_list = task_config_list
    workflow_config.benchamrk_config_list=benchamrk_config_list
    
    workflow = Workflow(workflow_config)

    print("=" * 60)
    print("Running Medical LLM Workflow")
    print("=" * 60)
    # print(f"Question: {medical_question.strip()}")
    print()

    try:
        
        # 运行工作流
        workflow_context = await workflow.fire()

        # 打印结果
        print()
        print("=" * 60)
        print("Workflow Results:")
        print("=" * 60)
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
