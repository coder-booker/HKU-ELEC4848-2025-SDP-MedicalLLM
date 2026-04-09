from enum import Enum
from dataclasses import dataclass


class RecipeType(str, Enum):
    """内置 recipe 类型。"""

    MEDICAL_REASONING_3_STEPS = "medical_reasoning_3_steps"
    # MEDICAL_REASONING_FAST_2_STEPS = "medical_reasoning_fast_2_steps"
    # MEDICAL_REASONING_ITERATIVE_4_STEPS = "medical_reasoning_iterative_4_steps"

@dataclass(frozen=True)
class RecipeMeta:
    """Recipe 元信息，用于展示和查询。"""

    recipe_type: RecipeType
    name: str
    description: str