"""Recipe 工厂：统一管理 recipe 注册与创建。"""
from typing import Dict

from medical_llm_workflow.Domain.recipes.recipe import Recipe
from medical_llm_workflow.Domain.recipes.models import RecipeType
from medical_llm_workflow.Domain.recipes.all_recipes.medical_reasoning_3_steps_recipe import (
	MedicalReasoning3StepsRecipe,
)


class RecipeFactory:
	"""Recipe 工厂。"""

	_recipes: Dict[RecipeType, Recipe] = {
		RecipeType.MEDICAL_REASONING_3_STEPS: MedicalReasoning3StepsRecipe(),
		# RecipeType.MEDICAL_REASONING_FAST_2_STEPS: MedicalReasoningFast2StepsRecipe(),
		# RecipeType.MEDICAL_REASONING_ITERATIVE_4_STEPS: MedicalReasoningIterative4StepsRecipe(),
	}

	@classmethod
	def get_recipe(cls, recipe_type: RecipeType) -> Recipe:
		"""获取 recipe 实例。"""
		recipe = cls._recipes.get(recipe_type)
		if recipe is None:
			raise ValueError(f"Unsupported recipe type: {recipe_type}")
		return recipe

	# @classmethod
	# def list_recipes(cls) -> List[RecipeMeta]:
	# 	"""返回所有可用 recipe 的元信息。"""
	# 	return [recipe.meta for recipe in cls._recipes.values()]

	# @classmethod
	# def create_task_configs(
	# 	cls,
	# 	recipe_type: RecipeType,
	# 	chatbot_config: PoeChatbotConfig,
	# ) -> List[TaskConfig]:
	# 	"""根据 recipe 直接生成任务配置列表。"""
	# 	recipe = cls.get_recipe(recipe_type)
	# 	return recipe.build_task_configs(chatbot_config)
