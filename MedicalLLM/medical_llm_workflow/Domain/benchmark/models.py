"""Benchmark 领域模型。"""
from enum import Enum
from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field

from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType
from medical_llm_workflow.Domain.benchmark.Dataset.models import DatasetConfig
import uuid


class BenchmarkConfig(BaseModel):
    """单个 benchmark 数据源的抽样配置。"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = "Default Benchmark Name"
    # 数据集配置列表，支持多个数据集
    dataset_list: List[DatasetConfig] = Field(default_factory=list)
    # 评估器配置列表，支持一个 dataset 对应多个评估维度
    evaluator_group_list: List[List[EvaluatorType]] = Field(default_factory=list)

