"""核心数据模型定义。

该模块统一定义工作流所需的配置、消息协议、任务结构与 benchmark 协议，
供 Domain / Service / Infrastructure 各层共享，避免跨层字段漂移。
"""
from dataclasses import dataclass, field
import uuid
from enum import Enum
from typing import Dict, List, Optional, Protocol
from pydantic import BaseModel, Field



# language
class LanguageType(Enum): # TODO：现在先不允许选语言，之后再搞
    """支持的语言枚举。"""
    EN = "en"
    ZH = "zh"



# Conversation Message，我们自己拓展的聊天记录模型，实际上不止承载了和 AI 的聊天记录，还承载了一些系统的记录
class ConversationMessageStatus(Enum):
    """消息在工作流中的状态。"""
    NORMAL = "normal"
    COMPLETED = "completed"
    FAILED = "failed"

# 供 fast api 使用的 role 类型
class ConversationMessageRole(Enum):
    """消息角色（与下游 API role 对齐）。"""
    # system, user, bot, tool
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    
class ConversationMessage(BaseModel): # TODO：之后可以配置化，让重复内容从一个唯一池子中获取
    """对话消息。"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    role: ConversationMessageRole
    content: str | Dict | List  # 兼容文本和结构化内容，例如 evaluation output 可能是一个 dict
    status: ConversationMessageStatus = ConversationMessageStatus.NORMAL
    
    def __str__(self):
        """格式化输出，方便在日志中查看消息来源和内容。"""
        return f"[Message-{self.id}]({self.role})({self.status}):\n{self.content}"
