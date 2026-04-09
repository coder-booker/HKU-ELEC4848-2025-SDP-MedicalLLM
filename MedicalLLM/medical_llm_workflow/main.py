"""医疗推理工作流主入口。

该文件被重构为支持外部配置注入的形式，为后续改为后端微服务接口做准备。
全局维护了一套默认配置，确保在无任何输入的情况下依然能按原有的行为运行此脚本。
"""
import asyncio
from typing import List, Optional

from medical_llm_workflow.Domain.tasks import TaskConfig, TaskContext
from medical_llm_workflow.Domain.workflow_context.workflow_context import WorkflowContext
from medical_llm_workflow.Domain.recipes import RecipeFactory, RecipeType
from medical_llm_workflow.Domain.benchmark.Dataset import DatasetType, DatasetConfig
from medical_llm_workflow.Domain.benchmark.Evaluator import EvaluatorType
from medical_llm_workflow.Infrastructure.LLM_client import PoeChatbotConfig, PoeChatbotModel, ChatbotType
from medical_llm_workflow.Service.workflow import Workflow
from medical_llm_workflow.utils import print_log



# 全局默认配置：作为以后后端服务的默认回退参数，各函数直接在此取值
DEFAULT_DATASET_CONFIG = {
    "dataset_type": DatasetType.MED_QA,
    "num_of_questions": 1,
}

# 全局默认配置：评测器类型列表
DEFAULT_EVALUATOR_TYPE_LIST = [
    EvaluatorType.ACCURACY,
]

# 全局默认配置：大语言模型请求配置
DEFAULT_CHATBOT_CONFIG = {
    "chatbot_type": ChatbotType.POE,
    "model": PoeChatbotModel.GPT_5_4_NANO,
    "temperature": 0.7,
    "max_tokens": 2048,
}

# 全局默认配置：执行的流程配方
DEFAULT_RECIPE_TYPE = RecipeType.MEDICAL_REASONING_3_STEPS

def print_result_record(all_workflow_context: List[WorkflowContext]):
    # 打印流程记录与日志
    print_log("\n" + "🌟" * 30 + " WORKFLOW EXECUTION RECORDS " + "🌟" * 30 + "\n", prefix="[WORKFLOW]")
    for workflow_context in all_workflow_context:
        
        # 使用 getattr 获取可能发生变动的属性，确保不会轻易抛出边界异常
        workflow_id = getattr(workflow_context, "workflow_id", getattr(workflow_context, "get_workflow_id", lambda: "UNKNOWN")())
        
        print_log("\n\n" + "🌀" * 20 + f" WORKFLOW '{workflow_id}' BEGIN " + "🌀" * 20, prefix="[WORKFLOW]")
        
        # 打印每个 Task 的详细记录
        for task_record in workflow_context.get_all_records():
            task_config: TaskConfig = task_record["task_config"]
            task_context: TaskContext = task_record["task_context"]
            
            print_log("\n\n" + "🔽" * 30 + " NEW TASK " + "🔽" * 30, prefix="[WORKFLOW]")
            print_log(f"🚀 Task ID: {getattr(task_config, 'id', 'Unnamed')}  |  Type: [{task_config.type.value}]", prefix="[WORKFLOW]")
            print_log("=" * 72 + "\n", prefix="[WORKFLOW]")
            
            # 打印 Task 输入
            input_msgs = task_context.get("input", [])
            input_log = "\n" + "🟢" * 20 + " TASK INPUT MESSAGES " + "🟢" * 20 + "\n"
            for idx, msg in enumerate(input_msgs):
                role_str = getattr(msg.get('role'), 'value', msg.get('role', 'UNKNOWN'))
                input_log += f"\n{'━'*20} [Input Message {idx + 1}: {str(role_str).upper()}] {'━'*20}\n"
                input_log += f"{msg.get('content', '')}\n"
            print_log(input_log.strip(), prefix="[WORKFLOW]")
            
            # 打印 Task 输出
            output_msgs = task_context.get("output", [])
            output_log = "\n" + "🔵" * 20 + " TASK OUTPUT MESSAGES " + "🔵" * 20 + "\n"
            for idx, msg in enumerate(output_msgs):
                role_str = getattr(msg.get('role'), 'value', msg.get('role', 'UNKNOWN'))
                output_log += f"\n{'━'*20} [Output Message {idx + 1}: {str(role_str).upper()}] {'━'*20}\n"
                output_log += f"{msg.get('content', '')}\n"
            print_log("\n" + output_log.strip(), prefix="[WORKFLOW]")
            print_log("\n" + "🔼" * 30 + " TASK END " + "🔼" * 30 + "\n\n", prefix="[WORKFLOW]")
        
        print_log("\n" + "🛑" * 20 + f" WORKFLOW '{workflow_id}' END " + "🛑" * 20 + "\n\n", prefix="[WORKFLOW]")


async def run_workflow(
    dataset_kwargs: dict = DEFAULT_DATASET_CONFIG,
    evaluator_type_list: List[EvaluatorType] = DEFAULT_EVALUATOR_TYPE_LIST,
    chatbot_config: PoeChatbotConfig = DEFAULT_CHATBOT_CONFIG,
    recipe_type: RecipeType = DEFAULT_RECIPE_TYPE,
    custom_task_config_list: Optional[List[TaskConfig]] = None,
):
    """工作流核心执行函数，提供可以从外部注入参数的接口。
    
    如果不传入参数，将默认使用本文件顶部的全局 DEFAULT 变量。
    """
    
    # 1. 拆解并构建数据集配置（这里简单通过字典构造单例给列表）
    dataset_config_list = [
        DatasetConfig(
            dataset_type=dataset_kwargs.get("dataset_type", DatasetType.MED_QA),
            num_of_questions=dataset_kwargs.get("num_of_questions", 4),
        ),
    ]

    # 2. 根据配方生成任务链（TaskConfigs）
    # 如果允许外部提供了自定义的 task_config_list 则优先使用
    if custom_task_config_list is not None:
        task_config_list = custom_task_config_list
    else:
        recipe = RecipeFactory.get_recipe(
            recipe_type=recipe_type,
            chatbot_config=chatbot_config,
        )
        task_config_list = recipe.build_task_configs()

    # 3. 创建工作流实例
    workflow = Workflow(
        name="Medical Reasoning Workflow Demo",
        task_config_list=task_config_list,
        dataset_config_list=dataset_config_list,
        evaluator_type_list=evaluator_type_list,
    )

    # 直接包裹主执行与日志输出逻辑，不需要过度抓取边界异常
    try:
        # 执行工作流全流程
        print_log("Running workflow...", prefix="[WORKFLOW]")
        all_workflow_context = await workflow.run()
        
        print_result_record(all_workflow_context)
    except Exception as e:
        print_log(f"Error occurred: {e}", prefix="[WORKFLOW]")
        raise


async def main():
    """程序主入口：提供服务化前最后一次以脚本运行的方式。"""
    # 调用主函数不传入参数，将以定义的 Default 全局变量执行
    await run_workflow()


if __name__ == "__main__":
    asyncio.run(main())
