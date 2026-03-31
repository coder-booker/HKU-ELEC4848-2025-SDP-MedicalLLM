from __future__ import annotations
from enum import Enum
from typing_extensions import TypedDict
from pydantic import BaseModel


# LLM
class ChatbotType(str, Enum):
    """客户端类型。"""
    POE = "poe"
    GLM = "glm"

class BaseChatbotConfig(TypedDict):
    """单次模型调用参数配置。"""
    chatbot_type: ChatbotType
    model: PoeChatbotModel | GLMChatbotModel
    temperature: float
    max_tokens: int

# Poe
class PoeChatbotModel(str, Enum):
    """Poe 聊天机器人模型枚举。"""
    EMPTY_MODEL = "empty_model" # 占位符模型
    GPT_4_1 = "GPT-4.1"
    GPT_5_1 = "GPT-5.1"
    # 可根据需要添加更多模型

class PoeChatbotConfig(BaseChatbotConfig):
    """单次模型调用参数配置。"""
    model: PoeChatbotModel


# GLM
class GLMChatbotModel(str, Enum):
    """GLM 聊天机器人模型枚举。"""
    EMPTY_MODEL = "empty_model" # 占位符模型
    GLM_3_0 = "GLM-3.0"
    GLM_3_5 = "GLM-3.5"
    # 可根据需要添加更多模型

class GLMChatbotConfig(BaseChatbotConfig):
    """单次模型调用参数配置。"""
    model: GLMChatbotModel
