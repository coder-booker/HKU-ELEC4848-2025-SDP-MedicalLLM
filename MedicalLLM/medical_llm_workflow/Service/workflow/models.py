from typing import List, Dict
import uuid
from pydantic import BaseModel, Field
from medical_llm_workflow.Domain.tasks.models import TaskConfig
from medical_llm_workflow.Domain.benchmark.models import BenchmarkConfig

# Workflow
class WorkflowConfig(BaseModel):
    """工作流配置。"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = "Default Workflow Name"
    # 任务按列表顺序执行。
    task_config_list: List[TaskConfig] = Field(default_factory=list) # 按顺序执行的任务列表
    benchamrk_config: BenchmarkConfig # TODO: 目前只支持单一 benchmark
    
    task_connections: Dict[str, List[str]] = Field(default_factory=dict) # 任务连接关系图，key 是上游任务 id ，value 是下游任务 id 列表
    # language: LanguageType = LanguageType.EN # 整条工作流的语言