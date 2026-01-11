from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    """Prompt 模板"""
    system: str  # system prompt
    user: str    # user 部分模板（可含变量如 {input}）
    instructions: Optional[str] = None  # 额外指令