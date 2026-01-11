from __future__ import annotations

import base64
import os
from typing import Any, Dict, List, Optional, Union, Iterable

import openai
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator


# ===== 配置模型，用于类型设定与检查 =====

class PoeConfig(BaseModel):
    """
    封装 Poe API 所需的基础配置，使用 pydantic 做类型与值校验。
    """
    api_key: str = Field(default_factory=lambda: os.environ.get("POE_API_KEY", ""))
    base_url: str = Field(default="https://api.poe.com/v1")
    model: str = Field(default="Claude-Sonnet-4")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    stream: bool = Field(default=False)

    # 你可以根据需要补充更多 OpenAI Chat Completions 的字段
    # 如：stop, logprobs, tools, tool_choice 等

    @field_validator("api_key")
    @classmethod
    def api_key_must_not_be_empty(cls, v: str) -> str:
        if not v:
            raise ValueError(
                "POE_API_KEY is empty. "
                "请在环境变量中设置 POE_API_KEY，或在创建 PoeConfig 时显式传入 api_key"
            )
        return v


# ===== 消息与文件输入模型 =====

class ChatMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: Union[str, List[Dict[str, Any]]]


class FileInput(BaseModel):
    """
    把文件封装成 base64 data URL，便于直接作为 messages.content 里的元素。
    """
    filename: str
    mime_type: str
    data_base64: str

    @classmethod
    def from_path(cls, path: str, mime_type: Optional[str] = None) -> "FileInput":
        # 简单根据扩展名猜 MIME；生产环境可用 mimetypes 库或更精细映射
        ext = os.path.splitext(path)[1].lower()
        if mime_type is None:
            if ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            elif ext == ".png":
                mime_type = "image/png"
            elif ext == ".pdf":
                mime_type = "application/pdf"
            elif ext in [".mp3"]:
                mime_type = "audio/mp3"
            elif ext in [".wav"]:
                mime_type = "audio/wav"
            elif ext in [".mp4"]:
                mime_type = "video/mp4"
            else:
                # 默认按二进制文件处理
                mime_type = "application/octet-stream"

        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        return cls(
            filename=os.path.basename(path),
            mime_type=mime_type,
            data_base64=b64,
        )

    def to_message_block(self) -> Dict[str, Any]:
        """
        转换为 Poe/OpenAI chat.completions 所需的 file 类型 block。
        """
        return {
            "type": "file",
            "file": {
                "filename": self.filename,
                "file_data": f"data:{self.mime_type};base64,{self.data_base64}",
            },
        }


class ImageUrlInput(BaseModel):
    """
    对于已上传到公网可访问 URL 的图片，而不是本地文件。
    """
    url: str

    def to_message_block(self) -> Dict[str, Any]:
        return {
            "type": "image_url",
            "image_url": {
                "url": self.url
            },
        }


# ===== Chatbot 类 =====

