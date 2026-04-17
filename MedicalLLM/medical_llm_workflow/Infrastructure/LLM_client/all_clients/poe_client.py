"""Poe API 客户端封装层。

该模块负责：
1) 将内部消息模型转换为 fastapi_poe 协议消息；
2) 统一处理流式响应拼接；
3) 提供单例客户端供任务层复用。
"""
from typing import List
import fastapi_poe as fp
import asyncio

from medical_llm_workflow.schemas.models import ConversationMessage
from ..base_client import BaseLLMClient
from ..models import PoeChatbotConfig
from medical_llm_workflow.app_settings import AppSettings
from medical_llm_workflow.utils import print_log



class PoeClient(BaseLLMClient):
    """Poe API 客户端，负责与 Poe API 交互。"""

    client_name = "poe"
    base_url: str = "https://api.poe.com"
    
    def __init__(self):
        key_name = f"{PoeClient.client_name.upper()}_KEY"
        self.api_key = AppSettings.POE_KEY
        # print_log(f"Initialized PoeClient with API key from env var '{key_name}'", prefix="[LLM]", debug=True)

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
            fp_messages.append(
                fp.ProtocolMessage(
                    role=msg["role"],
                    content=msg["content"]
                )
            )

        # 调用 Poe API
        chunks = []
        if not AppSettings.REAL_LLM_RESPONSE:
            # fake response for debug
            chunks.append("This")
            chunks.append(" is")
            chunks.append(" a")
            chunks.append(" fake")
            chunks.append(" response.")
            return "".join(chunks)
        
        print_log("Calling Poe API...", prefix="[LLM]", debug=True)
        
        max_retries = 3
        timeout_seconds = 30  # 设置一个宽容的单次调用超时阈值
        
        for attempt in range(max_retries):
            chunks = []
            try:
                # 包装流式请求为单体协程，以适用 asyncio.wait_for 设置超时拦截网络挂起
                async def _fetch_stream():
                    async for part in fp.get_bot_response(
                        messages=fp_messages,
                        bot_name=chatbot_config["model"],
                        api_key=self.api_key,
                    ):
                        if part.text:
                            chunks.append(part.text)

                await asyncio.wait_for(_fetch_stream(), timeout=timeout_seconds)
                full_response = "".join(chunks)
                break
                
            except asyncio.TimeoutError:
                err_msg = f"Attempt {attempt + 1}/{max_retries} timed out after {timeout_seconds}s."
                print_log(err_msg, prefix="[LLM]", debug=True)
            except Exception as e:
                err_msg = f"Attempt {attempt + 1}/{max_retries} failed with error: {str(e)}"
                print_log(err_msg, prefix="[LLM]", debug=True)

            # 若还未到最后一次尝试，则短暂停顿后重发请求
            if attempt < max_retries - 1:
                print_log("Retrying in 2 seconds...", prefix="[LLM]")
                await asyncio.sleep(2)
            else:
                # 所有重试次数用尽，抛出异常阻断当前任务
                raise RuntimeError(f"Failed to call Poe API after {max_retries} attempts.")
        
        return full_response


def build_poe_client() -> PoeClient:
    return PoeClient()

