"""三步医学推理 recipe。

步骤：
1) Problem Representation
2) Hypothesis Generation
3) Hypothesis Evaluation
"""
from typing import List

from medical_llm_workflow.schemas.models import PoeChatbotConfig
from medical_llm_workflow.Domain.tasks.models import TaskConfig, TaskType, MedicalType
from medical_llm_workflow.Domain.recipes.recipe import Recipe
from medical_llm_workflow.Domain.recipes.models import RecipeMeta, RecipeType


class MedicalReasoning3StepsRecipe(Recipe):
    """经典三步临床推理模板。"""

    meta = RecipeMeta(
        recipe_type=RecipeType.MEDICAL_REASONING_3_STEPS,
        name="Medical Reasoning - 3 Steps",
        description="问题表征 -> 假设生成 -> 假设评估",
    )

    def build_task_configs(self, chatbot_config: PoeChatbotConfig) -> List[TaskConfig]:
        return [
            TaskConfig(
                id="Problem Representation 1",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.PROBLEM_REPRESENTATION,
                chatbot_config=chatbot_config,
                # connect_to=["Hypothesis Generation 1"],
                # prompt_args_map={"question": "{{QUESTION}}"},
            ),
            TaskConfig(
                id="Hypothesis Generation 1",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.HYPOTHESIS_GENERATION,
                chatbot_config=chatbot_config,
            ),
            TaskConfig(
                id="Hypothesis Evaluation 1",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.HYPOTHESIS_EVALUATION,
                chatbot_config=chatbot_config,
            ),
        ]

