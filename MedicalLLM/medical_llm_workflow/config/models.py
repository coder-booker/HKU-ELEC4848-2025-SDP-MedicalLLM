"""数据模型定义模块，使用 dataclasses 和 Enum 定义所有配置和上下文结构。"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskType(Enum):
    """任务类型枚举。"""
    SINGLE_AGENT = "single_agent"
    SELF_REFINE = "self_refine"
    # 后续可扩展：SELF_CONSISTENCY, MULTI_AGENT 等

class PoeChatbotModel(Enum):
    """Poe 聊天机器人模型枚举。"""
    GPT_4_1 = "GPT-4.1"
    GPT_5_1 = "GPT-5.1"
    # 可根据需要添加更多模型


@dataclass
class PoeAPIConfig:
    """Poe API 配置。"""
    api_key: str
    base_url: str = "https://api.poe.com"


@dataclass
class PoeChatbotConfig:
    """Poe 聊天机器人配置。"""
    model: PoeChatbotModel
    temperature: float = 0.7
    max_tokens: int = 2048

@dataclass
class LanguageType(Enum):
    """支持的语言枚举。"""
    EN = "en"
    ZH = "zh"
    

@dataclass
class PromptType(Enum):
    """提示词类型，供选择不同的提示词模板。"""
    STRUCTURED = "structured"
    COT = "chain_of_thought"
    SELF_REFINE = "self_refine"

@dataclass
class PromptTemplate:
    """提示词模板。"""
    system: str
    user: str
    instructions: Optional[str] = None




@dataclass
class TaskConfig:
    """任务配置。"""
    task_id: str
    task_type: TaskType
    prompt_template: Optional[PromptTemplate] = None # will be dynamically generated
    prompt_type_list: Optional[List[PromptTemplate]] = None
    chatbot_config: PoeChatbotConfig # 让 Task 的每次访问都原子化
    language: LanguageType = LanguageType.EN # 任务的语言，继承但可以覆盖工作流的语言设置
    max_retries: int = 3 # 重试次数
    timeout: int = 60 # 超时时间，单位秒

# @dataclass
# class TaskContext:
#     """任务上下文，存储任务执行过程中的输入输出。"""
#     input_text: str
#     output: Optional[str] = None
#     # variables: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskOutput:
    """任务结果，存储任务执行过程中的输入输出和 artifact。"""
    task_id: str
    input_text: str
    output: Optional[str] = None
    artifact: Optional[str] = None # 供下游任务使用
    # variables: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskArtifactOrdinary:
    """普通任务的任务产物，供下游任务使用。"""
    CASE: str

@dataclass
class TaskArtifactSelfRefineFirst:
    """self-refine 中第一步（初始答案）的任务产物，供下游任务使用。"""
    CASE: str
    INITIAL_ANSWER: str
@dataclass
class TaskArtifactSelfRefineSecond:
    """self-refine 中第二步（批判）的任务产物，供下游任务使用。"""
    CASE: str
    INITIAL_ANSWER: str
    CRITIQUE: str
@dataclass
class TaskArtifactSelfRefineThird:
    """self-refine 中第三步（修正）的任务产物，供下游任务使用。"""
    # todo ，未必需要
    
@dataclass
class TaskArtifact(Enum):
    """任务产物，供下游任务使用。"""
    ORDINARY: TaskArtifactOrdinary
    SELF_REFINE_FIRST: TaskArtifactSelfRefineFirst
    SELF_REFINE_SECOND: TaskArtifactSelfRefineSecond
    
    



@dataclass
class ConversationMessage:
    """对话消息。"""
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class WorkflowConfig:
    """工作流配置。"""
    workflow_id: str
    name: str
    task_config_list: List[TaskConfig]
    language: LanguageType = LanguageType.EN # 整条工作流的语言

@dataclass
class WorkflowContext:
    """工作流上下文，存储整个工作流的执行状态。"""
    workflow_id: str
    session_id: str
    conversation_history: List[ConversationMessage] = field(default_factory=list)
    task_results: Dict[str, TaskContext] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

