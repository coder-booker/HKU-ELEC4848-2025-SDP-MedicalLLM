"""两步快速医学推理 recipe。

步骤：
1) Hypothesis Generation
2) Hypothesis Evaluation

适合快速试跑或低成本基线。
"""
from typing import List

from medical_llm_workflow.schemas.models import PoeChatbotConfig
from medical_llm_workflow.Domain.tasks.models import TaskConfig, TaskType, MedicalType
from medical_llm_workflow.Domain.recipes.recipe import Recipe
from medical_llm_workflow.Domain.recipes.models import RecipeMeta, RecipeType


class MedicalReasoningFast2StepsRecipe(Recipe):
    """快速两步临床推理模板。"""

    meta = RecipeMeta(
        recipe_type=RecipeType.MEDICAL_REASONING_FAST_2_STEPS,
        name="Medical Reasoning - Fast 2 Steps",
        description="假设生成 -> 假设评估（快速基线）",
    )

    def build_task_configs(self, chatbot_config: PoeChatbotConfig) -> List[TaskConfig]:
        return [
            TaskConfig(
                id="Hypothesis Generation 1",
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
