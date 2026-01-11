from dataclasses import dataclass
from typing import List
from enum import Enum
import fastapi_poe as fp
from Context import ConversationMessage


@dataclass
class PoeAPIConfig:
    """Poe API 配置"""
    api_key: str
    base_url: str = "https://api.poe.com"

class PoeChatbotModel(Enum):
    """枚举：Poe 支持的聊天机器人"""
    GPT_4_1 = "GPT-4.1"
    GPT_5_1 = "GPT-5.1"
    CLAUDE_3 = "Claude-3.5-Sonnet"

@dataclass
class PoeChatbotConfig:
    """单个聊天机器人的配置"""
    model: PoeChatbotModel
    temperature: float = 0.7
    max_tokens: int = 2048
    
# ============================================================================
# 2. POE API CLIENT
# ============================================================================

class PoeAPIClient:
    """
    Poe API 客户端，封装对 Poe 的所有调用
    """

    def __init__(self, config: PoeAPIConfig):
        self.config = config

    async def call_chatbot(
        self,
        messages: List[ConversationMessage],
        chatbot_config: PoeChatbotConfig,
    ) -> str:
        """
        调用 Poe 的单个聊天机器人

        Args:
            messages: 对话历史
            chatbot_config: 聊天机器人配置

        Returns:
            模型的返回文本
        """
        # 将 ConversationMessage 转换为 fp.ProtocolMessage
        fp_messages = [
            fp.ProtocolMessage(role=msg.role, content=msg.content)
            for msg in messages
        ]

        chunks = []
        async for part in fp.stream_request(
            fp.QueryRequest(query=fp_messages),
            bot_name=chatbot_config.model.value,
            api_key=self.config.api_key,
        ):
            if part.text:
                chunks.append(part.text)

        return "".join(chunks)