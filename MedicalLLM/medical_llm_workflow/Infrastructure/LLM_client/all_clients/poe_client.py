"""Poe API 客户端封装层。

该模块负责：
1) 将内部消息模型转换为 fastapi_poe 协议消息；
2) 统一处理流式响应拼接；
3) 提供单例客户端供任务层复用。
"""
from typing import List
import fastapi_poe as fp
from os import getenv

from medical_llm_workflow.schemas.models import ConversationMessage
from medical_llm_workflow.meta_config.meta_config import meta_settings
from ..base_client import BaseLLMClient
from ..models import PoeChatbotConfig


class PoeClient(BaseLLMClient):
    """Poe API 客户端，负责与 Poe API 交互。"""

    client_name = "poe"
    base_url: str = "https://api.poe.com"
    
    def __init__(self):
        key_name = f"{PoeClient.client_name.upper()}_KEY"
        self.api_key = getenv(key_name)

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
        # 将内部消息对象转换为 Poe SDK 协议消息。
        fp_messages = []
        for msg in messages:
            fp_messages.append(fp.ProtocolMessage(role=msg["role"].value, content=msg["content"]))

        # 调用 Poe API
        chunks = []
        if meta_settings.debug:
            # fake response for debug
            chunks.append("This")
            chunks.append(" is")
            chunks.append(" a")
            chunks.append(" fake")
            chunks.append(" response.")
            return "".join(chunks)
        
        try:
            # 逐块接收流式 token，并在最后拼接为完整文本。
            async for part in fp.stream_request(
                fp.QueryRequest(query=fp_messages),
                bot_name=chatbot_config.model.value,
                api_key=self.api_key,
            ):
                if part.text:
                    chunks.append(part.text)
        except Exception as e:
            raise RuntimeError(f"Failed to call Poe API: {e}") from e
        
        return "".join(chunks)


def build_poe_client() -> PoeClient:
    return PoeClient()

