"""核心数据模型定义。

该模块统一定义工作流所需的配置、消息协议、任务结构与 benchmark 协议，
供 Domain / Service / Infrastructure 各层共享，避免跨层字段漂移。
"""
from enum import Enum
from typing_extensions import TypedDict


# class EZSerializableModel(BaseModel):
#     @model_serializer(mode='wrap')
#     def serialize_none_as_empty(self, handler):
#         # handler(self) 会先将模型正常序列化为字典
#         dumped = handler(self)
#         # 然后将结果中的 None 替换为 ""
#         if isinstance(data, dict):
#             return {
#                 k: ("" if v is None else replace_none_with_empty_str(v)) 
#                 for k, v in data.items()
#             }
#         elif isinstance(data, list):
#             return [replace_none_with_empty_str(item) for item in data]
#         return data
#         return replace_none_with_empty_str(dumped)


# language
class LanguageType(str, Enum): # TODO：现在先不允许选语言，之后再搞
    """支持的语言枚举。"""
    EN = "en"
    ZH = "zh"



# Conversation Message，我们自己拓展的聊天记录模型，实际上不止承载了和 AI 的聊天记录，还承载了一些系统的记录
class ConversationMessageStatus(str, Enum):
    """消息在工作流中的状态。"""
    NORMAL = "normal"
    COMPLETED = "completed"
    FAILED = "failed"

# 供 fast api 使用的 role 类型
class ConversationMessageRole(str, Enum):
    """消息角色（与下游 API role 对齐）。"""
    # system, user, bot, tool
    SYSTEM = "system"
    USER = "user"
    BOT = "bot"
    TOOL = "tool"
    
class ConversationMessage(TypedDict): # TODO：之后可以配置化，让重复内容从一个唯一池子中获取
    """对话消息。"""
    # id: uuid.UUID = Field(default_factory=uuid.uuid4)
    role: ConversationMessageRole
    content: str
    status: ConversationMessageStatus
