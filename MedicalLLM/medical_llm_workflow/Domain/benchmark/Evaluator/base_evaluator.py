"""评估器抽象基类。

支持：
1) 参数化评分
2) 注入自定义对比函数
3) 批量评分
4) 导出图表（Mermaid）
5) 导出 Markdown 报告
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from statistics import mean
from typing import Any, Callable, Dict, List, Optional

from .models import (
    BatchEvaluationResult,
    EvaluationArtifacts,
    EvaluationRunOutput,
    EvaluationSample,
    ScoreRecord,
)

CompareFn = Callable[[Any, Any, Dict[str, Any]], float]


class BaseEvaluator(ABC):
    """评估器抽象。"""

    evaluator_name: str = "base_evaluator"
    metric_name: str = "base_metric"

    def __init__(
        self,
        params: Optional[Dict[str, Any]] = None,
        compare_fn: Optional[CompareFn] = None,
    ) -> None:
        self.params: Dict[str, Any] = params or {}
        self.compare_fn: CompareFn = compare_fn or self.default_compare

    @abstractmethod
    def default_compare(self, prediction: Any, target: Any, params: Dict[str, Any]) -> float:
        """默认评分函数（当未注入 compare_fn 时使用）。"""

    def score_one(self, sample: EvaluationSample) -> ScoreRecord:
        """评分单条样本。"""
        score = float(self.compare_fn(sample.prediction, sample.target, self.params))
        # 统一钳制到 [0, 1]，避免注入函数异常返回污染统计。
        score = max(0.0, min(1.0, score))
        return ScoreRecord(
            sample_id=sample.sample_id,
            score=score,
            prediction=sample.prediction,
            target=sample.target,
        )

    def score_batch(self, samples: List[EvaluationSample]) -> BatchEvaluationResult:
        """批量评分。"""
        if not samples:
            return BatchEvaluationResult(
                evaluator_name=self.evaluator_name,
                metric_name=self.metric_name,
                params=self.params,
                total_samples=0,
                average_score=0.0,
                min_score=0.0,
                max_score=0.0,
                records=[],
                summary={"note": "No samples provided."},
            )

        records = [self.score_one(sample) for sample in samples]
        scores = [record.score for record in records]

        return BatchEvaluationResult(
            evaluator_name=self.evaluator_name,
            metric_name=self.metric_name,
            params=self.params,
            total_samples=len(records),
            average_score=float(mean(scores)),
            min_score=float(min(scores)),
            max_score=float(max(scores)),
            records=records,
            summary=self._build_summary(records),
        )

    def _build_summary(self, records: List[ScoreRecord]) -> Dict[str, Any]:
        """构建默认摘要。"""
        hit_count = sum(1 for r in records if r.score >= 1.0)
        return {
            "hit_count": hit_count,
            "hit_rate": (hit_count / len(records)) if records else 0.0,
        }

    def build_chart_mermaid(self, result: BatchEvaluationResult) -> str:
        """生成 Mermaid 条形图（文本）。"""
        avg = round(result.average_score, 4)
        min_v = round(result.min_score, 4)
        max_v = round(result.max_score, 4)

        return (
            "xychart-beta\n"
            f'    title "{result.metric_name} summary"\n'
            '    x-axis ["average", "min", "max"]\n'
            '    y-axis "score" 0 --> 1\n'
            f"    bar [{avg}, {min_v}, {max_v}]\n"
        )

    def build_report_markdown(self, result: BatchEvaluationResult) -> str:
        """生成 Markdown 报告内容。"""
        lines: List[str] = []
        lines.append(f"# Evaluation Report - {result.evaluator_name}")
        lines.append("")
        lines.append(f"- Metric: {result.metric_name}")
        lines.append(f"- Total Samples: {result.total_samples}")
        lines.append(f"- Average Score: {result.average_score:.4f}")
        lines.append(f"- Min Score: {result.min_score:.4f}")
        lines.append(f"- Max Score: {result.max_score:.4f}")
        lines.append(f"- Params: {result.params}")
        lines.append("")

        lines.append("## Summary")
        lines.append("")
        for key, value in result.summary.items():
            lines.append(f"- {key}: {value}")
        lines.append("")

        lines.append("## Score Distribution")
        lines.append("")
        lines.append("```mermaid")
        lines.append(self.build_chart_mermaid(result).rstrip())
        lines.append("```")
        lines.append("")

        lines.append("## Per Sample")
        lines.append("")
        lines.append("| sample_id | score | prediction | target |")
        lines.append("|---|---:|---|---|")
        for record in result.records:
            lines.append(
                f"| {record.sample_id} | {record.score:.4f} | {record.prediction} | {record.target} |"
            )

        lines.append("")
        return "\n".join(lines)

    def run(
        self,
        samples: List[EvaluationSample],
        report_path: Optional[str] = None,
        chart_path: Optional[str] = None,
    ) -> EvaluationRunOutput:
        """执行批量评估并按需写出产物。"""
        result = self.score_batch(samples)
        artifacts = EvaluationArtifacts()

        if report_path:
            report_text = self.build_report_markdown(result)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            artifacts.report_path = report_path

        if chart_path:
            chart_text = self.build_chart_mermaid(result)
            with open(chart_path, "w", encoding="utf-8") as f:
                f.write(chart_text)
            artifacts.chart_path = chart_path

        return EvaluationRunOutput(result=result, artifacts=artifacts)
