"""任务领域模型。"""

from enum import Enum
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from medical_llm_workflow.schemas.models import ConversationMessage
from medical_llm_workflow.Infrastructure.LLM_client.models import ChatbotConfig
from medical_llm_workflow.Domain.prompts.models import PromptTemplate
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType


# BaseTask
class TaskType(Enum):
    """任务执行模式。"""

    PLAIN_TEXT = "plain_text"  # 纯文本任务，仅用于传递文本
    SINGLE_AGENT = "single_agent"
    SELF_REFINE = "self_refine"
    EVALUATION = "evaluation"  # 结果评测
    # 后续可扩展：SELF_CONSISTENCY, MULTI_AGENT 等


class MedicalType(Enum):  # 特殊状态，用来区分临床推理各步骤
    # SYSTEM = "system" # TODO：先不考虑 system 角色，这本质上就是 prompt 的一部分而已
    QUESTION = "question"

    PROBLEM_REPRESENTATION = "problem_representation"  # 问题表述
    HYPOTHESIS_GENERATION = "hypothesis_generation"  # 假设生成
    HYPOTHESIS_EVALUATION = "hypothesis_evaluation"  # 假设评估，包含了最终答案

    DEFAULT = "default"  # 默认值，暂时理解为占位符
    # ASSISTANT = "assistant" # AI 输出 TODO 不知道需不需要，先保留


class TaskContext(BaseModel):
    """任务输入输出容器。"""

    input: List[ConversationMessage]
    output: List[ConversationMessage]


class TaskConfig(BaseModel):
    """任务配置。"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)  # TODO：临时允许 str ，方便 demo 时手动指定 id
    type: TaskType
    medical_type: MedicalType = MedicalType.DEFAULT
    # context: TaskContext # TODO: 用户可以设定上下文

    chatbot_config: ChatbotConfig
    # language: LanguageType = LanguageType.EN # 继承但可以覆盖工作流的语言设置
    max_retries: int = 3
    timeout: int = 60

    # 用于动态生成 prompt 的参数映射。
    prompt_args_map: Dict[str, Any] = Field(default_factory=dict)

    # 对于 PlainTextTask 或需要显式文本模板的任务，可直接使用该字段。
    prompt_template: PromptTemplate | None = None

    # TODO：下游任务 id 列表，决定了该任务的输出会传递给哪些下游任务
    connect_to: List[str] = Field(default_factory=list)


class PlainTextTaskConfig(TaskConfig):
    """纯文本任务配置。"""

    type: TaskType = Field(default=TaskType.PLAIN_TEXT)
    prompt_template: PromptTemplate
    chatbot_config: Optional[ChatbotConfig]

class EvaluationTaskConfig(TaskConfig):
    type: TaskType = Field(default=TaskType.EVALUATION)
    
    # 给 factory 用的
    evaluator_list: List[EvaluatorType]


class TaskRecord(BaseModel):
    """记录在工作流上下文中的任务执行结果。"""

    task_config: TaskConfig
    task_context: TaskContext
