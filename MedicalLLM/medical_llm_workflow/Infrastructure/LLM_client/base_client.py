"""LLM 客户端抽象基类与通用工具。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from medical_llm_workflow.schemas.models import ConversationMessage
from .models import BaseChatbotConfig


class BaseLLMClient(ABC):
    """统一 LLM 客户端协议。"""

    client_name: str = "base"
    API_NAME: str = None

    @abstractmethod
    async def call_chatbot(
        self,
        messages: List[ConversationMessage],
        chatbot_config: BaseChatbotConfig,
    ) -> str:
        """调用模型并返回纯文本响应。"""

    # @classmethod
    # def get_client_name(cls):
    #     """返回客户端名称。"""
    #     api_key = getenv(cls.API_NAME)
    #     if not api_key:
    #         raise RuntimeError("POE_KEY is missing. Please set POE_KEY in environment variables.")
            
    #     return cls.client_name
    