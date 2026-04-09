"""Accuracy 评估器实现。"""
from __future__ import annotations

from medical_llm_workflow.Domain.benchmark.Evaluator.base_evaluator import BaseEvaluator
from medical_llm_workflow.Domain.benchmark.Evaluator.models import SimpleEvaluatorProtocol


class AccuracyEvaluator(BaseEvaluator):
    """准确率评估器。

    支持参数：
    - case_sensitive: bool，默认 False
    - strip_whitespace: bool，默认 True
    """

    evaluator_name = "accuracy_evaluator"
    metric_name = "accuracy"
    # 指定 llm 用于评测的输出格式，方便后续自动评测脚本解析结果。这个格式需要能够被组合，所以 key 要比较 unique，避免和其他评测器的输出格式冲突。
    protocol: SimpleEvaluatorProtocol = {
        "answer": "<The exact option letter/index of the final answer, e.g. 'A' or '1'>",
    }

    # compare需要按照 dataset 是什么来对比吧
    def default_compare(
        self,
        llm_output_dict: SimpleEvaluatorProtocol,
        dataset_ground_truth_dict: SimpleEvaluatorProtocol,
        # params: Dict[str, Any]
    ) -> float:
        # case_sensitive = bool(params.get("case_sensitive", False))
        # strip_whitespace = bool(params.get("strip_whitespace", True))

        pred_text = llm_output_dict["answer"]
        gold_text = dataset_ground_truth_dict["answer"]

        score = 1.0 if pred_text == gold_text else 0.0
        
        return score

    # def _build_summary(self, records: List[ScoreRecord]) -> Dict[str, Any]:
    #     summary = super()._build_summary(records)
    #     miss_count = len(records) - int(summary["hit_count"])
    #     summary["miss_count"] = miss_count
    #     summary["accuracy"] = summary["hit_rate"]
    #     return summary

