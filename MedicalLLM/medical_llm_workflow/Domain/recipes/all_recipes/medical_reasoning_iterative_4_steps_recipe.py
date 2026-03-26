"""四步迭代医学推理 recipe。

步骤：
1) Problem Representation
2) Hypothesis Generation
3) Hypothesis Generation (Refine)
4) Hypothesis Evaluation

通过二次假设生成实现轻量迭代。
"""
from typing import List

from medical_llm_workflow.schemas.models import PoeChatbotConfig
from medical_llm_workflow.Domain.tasks.models import TaskConfig, TaskType, MedicalType
from medical_llm_workflow.Domain.recipes.recipe import Recipe
from medical_llm_workflow.Domain.recipes.models import RecipeMeta, RecipeType


class MedicalReasoningIterative4StepsRecipe(Recipe):
    """带迭代生成环节的临床推理模板。"""

    meta = RecipeMeta(
        recipe_type=RecipeType.MEDICAL_REASONING_ITERATIVE_4_STEPS,
        name="Medical Reasoning - Iterative 4 Steps",
        description="问题表征 -> 假设生成 -> 再生成 -> 假设评估",
    )

    def build_task_configs(self, chatbot_config: PoeChatbotConfig) -> List[TaskConfig]:
        return [
            TaskConfig(
                id="Problem Representation 1",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.PROBLEM_REPRESENTATION,
                chatbot_config=chatbot_config,
                connect_to=["Hypothesis Generation 1"],
                prompt_args_map={"question": "{{QUESTION}}"},
            ),
            TaskConfig(
                id="Hypothesis Generation 1",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.HYPOTHESIS_GENERATION,
                chatbot_config=chatbot_config,
                connect_to=["Hypothesis Generation 2"],
            ),
            TaskConfig(
                id="Hypothesis Generation 2",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.HYPOTHESIS_GENERATION,
                chatbot_config=chatbot_config,
                connect_to=["Hypothesis Evaluation 1"],
            ),
            TaskConfig(
                id="Hypothesis Evaluation 1",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.HYPOTHESIS_EVALUATION,
                chatbot_config=chatbot_config,
            ),
        ]
