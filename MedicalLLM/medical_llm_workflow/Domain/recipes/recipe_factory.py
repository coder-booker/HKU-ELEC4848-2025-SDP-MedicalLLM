"""Recipe 工厂：统一管理 recipe 注册与创建。"""
from typing import Dict, Callable

from medical_llm_workflow.Domain.recipes.recipe import Recipe
from medical_llm_workflow.Domain.recipes.models import RecipeType
from medical_llm_workflow.Domain.recipes.all_recipes.medical_reasoning_3_steps_recipe import (
    MedicalReasoning3StepsRecipe,
)
from medical_llm_workflow.Domain.recipes.all_recipes.two_stage_verification_recipe import (
    TwoStageVerificationRecipe,
)
from medical_llm_workflow.Infrastructure.LLM_client import BaseChatbotConfig



RecipeCallable = Callable[[BaseChatbotConfig], Recipe]  # 定义一个类型别名，表示无参数返回 Recipe 实例的可调用对象
class RecipeFactory:
    """Recipe 工厂。"""

    _recipes: Dict[RecipeType, RecipeCallable] = {
        RecipeType.MEDICAL_REASONING_3_STEPS: MedicalReasoning3StepsRecipe,
        RecipeType.TWO_STAGE_VERIFICATION: TwoStageVerificationRecipe,
        # RecipeType.MEDICAL_REASONING_FAST_2_STEPS: MedicalReasoningFast2StepsRecipe(),
        # RecipeType.MEDICAL_REASONING_ITERATIVE_4_STEPS: MedicalReasoningIterative4StepsRecipe(),
    }

    @classmethod
    def get_recipe(
        cls,
        recipe_type: RecipeType,
        chatbot_config: BaseChatbotConfig,
    ) -> Recipe:
        """获取 recipe 实例。"""
        recipe_cls = cls._recipes.get(recipe_type)
        if recipe_cls is None:
            raise ValueError(f"指定的 RecipeType: {recipe_type} 加载失败，找不到工厂映射，请检查代码注入。")
        
        recipe = recipe_cls(chatbot_config=chatbot_config) # 目前先直接实例化，之后如果需要的话再改成单例模式

        return recipe

    # @classmethod
    # def list_recipes(cls) -> List[RecipeMeta]:
    #     """返回所有可用 recipe 的元信息。"""
    #     return [recipe.meta for recipe in cls._recipes.values()]

    # @classmethod
    # def create_task_configs(
    #     cls,
    #     recipe_type: RecipeType,
    #     chatbot_config: PoeChatbotConfig,
    # ) -> List[TaskConfig]:
    #     """根据 recipe 直接生成任务配置列表。"""
    #     recipe = cls.get_recipe(recipe_type)
    #     return recipe.build_task_configs(chatbot_config)
