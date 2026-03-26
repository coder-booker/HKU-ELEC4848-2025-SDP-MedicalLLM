"""评估器公共数据模型。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class EvaluatorType(Enum):
    """内置评估器类型。"""

    ACCURACY = "accuracy"

class EvaluationSample(BaseModel):
    """单条评估样本。"""

    sample_id: str
    prediction: Any
    target: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ScoreRecord(BaseModel):
    """单条样本评分结果。"""

    sample_id: str
    score: float
    prediction: Any
    target: Any
    detail: Optional[Dict[str, Any]] = Field(default_factory=dict)


class BatchEvaluationResult(BaseModel):
    """批量评估结果。"""

    evaluator_name: str
    metric_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    total_samples: int = 0
    average_score: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0
    records: List[ScoreRecord] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)


class EvaluationArtifacts(BaseModel):
    """产物路径信息。"""

    report_path: Optional[str] = None
    chart_path: Optional[str] = None


class EvaluationRunOutput(BaseModel):
    """一次 run 的完整输出。"""

    result: BatchEvaluationResult
    artifacts: EvaluationArtifacts = Field(default_factory=EvaluationArtifacts)
