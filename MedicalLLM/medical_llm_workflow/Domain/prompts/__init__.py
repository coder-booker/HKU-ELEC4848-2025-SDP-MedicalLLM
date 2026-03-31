"""提示词模块导出入口。"""
from .models import PromptType, PromptTemplate

# 统一对外暴露提示词工厂函数。
__all__ = [
    "PromptType",
    "PromptTemplate",
]

