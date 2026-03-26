"""LLM 客户端工厂。"""
from __future__ import annotations

from collections.abc import Callable

from .base_client import BaseLLMClient
from .all_clients.glm_client import build_glm_client
from .all_clients.poe_client import build_poe_client
from .models import ChatbotType


class ClientFactory:
    """客户端工厂。"""

    _client_cache: dict[ChatbotType, BaseLLMClient] = {}
    _registry: dict[ChatbotType, Callable[[], BaseLLMClient]] = {
        ChatbotType.POE: build_poe_client,
        ChatbotType.GLM: build_glm_client,
    }

    @classmethod
    def register(
        cls,
        chatbot_type: ChatbotType,
        builder: Callable[[], BaseLLMClient],
    ) -> None:
        """注册自定义客户端构造器。"""
        cls._registry[chatbot_type] = builder

    # 外部一般不调用此方法，用 get_client_instance 就够了。
    @classmethod
    def create(
        cls,
        chatbot_type: ChatbotType,
    ) -> BaseLLMClient:
        """创建客户端实例。"""
        build_client = cls._registry.get(chatbot_type)
        if build_client is None:
            raise ValueError(f"Unsupported client type: {chatbot_type}")

        return build_client()

    @classmethod
    def get_client_instance(
        cls,
        chatbot_type: ChatbotType = ChatbotType.POE,
    ) -> BaseLLMClient:
        """按类型返回缓存客户端实例。"""
        if chatbot_type in cls._client_cache:
            return cls._client_cache[chatbot_type]

        # 使用工厂创建实例并写入缓存，避免重复初始化客户端。
        client = cls.create(chatbot_type)
        cls._client_cache[chatbot_type] = client
        return client
