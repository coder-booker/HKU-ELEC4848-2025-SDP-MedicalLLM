"""数据模型定义模块，使用 dataclasses 和 Enum 定义所有配置和上下文结构。"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field




# Poe
class PoeChatbotModel(Enum):
    """Poe 聊天机器人模型枚举。"""
    GPT_4_1 = "GPT-4.1"
    GPT_5_1 = "GPT-5.1"
    # 可根据需要添加更多模型

class PoeClientConfig(BaseModel):
    api_key: str
    base_url: str = "https://api.poe.com"

class PoeChatbotConfig(BaseModel):
    model: PoeChatbotModel
    temperature: float = 0.7
    max_tokens: int = 2048



# language
class LanguageType(Enum): # TODO：现在先不允许选语言，之后再搞
    """支持的语言枚举。"""
    EN = "en"
    ZH = "zh"



# Prompt
class PromptType(Enum):
    STRUCTURED = "structured"
    COT = "chain_of_thought"
    SELF_REFINE = "self_refine"

class PromptTemplate(BaseModel):    # TODO: 这个模板的model定义其实不太一致，这里的定义是类本身，而非 param，需要再调整
    """提示词模板。"""
    system: str
    user: str
    tools: Optional[List[str]] = None



# Conversation
class ConversationMessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ERROR = "error"
    
class ConversationMessage(BaseModel): # TODO：之后可以配置化，让重复内容从一个唯一池子中获取
    """对话消息。"""
    role: ConversationMessageRole
    content: str



# Task
class TaskType(Enum):
    SINGLE_AGENT = "single_agent"
    SELF_REFINE = "self_refine"
    # 后续可扩展：SELF_CONSISTENCY, MULTI_AGENT 等

class TaskContext(BaseModel):
    input: List[ConversationMessage]
    output: List[ConversationMessage]

class TaskConfig(BaseModel):
    """前端传入的任务配置。"""
    id: str
    type: TaskType
    context: TaskContext
    
    chatbot_config: PoeChatbotConfig
    # language: LanguageType = LanguageType.EN # 继承但可以覆盖工作流的语言设置
    max_retries: int = 3
    timeout: int = 60
    
    prompt: Optional[PromptTemplate] = None # will be dynamically generated

class TaskRecord(BaseModel):
    """记录在工作流上下文中的任务执行结果。"""
    task_config: TaskConfig
    task_context: TaskContext

# Workflow
class WorkflowConfig(BaseModel):
    """工作流配置。"""
    id: str
    name: str
    task_config_list: List[TaskConfig]
    language: LanguageType = LanguageType.EN # 整条工作流的语言

# class WorkflowContext:
#     """工作流上下文，存储整个工作流的执行状态。"""
#     workflow_id: str
#     conversation_history: Dict[str, List[ConversationMessage]] = field(default_factory=dict)





# Deprecated:

# @dataclass
# class TaskOutput:
#     """任务结果，存储任务执行过程中的输入输出和 artifact。"""
#     task_id: str
#     input_text: str
#     output: Optional[str] = None
#     # variables: Dict[str, Any] = field(default_factory=dict)

# @dataclass
# class TaskArtifactOrdinary:
#     """普通任务的任务产物，供下游任务使用。"""
#     CASE: str

# @dataclass
# class TaskArtifactSelfRefineFirst:
#     """self-refine 中第一步（初始答案）的任务产物，供下游任务使用。"""
#     CASE: str
#     INITIAL_ANSWER: str
# @dataclass
# class TaskArtifactSelfRefineSecond:
#     """self-refine 中第二步（批判）的任务产物，供下游任务使用。"""
#     CASE: str
#     INITIAL_ANSWER: str
#     CRITIQUE: str
# @dataclass
# class TaskArtifactSelfRefineThird:
#     """self-refine 中第三步（修正）的任务产物，供下游任务使用。"""
#     # todo ，未必需要
    
# @dataclass
# class TaskArtifact(Enum):
#     """任务产物，供下游任务使用。"""
#     ORDINARY: TaskArtifactOrdinary
#     SELF_REFINE_FIRST: TaskArtifactSelfRefineFirst
#     SELF_REFINE_SECOND: TaskArtifactSelfRefineSecond
   
