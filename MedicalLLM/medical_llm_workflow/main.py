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
from medical_llm_workflow.utils import print_log



def _temp_get_dataset_config() -> List[DatasetConfig]:
    """构建 demo 用数据集配置。"""
    # hard code for demo
    config = DatasetConfig(
        dataset_type=DatasetType.MED_QA,
        num_of_questions=4,
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
        "model": PoeChatbotModel.GPT_5_4_NANO,
        "temperature": 0.7,
        "max_tokens": 2048,
    }
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
        print_log("Running workflow...", prefix="[WORKFLOW]")
        all_workflow_context = await workflow.run()

        # 打印结果
        print_log("\n" + "🌟" * 30 + " WORKFLOW EXECUTION RECORDS " + "🌟" * 30 + "\n", prefix="[WORKFLOW]")
        for workflow_context in all_workflow_context:
            print_log("\n\n" + "🌀" * 20 + f" WORKFLOW '{workflow_context.get_workflow_id()}' BEGIN " + "🌀" * 20, prefix="[WORKFLOW]")
            for task_record in workflow_context.get_all_records():
                task_config: TaskConfig = task_record["task_config"]
                task_context: TaskContext = task_record["task_context"]
                
                print_log("\n\n" + "🔽" * 30 + " NEW TASK " + "🔽" * 30, prefix="[WORKFLOW]")
                print_log(f"🚀 Task ID: {getattr(task_config, 'id', 'Unnamed')}  |  Type: [{task_config.type.value}]", prefix="[WORKFLOW]")
                print_log("=" * 72 + "\n", prefix="[WORKFLOW]")
                
                # 构建输入日志
                input_msgs = task_context.get("input", [])
                input_log = "\n" + "🟢" * 20 + " TASK INPUT MESSAGES " + "🟢" * 20 + "\n"
                for idx, msg in enumerate(input_msgs):
                    role_str = getattr(msg.get('role'), 'value', msg.get('role', 'UNKNOWN'))
                    input_log += f"\n{'━'*20} [Input Message {idx + 1}: {str(role_str).upper()}] {'━'*20}\n"
                    input_log += f"{msg.get('content', '')}\n"
                print_log(input_log.strip(), prefix="[WORKFLOW]")
                
                # 构建输出日志
                output_msgs = task_context.get("output", [])
                output_log = "\n" + "🔵" * 20 + " TASK OUTPUT MESSAGES " + "🔵" * 20 + "\n"
                for idx, msg in enumerate(output_msgs):
                    role_str = getattr(msg.get('role'), 'value', msg.get('role', 'UNKNOWN'))
                    output_log += f"\n{'━'*20} [Output Message {idx + 1}: {str(role_str).upper()}] {'━'*20}\n"
                    output_log += f"{msg.get('content', '')}\n"
                print_log("\n" + output_log.strip(), prefix="[WORKFLOW]")
                print_log("\n" + "🔼" * 30 + " TASK END " + "🔼" * 30 + "\n\n", prefix="[WORKFLOW]")
            
            print_log("\n" + "🛑" * 20 + f" WORKFLOW '{workflow_context.workflow_id}' END " + "🛑" * 20 + "\n\n", prefix="[WORKFLOW]")

    except Exception as e:
        print_log(f"Error occurred: {e}", prefix="[WORKFLOW]")
        raise


async def main():
    """程序主入口：运行 demo 工作流。"""
    await _temp_create_and_run_workflow()


if __name__ == "__main__":
    asyncio.run(main())