class PoeChatbot:
    """
    基于 Poe OpenAI-Compatible API 的通用 Chatbot 封装。

    - 支持配置管理（get/set/update/delete）
    - 支持非流式与流式对话
    - 支持传入多模态文件（图片、PDF、音频、视频等）和远程图片 URL
    """

    def __init__(self, config: Optional[PoeConfig] = None) -> None:
        self.config = config or PoeConfig()
        self._client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )

    # ==== 配置相关：增删改查 ====

    def get_config(self) -> PoeConfig:
        """
        读取当前完整配置（PoeConfig）。
        """
        return self.config

    def get_config_key(self, key: str) -> Any:
        """
        读取某个配置项的值。
        """
        if not hasattr(self.config, key):
            raise KeyError(f"配置项 '{key}' 不存在")
        return getattr(self.config, key)

    def set_config_key(self, key: str, value: Any) -> None:
        """
        设置/修改单个配置项。调用 pydantic 的校验。
        """
        if not hasattr(self.config, key):
            raise KeyError(f"配置项 '{key}' 不存在")
        # 使用 model_copy(update=...) 触发校验
        new_config = self.config.model_copy(update={key: value})
        self.config = new_config
        # 更新 client，如果改了 api_key 或 base_url
        if key in ("api_key", "base_url"):
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )

    def update_config(self, **kwargs: Any) -> None:
        """
        批量更新多个配置项。
        """
        unknown_keys = [k for k in kwargs.keys() if not hasattr(self.config, k)]
        if unknown_keys:
            raise KeyError(f"以下配置项不存在: {unknown_keys}")
        new_config = self.config.model_copy(update=kwargs)
        self.config = new_config
        # 如果有 api_key/base_url 变化，重建 client
        if any(k in kwargs for k in ("api_key", "base_url")):
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )

    def delete_config_key(self, key: str) -> None:
        """
        删除配置项的值（这里简单实现为恢复默认，而不是彻底删除字段）。
        真正“删除字段”在 pydantic 模型中意义不大，所以用 reset 语义更合理。
        """
        if not hasattr(self.config, key):
            raise KeyError(f"配置项 '{key}' 不存在")
        # 使用默认重建：构造一个新的默认 config，并用当前配置覆盖除该 key 外的字段
        default_config = PoeConfig()
        data = self.config.model_dump()
        data.pop(key, None)
        # 先用默认，再 update 剩下字段
        intermediate = default_config.model_copy(update=data)
        self.config = intermediate
        if key in ("api_key", "base_url"):
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )



    # ==== 构建消息 & 文件输入的公共入口 ====

    def build_message_with_files(
        self,
        text: str,
        files: Optional[List[FileInput]] = None,
        image_urls: Optional[List[ImageUrlInput]] = None,
    ) -> ChatMessage:
        """
        构建一个包含文本 + 多个附件(file/image_url) 的 user 消息。
        """
        content_blocks: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": text,
            }
        ]

        if image_urls:
            for img in image_urls:
                content_blocks.append(img.to_message_block())

        if files:
            for f in files:
                content_blocks.append(f.to_message_block())

        return ChatMessage(role="user", content=content_blocks)

    # ==== 对话：非流式 ====

    def chat(
        self,
        messages: List[ChatMessage],
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        非流式对话，返回完整的字符串回复。

        参数:
            messages: ChatMessage 列表，必须包含 role 和 content。
            extra_body: 用于传入文档里的自定义参数，例如：
                        {"web_search": True, "thinking_level": "high"}
        """
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": [m.model_dump() for m in messages],
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
        }
        if self.config.max_tokens is not None:
            payload["max_tokens"] = self.config.max_tokens
        if extra_body:
            payload["extra_body"] = extra_body

        chat = self._client.chat.completions.create(**payload)
        return chat.choices[0].message.content  # type: ignore[return-value]

    # ==== 对话：流式 ====

    def chat_stream(
        self,
        messages: List[ChatMessage],
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Iterable[str]:
        """
        流式对话，返回一个迭代器，每次 yield 一小段文本。
        """
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": [m.model_dump() for m in messages],
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": True,
        }
        if self.config.max_tokens is not None:
            payload["max_tokens"] = self.config.max_tokens
        if extra_body:
            payload["extra_body"] = extra_body

        stream = self._client.chat.completions.create(**payload)
        for chunk in stream:
            delta = chunk.choices[0].delta  # type: ignore[assignment]
            if delta and getattr(delta, "content", None):
                yield delta.content

    # ==== 简单封装：只输入文本 ====

    def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        stream: Optional[bool] = None,
    ) -> Union[str, Iterable[str]]:
        """
        对于最常见的场景：只给一个 user 文本，可选 system，快速发问。

        stream:
          - True  时使用流式输出，返回迭代器
          - False 时使用非流式输出，返回字符串
          - None  时使用当前 config.stream 的设定
        """
        if stream is None:
            stream = self.config.stream

        messages: List[ChatMessage] = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=prompt))

        if stream:
            return self.chat_stream(messages=messages, extra_body=extra_body)
        else:
            return self.chat(messages=messages, extra_body=extra_body)