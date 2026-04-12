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
    EvluationBatchResult,
    EvaluationArtifacts,
    EvaluationRunOutput,
    EvaluationSample,
    EvluationRecord,
    EVALUATOR_DISPLAY_MAP,
    EvaluatorDisplayType
)
from medical_llm_workflow.app_settings import AppSettings
import os

DEFAULT_REPORT_PATH = os.path.join(AppSettings.RESULT_DIR, AppSettings.EVALUATION_REPORT_FILENAME)
DEFAULT_CHART_PATH = os.path.join(AppSettings.RESULT_DIR, AppSettings.EVALUATION_CHART_FILENAME)

CompareFn = Callable[[Any, Any, Dict[str, Any]], float]


class BaseEvaluator(ABC):
    """评估器抽象。"""

    evaluator_name: str = "base_evaluator"
    metric_name: str = "base_metric"
    protocol: Dict[str, str] = {}

    def __init__(
        self,
        # params: Optional[Dict[str, Any]] = None,
        compare_fn: Optional[CompareFn] = None,
    ) -> None:
        # self.params: Dict[str, Any] = params or {}
        self.compare_fn: CompareFn = compare_fn or self.default_compare

    @abstractmethod
    def default_compare(self, prediction: Any, ground_truth: Any) -> float:
        """默认评分函数（当未注入 compare_fn 时使用）。"""

    def normalize_compare_element(self, raw_prediction: Any) -> Any:
        """把工作流原始输出归一化为评测输入。"""
        # 默认不做转换，交给具体 evaluator 按指标语义覆盖。
        return raw_prediction

    def _build_summary(self, records: List[EvluationRecord]) -> Dict[str, Any]:
        """
        构建默认摘要信息。
        
        基类仅负责提供与具体指标计算无关的元数据（如样本总数）。
        更细节的计算（如命中数、精确率等）全交由具体 Evaluator 负责补充。
        """
        return {
            "total_samples": len(records),
        }

    def build_chart_data(self, result: EvluationBatchResult) -> Dict[str, Any]:
        """为前端提供图表所需的数据结构。"""
        # 前端使用 Recharts 或者自定义图表时，直接提供这组 JSON 结构即可。
        return {
            "title": f"{result['metric_name']} summary",
            "xAxis": ["average", "min", "max"],
            "yAxisLabel": "score",
            "yAxisRange": [0, 1],
            "series": [
                {"name": "average", "value": round(result["average_score"], 4)},
                {"name": "min", "value": round(result["min_score"], 4)},
                {"name": "max", "value": round(result["max_score"], 4)},
            ]
        }

    def build_report_markdown(self, result: EvluationBatchResult) -> str:
        """生成 Markdown 报告内容。不再内嵌 mermaid 纯文本逻辑。"""
        lines: List[str] = []
        lines.append(f"## Evaluation Report - {result['evaluator_name']}")
        lines.append("")
        lines.append(f"- Metric: {result['metric_name']}")
        lines.append(f"- Total Samples: {result['total_samples']}")
        lines.append(f"- Average Score: {result['average_score']:.4f}")
        lines.append(f"- Min Score: {result['min_score']:.4f}")
        lines.append(f"- Max Score: {result['max_score']:.4f}")
        # lines.append(f"- Params: {result.params}")
        lines.append("")

        lines.append("")
        for key, value in result.get("summary", {}).items():
            lines.append(f"- {key}: {value}")
        lines.append("")

        return "\n".join(lines)
    
    
    def evaluate_one(self, sample: EvaluationSample) -> EvluationRecord:
        """评分单条样本。"""
        score = float(
            self.compare_fn(
                self.normalize_compare_element(sample["llm_output_dict"]),
                self.normalize_compare_element(sample["dataset_ground_truth_dict"]),
            )
        )
        # 统一钳制到 [0, 1]，避免注入函数异常返回污染统计。
        score = max(0.0, min(1.0, score))
        
        return {
            # "sample_id": sample[],
            "score": score,
            "prediction": sample["llm_output_dict"],
            "ground_truth": sample["dataset_ground_truth_dict"],
        }

    def evaluate_batch(self, sample_list: List[EvaluationSample]) -> EvluationBatchResult:
        """批量评分。"""
        # if not sample_list:
        #     return EvluationBatchResult(
        #         evaluator_name=self.evaluator_name,
        #         metric_name=self.metric_name,
        #         params=self.params,
        #         total_samples=0,
        #         average_score=0.0,
        #         min_score=0.0,
        #         max_score=0.0,
        #         records=[],
        #         summary={"note": "No sample_list provided."},
        #     )

        records = [self.evaluate_one(sample) for sample in sample_list]
        scores = [record["score"] for record in records]

        return {
            "evaluator_name": self.evaluator_name,
            "display_type": EVALUATOR_DISPLAY_MAP.get(self.evaluator_name, EvaluatorDisplayType.BAR_CHART.value),
            "metric_name": self.metric_name,
            # "params": self.params,
            "total_samples": len(records),
            "average_score": float(mean(scores)),
            "min_score": float(min(scores)),
            "max_score": float(max(scores)),
            "records": records,
            "summary": self._build_summary(records),
        }

    def run(
        self,
        sample_list: List[EvaluationSample],
        report_path: str = DEFAULT_REPORT_PATH,
        chart_path: str = DEFAULT_CHART_PATH,
    ) -> EvaluationRunOutput:
        """执行批量评估并按需写出产物。"""
        # 运行评分逻辑，得到结果对象。
        result = self.evaluate_batch(sample_list)

        report_text = self.build_report_markdown(result)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)
            
        chart_data = self.build_chart_data(result)
        # 不再通过 chart_text 写文本图表
        # with open(chart_path, "w", encoding="utf-8") as f: ...
        
        artifacts: EvaluationArtifacts = {
            "report_path": report_path,
            "chart_path": chart_path,
        }
        
        run_output: EvaluationRunOutput = {
            "result": result,
            "artifacts": artifacts,
        }

        return run_output
