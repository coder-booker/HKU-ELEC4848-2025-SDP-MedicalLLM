"""GLM API 客户端封装层。"""
from __future__ import annotations

import asyncio
import json
from os import getenv
from typing import List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from medical_llm_workflow.meta_config.meta_config import meta_settings
from medical_llm_workflow.schemas.models import ConversationMessage
from medical_llm_workflow.Infrastructure.LLM_client.models import GLMChatbotConfig

from ..base_client import BaseLLMClient


# TODO 先暂时不使用，只用POE
class GLMClient(BaseLLMClient):
    """GLM 客户端（OpenAI-compatible HTTP API）。"""

    client_name = "glm"
    base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    def __init__(self):
        key_name = f"{GLMClient.client_name.upper()}_KEY"
        self.api_key = getenv(key_name)

    async def call_chatbot(
        self,
        messages: List[ConversationMessage],
        chatbot_config: GLMChatbotConfig,
    ) -> str:
        if meta_settings.debug:
            return "This is a fake GLM response."

        return await asyncio.to_thread(self._call_chatbot_sync, messages, chatbot_config)

    def _call_chatbot_sync(self, messages: List[ConversationMessage], chatbot_config: GLMChatbotConfig) -> str:
        glm_messages = [{"role": msg["role"].value, "content": msg["content"]} for msg in messages]
        requested_model = str(chatbot_config.model.value)
        model_name = requested_model if requested_model.startswith("glm") else "glm-4.5"
        payload = {
            "model": model_name,
            "messages": glm_messages,
            "temperature": chatbot_config.temperature,
            "max_tokens": chatbot_config.max_tokens,
        }

        req = Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8")
        except HTTPError as e:
            raise RuntimeError(f"GLM API HTTP error: {e.code} {e.reason}") from e
        except URLError as e:
            raise RuntimeError(f"GLM API URL error: {e.reason}") from e

        data = json.loads(body)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"Unexpected GLM response: {body}") from e


def build_glm_client() -> GLMClient:
    return GLMClient()
