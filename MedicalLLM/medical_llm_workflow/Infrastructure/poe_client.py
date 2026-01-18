"""Poe API 客户端，用于调用 Poe 官方 chatbot API。"""
from typing import List
import fastapi_poe as fp
from os import getenv

from medical_llm_workflow.schemas import ConversationMessage, PoeClientConfig, PoeChatbotConfig


class PoeClient:
    """Poe API 客户端，负责与 Poe API 交互。"""

    def __init__(self, config: PoeClientConfig):
        """
        初始化 Poe API 客户端。

        Args:
            api_config: Poe API 配置
        """
        self.config = config

    async def call_chatbot(
        self,
        messages: List[ConversationMessage],
        chatbot_config: PoeChatbotConfig,
    ) -> str:
        """
        调用 Poe chatbot API。

        Args:
            messages: 对话消息列表
            chatbot_config: 聊天机器人配置

        Returns:
            模型返回的完整文本响应
        """
        if fp is None:
            raise ImportError(
                "fastapi-poe is required. Install it with: pip install fastapi-poe"
            )
        
        # 将 ConversationMessage 转换为 fastapi_poe.ProtocolMessage
        fp_messages = [
            fp.ProtocolMessage(role=msg.role, content=msg.content) for msg in messages
        ]

        # 调用 Poe API
        chunks = []
        try:
            async for part in fp.stream_request(
                fp.QueryRequest(query=fp_messages),
                bot_name=chatbot_config.model.value,
                api_key=self.config.api_key,
            ):
                if part.text:
                    chunks.append(part.text)
        except Exception as e:
            raise RuntimeError(f"Failed to call Poe API: {e}") from e

        return "".join(chunks)


_api_key = getenv("POE_API_KEY", "YOUR_API_KEY")
if _api_key == "YOUR_API_KEY":
    print("Warning: Please set POE_API_KEY environment variable or update the code.")

_client_config = PoeClientConfig(api_key=_api_key)
_poe_client_instance = PoeClient(_client_config)


def get_client_instance() -> PoeClient: # TODO: 之后得泛化一些，支持其他类型的 client
    """创建并返回 PoeClient 实例。"""
    return _poe_client_instance