"""任务领域模型。"""

from enum import Enum
import uuid
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import json

from medical_llm_workflow.schemas.models import ConversationMessage
from medical_llm_workflow.Infrastructure.LLM_client.models import BaseChatbotConfig
from medical_llm_workflow.Domain.prompts.models import PromptTemplate
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType



# BaseTask
class TaskType(str, Enum):
    """任务执行模式。"""

    PLAIN_TEXT = "plain_text"  # 纯文本任务，仅用于传递文本
    SINGLE_AGENT = "single_agent"
    SELF_REFINE = "self_refine"
    EVALUATION = "evaluation"  # 结果评测
    SMART_EXTRACTOR = "smart_extractor"  # evaluator 驱动的结构化抽取
    # 后续可扩展：SELF_CONSISTENCY, MULTI_AGENT 等


class MedicalType(str, Enum):  # 特殊状态，用来区分临床推理各步骤
    # SYSTEM = "system" # TODO：先不考虑 system 角色，这本质上就是 prompt 的一部分而已
    QUESTION = "question"

    PROBLEM_REPRESENTATION = "problem_representation"  # 问题表述
    HYPOTHESIS_GENERATION = "hypothesis_generation"  # 假设生成
    HYPOTHESIS_EVALUATION = "hypothesis_evaluation"  # 假设评估，包含了最终答案

    DEFAULT = "default"  # 默认值，暂时理解为占位符
    # BOT = "assistant" # AI 输出 TODO 不知道需不需要，先保留


class TaskContext(TypedDict):
    """
    - input: List[ConversationMessage] - 任务输入的对话消息列表
    - output: List[ConversationMessage] - 任务输出的对话消息列表
    """

    input: List[ConversationMessage]
    output: List[ConversationMessage]
    
    def to_dict(self) -> Dict[str, Any]:
        """把 TaskContext 转换为普通字典，方便打印输出。"""
        return {
            "input": [message.model_dump() for message in self["input"]],
            "output": [message.model_dump() for message in self["output"]],
        }


class TaskConfig(BaseModel):
    """
    - id: str - 任务唯一标识
    - type: TaskType - 任务类型
    - medical_type: MedicalType - 医学步骤类型
    - chatbot_config: BaseChatbotConfig - 任务专用的聊天机器人配置
    - max_retries: int - 任务最大重试次数
    - timeout: int - 任务超时时间（秒）
    - prompt_template: Optional[PromptTemplate] - 任务专用的 prompt 模板
    - prompt_args_map: Dict[str, Any] - 用于动态生成 prompt 的参数映射
    - connect_to: List[str] - 该任务的输出将传递给哪些下游任务
    - input_msg_sources: List[str] - 提供输入的上游 task_id 列表，prompt 中直接使用 {{task_id}} 作为 placeholder
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # 支持 UUID 和用户自定义字符串
    type: TaskType
    medical_type: MedicalType = MedicalType.DEFAULT
    # context: TaskContext # TODO: 用户可以设定上下文

    chatbot_config: BaseChatbotConfig
    # language: LanguageType = LanguageType.EN # 继承但可以覆盖工作流的语言设置
    max_retries: int = 3
    timeout: int = 60

    # 提供输入的上游 task_id 列表，prompt 中直接使用 {{task_id}} 作为 placeholder
    input_msg_sources: List[str] = Field(default_factory=list)

    # 对于 PlainTextTask 或需要显式文本模板的任务，可直接使用该字段。
    prompt_template: PromptTemplate | None = None

    # TODO：下游任务 id 列表，决定了该任务的输出会传递给哪些下游任务
    connect_to: List[str] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """把 TaskConfig 转换为普通字典，方便打印输出。"""
        return {
            "id": self.id,
            "type": self.type.value,
            "medical_type": self.medical_type.value,
            "chatbot_config": json.dumps(self.chatbot_config, ensure_ascii=False, indent=2) if self.chatbot_config else "",
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "input_msg_sources": self.input_msg_sources,
            "prompt_template": self.prompt_template.model_dump() if self.prompt_template else "",
            "connect_to": self.connect_to,
        }


class PlainTextTaskConfig(TaskConfig):
    """
    - id: str - 任务唯一标识
    - type: TaskType.PLAIN_TEXT - 任务类型
    - medical_type: MedicalType - 医学步骤类型
    - chatbot_config: Optional[BaseChatbotConfig] - 任务专用的聊天机器人配置
    - max_retries: int - 任务最大重试次数
    - timeout: int - 任务超时时间（秒）
    - prompt_template: PromptTemplate - 任务专用的 prompt 模板
    - connect_to: List[str] - 该任务的输出将传递给哪些下游任务
    """

    type: TaskType = TaskType.PLAIN_TEXT
    prompt_template: PromptTemplate
    chatbot_config: Optional[BaseChatbotConfig] = None

class EvaluationTaskConfig(TaskConfig):
    """
    - evaluator_type_list: List[EvaluatorType] - 评测使用的评测器列表
    - question_list: List[Dict[str, str]] - 评测题目列表
    - id: str - 任务唯一标识
    - type: TaskType.EVALUATION - 任务类型
    - medical_type: MedicalType - 医学步骤类型
    - chatbot_config: Optional[BaseChatbotConfig] - 任务专用的聊天机器人配置
    - max_retries: int - 任务最大重试次数
    - timeout: int - 任务超时时间（秒）
    - prompt_template: PromptTemplate - 任务专用的 prompt 模板
    - connect_to: List[str] - 该任务的输出将传递给哪些下游任务
    """
    
    type: TaskType = Field(default=TaskType.EVALUATION)
    
    # 给 factory 用的
    evaluator_type_list: List[EvaluatorType]
    
    # 题目
    question_list: List[Dict[str, str]]


class SmartExtractorTaskConfig(TaskConfig):
    """
    - evaluator_type_list: List[EvaluatorType] - 评测使用的评测器列表
    - id: str - 任务唯一标识
    - type: TaskType.SMART_EXTRACTOR - 任务类型
    - medical_type: MedicalType - 医学步骤类型
    - chatbot_config: BaseChatbotConfig - 任务专用的聊天机器人配置
    - max_retries: int - 任务最大重试次数
    - timeout: int - 任务超时时间（秒）
    - prompt_template: Optional[PromptTemplate] - 任务专用的 prompt 模板
    - connect_to: List[str] - 该任务的输出将传递给哪些下游任务
    """

    type: TaskType = Field(default=TaskType.SMART_EXTRACTOR)

    # 用 evaluator 列表动态决定抽取 schema，避免硬编码固定字段。
    evaluator_type_list: List[EvaluatorType]
    


class TaskRecord(TypedDict):
    """
    - task_config: TaskConfig - 任务配置
    - task_context: TaskContext - 任务执行过程中的输入输出上下文
    """

    task_config: TaskConfig
    task_context: TaskContext
