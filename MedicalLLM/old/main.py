"""主程序示例，演示如何使用医疗 LLM 工作流框架。"""
import asyncio
import os

from medical_llm_workflow import (
    ContextManager,
    PoeAPIClient,
    PoeAPIConfig,
    PoeChatbotConfig,
    PoeChatbotModel,
    PromptTemplate,
    TaskConfig,
    TaskType,
    WorkflowConfig,
    WorkflowEngine,
)


async def main():
    """主函数示例。"""
    # 从环境变量获取 API key（或直接设置）
    api_key = os.getenv("POE_API_KEY", "YOUR_API_KEY")
    if api_key == "YOUR_API_KEY":
        print("Warning: Please set POE_API_KEY environment variable or update the code.")

    # 创建 Poe API 配置
    poe_api_config = PoeAPIConfig(api_key=api_key)

    # 创建 Poe API 客户端
    poe_client = PoeAPIClient(poe_api_config)

    # 创建上下文管理器
    context_manager = ContextManager()

    # 创建工作流引擎
    engine = WorkflowEngine(poe_client, context_manager)

    # 定义提示词模板
    prompt_template = PromptTemplate(
        system="You are a helpful medical assistant. Provide accurate and helpful medical information.",
        user="Please answer the following medical question: {input}",
        instructions="Be thorough and cite sources when possible.",
    )

    # 定义聊天机器人配置
    chatbot_config = PoeChatbotConfig(
        model=PoeChatbotModel.GPT_5_1,
        temperature=0.7,
        max_tokens=2048,
    )

    # 定义任务配置（使用 SELF_REFINE 模式）
    task_config = TaskConfig(
        task_id="medical_qa_task",
        task_type=TaskType.SELF_REFINE,
        prompt_template=prompt_template,
        chatbot_config=chatbot_config,
        max_retries=3,
        timeout=60,
    )

    # 定义工作流配置
    workflow_config = WorkflowConfig(
        workflow_id="example_workflow",
        name="Example Medical QA Workflow",
        tasks=[task_config],
    )

    # 示例医疗问题
    medical_question = """
    A 45-year-old patient presents with chest pain that started 2 hours ago. 
    The pain is described as crushing and radiates to the left arm. 
    What are the potential diagnoses and what immediate steps should be taken?
    """

    print("=" * 60)
    print("Running Medical LLM Workflow")
    print("=" * 60)
    print(f"Question: {medical_question.strip()}")
    print()

    # 运行工作流
    try:
        workflow_context = await engine.run_workflow(
            workflow_config, medical_question
        )

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


if __name__ == "__main__":
    asyncio.run(main())
