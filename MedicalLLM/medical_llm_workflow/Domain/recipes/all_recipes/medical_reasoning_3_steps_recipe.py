"""三步医学推理 recipe。

步骤：
1) Problem Representation
2) Hypothesis Generation
3) Hypothesis Evaluation
"""
from typing import List

from medical_llm_workflow.Domain.tasks.models import TaskConfig, TaskType
from medical_llm_workflow.Domain.recipes.recipe import Recipe
from medical_llm_workflow.Domain.recipes.models import RecipeMeta, RecipeType
from medical_llm_workflow.Domain.prompts.models import PromptTemplate


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
                chatbot_config=self.chatbot_config,
                input_msg_sources=[],
                prompt_template=PromptTemplate(
                    text="You are the “Clue Representation” agent in a clinical reasoning workflow.\nYour job is not to answer the question directly, but to convert the input patient case (in form of medical question) into a clear clinical clue representation for downstream agents.\n\nPatient Case:\n{{question_task}}\n"
                ),
            ),
            TaskConfig(
                id="Hypothesis Generation Task",
                type=TaskType.SINGLE_AGENT,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[],
                prompt_template=PromptTemplate(
                    text="You are the “Hypothesis Generation” agent in a clinical reasoning workflow.\nBased on the previous Problem Representation result, you must propose 3–5 plausible diagnostic/mechanistic hypotheses and provide key supporting and contradicting evidence for each, producing a candidate list for downstream evaluation.\n\nProblem Representation:\n{{Problem Representation Task}}\n"
                ),
            ),
            TaskConfig(
                id="Hypothesis Evaluation Task",
                type=TaskType.SINGLE_AGENT,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[],
                prompt_template=PromptTemplate(
                    text="You are the “Hypothesis Evaluation” agent in a clinical reasoning workflow. \nYour job is to compare and evaluate the candidate hypotheses and map them to the provided answer options, then select the final best answer. \nMake sure that the final answer you output strictly follows the provided answer options text. \nProblem Representation: \n{{Problem Representation Task}}\n\nHypothesis Generation: \n{{Hypothesis Generation Task}}\n"
                ),
            ),
        ]

