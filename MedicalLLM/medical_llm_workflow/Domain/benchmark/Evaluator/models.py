"""评估器公共数据模型。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class EvaluatorType(str, Enum):
    """内置评估器类型。"""

    ACCURACY = "accuracy"

class EvaluationSample(TypedDict):
    """
    - llm_output_dict: Dict[str, Any] - 模型预测结果，键值由评估
    - dataset_ground_truth_dict: Dict[str, Any] - 评估目标答案，键值由评估器协议定义
    """
    # - sample_id: str - 样本唯一标识
    # - metadata: Optional[Dict[str, Any]] - 其他元信息

    # sample_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    llm_output_dict: Dict[str, Any]
    dataset_ground_truth_dict: Dict[str, Any]
    # metadata: Dict[str, Any] = Field(default_factory=dict)

from enum import Enum

class EvaluatorDisplayType(str, Enum):
    PERCENTAGE = "percentage"
    BAR_CHART = "bar_chart"
    MIXED = "mixed"

EVALUATOR_DISPLAY_MAP = {
    "accuracy_evaluator": EvaluatorDisplayType.PERCENTAGE.value,
    "base_evaluator": EvaluatorDisplayType.BAR_CHART.value,
}

class EvluationRecord(TypedDict):
    """
    - sample_id: str - 样本唯一标识
    - score: float - 评估得分，范围 [0, 1]
    - prediction: Any - 模型预测结果原文
    - ground_truth: Any - 评估目标答案原文
    - detail: Optional[Dict[str, Any]] - 其他评估细节信息
    """

    # sample_id: str
    score: float
    prediction: Any
    ground_truth: Any
    detail: Optional[Dict[str, Any]] = Field(default_factory=dict)


class EvluationBatchResult(TypedDict):
    """
    - evaluator_name: str - 评估器名称
    - metric_name: str - 评测指标名称
    - total_samples: int - 评测样本总数
    - average_score: float - 平均得分
    - min_score: float - 最低得分
    - max_score: float - 最高得分
    - records: List[EvluationRecord] - 每条样本的评测记录列表
    - summary: Dict[str, Any] - 评测结果摘要信息，包含但不限于命中率、错误分析等
    """
    # - params: Dict[str, Any] - 评测参数配置

    evaluator_name: str
    display_type: str
    metric_name: str
    # params: Dict[str, Any] = Field(default_factory=dict)
    total_samples: int = 0
    average_score: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0
    records: List[EvluationRecord]
    summary: Dict[str, Any]


class EvaluationArtifacts(TypedDict):
    """
    - report_path: str - 评测报告文件路径
    - chart_path: Optional[str] - 评测图表文件路径（如果有）
    """

    report_path: str
    chart_path: Optional[str]


class EvaluationRunOutput(BaseModel):
    """
    - result: EvluationBatchResult - 评测结果对象
    - artifacts: EvaluationArtifacts - 评测产物对象，包含报告和图表文件路径
    """

    result: EvluationBatchResult
    artifacts: EvaluationArtifacts




class SimpleEvaluatorProtocol(TypedDict):
    """
    - answer: str - 问题答案
    """
    answer: str