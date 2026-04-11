"""三步医学推理 recipe。

步骤：
1) Problem Representation
2) Hypothesis Generation
3) Hypothesis Evaluation
"""
from typing import List

from medical_llm_workflow.Domain.tasks.models import TaskConfig, TaskType, MedicalType
from medical_llm_workflow.Domain.recipes.recipe import Recipe
from medical_llm_workflow.Domain.recipes.models import RecipeMeta, RecipeType
from medical_llm_workflow.Domain.prompts.models import PromptTemplate
from medical_llm_workflow.Domain.tasks.all_tasks.problem_representation_task import ProblemRepresentationTask
from medical_llm_workflow.Domain.tasks.all_tasks.hypothesis_generation_task import HypothesisGenerationTask
from medical_llm_workflow.Domain.tasks.all_tasks.hypothesis_evaluation_task import HypothesisEvaluationTask


class MedicalReasoning3StepsRecipe(Recipe):
    """经典三步临床推理模板。"""

    meta = RecipeMeta(
        recipe_type=RecipeType.MEDICAL_REASONING_3_STEPS,
        name="Medical Reasoning - 3 Steps",
        description="问题表征 -> 假设生成 -> 假设评估",
    )

    def build_task_configs(self) -> List[TaskConfig]:
        
        return [
            TaskConfig(
                id="Problem Representation Task",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.PROBLEM_REPRESENTATION,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[],
                prompt_template=PromptTemplate(text=ProblemRepresentationTask.PROMPT_TEMPLATE),
            ),
            TaskConfig(
                id="Hypothesis Generation Task",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.HYPOTHESIS_GENERATION,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[],
                prompt_template=PromptTemplate(text=HypothesisGenerationTask.PROMPT_TEMPLATE),
            ),
            TaskConfig(
                id="Hypothesis Evaluation Task",
                type=TaskType.SINGLE_AGENT,
                medical_type=MedicalType.HYPOTHESIS_EVALUATION,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[],
                prompt_template=PromptTemplate(text=HypothesisEvaluationTask.PROMPT_TEMPLATE),
            ),
        ]

