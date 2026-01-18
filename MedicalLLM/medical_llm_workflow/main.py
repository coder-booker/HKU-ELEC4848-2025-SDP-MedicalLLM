"""主程序示例，演示如何使用医疗 LLM 工作流框架。"""
import asyncio
import os
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
    WorkflowConfig,
)
from .Service.workflow import Workflow

from .Infrastructure import PoeClient

# 理论上是从前端传入的
# 示例：定义任务配置（使用 SELF_REFINE 模式）
def _temp_get_task_config() -> List[TaskConfig]:
    
    # 获得聊天机器人配置
    chatbot_config = PoeChatbotConfig(
        model=PoeChatbotModel.GPT_5_1,
        temperature=0.7,
        max_tokens=2048,
    )
    
    return [
        TaskConfig(
            task_id="medical_qa_task",
            task_type=TaskType.SELF_REFINE,
            prompt_type_list=[TaskType.SELF_REFINE],
            chatbot_config=chatbot_config,
            max_retries=3,
            timeout=60,
        )
    ]
    
async def _temp_create_and_run_workflow(poe_client: PoeClient):

    task_config_list = _temp_get_task_config()

    medical_question = """
    A 45-year-old patient presents with chest pain that started 2 hours ago. 
    The pain is described as crushing and radiates to the left arm. 
    What are the potential diagnoses and what immediate steps should be taken?
    """

    workflow_config = WorkflowConfig(
        id="example_workflow",
        name="Example Medical QA Workflow",
        task_config_list=task_config_list,
        poe_client = poe_client,
        initial_question=medical_question,
    )
    workflow = Workflow(workflow_config)

    print("=" * 60)
    print("Running Medical LLM Workflow")
    print("=" * 60)
    print(f"Question: {medical_question.strip()}")
    print()

    # 运行工作流
    try:
        # ------------------------------------------------
        workflow_context = await workflow.fire()
        # ------------------------------------------------

        # 打印结果
        print()
        print("=" * 60)
        print("Workflow Results")
        print("=" * 60)
        for task_id, task_context in workflow_context.task_results.items():
            print(f"\nTask ID: {task_id}")
            print(f"Input: {task_context.input_text[:100]}...")
            print(f"Output: {task_context.output[:200]}...")
            print("-" * 60)

    except Exception as e:
        print(f"Error occurred: {e}")
        raise


async def main():
    await _temp_create_and_run_workflow()
    


if __name__ == "__main__":
    asyncio.run(main())
