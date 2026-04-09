import uuid
from enum import Enum
from typing import List, Dict
from pydantic import BaseModel, Field


# Prompt
class PromptType(str, Enum):
    """提示词组织方式。"""
    STRUCTURED = "structured"
    COT = "chain_of_thought"
    SELF_REFINE = "self_refine"

class PromptTemplate(BaseModel):
    """提示词模板。"""
    # system: str
    # user: str
    text: str
    parameters: Dict[str, str] = Field(default_factory=dict) # for 模板参数填入
    tools: List[str] = Field(default_factory=list)