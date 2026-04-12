"""Accuracy 评估器实现。"""
from __future__ import annotations

from typing import Any, Dict, List

from medical_llm_workflow.Domain.benchmark.Evaluator.base_evaluator import BaseEvaluator
from medical_llm_workflow.Domain.benchmark.Evaluator.models import (
    SimpleEvaluatorProtocol,
    EvaluatorType,
    EvluationRecord,
)


class AccuracyEvaluator(BaseEvaluator):
    """
    Accuracy 评估器。
    
    主要用于评估单选题（如MEDQA），通过计算预测与真值一致的频次，计算题目的最终准确率。
    """

    evaluator_name = "accuracy_evaluator"
    metric_name = EvaluatorType.ACCURACY.value
    
    # 指定 llm 用于评测的输出格式，方便后续自动评测脚本解析结果。
    protocol: Dict[str, str] = {
        "accuracy_answer": "<The exact option letter/index/word of the final answer, e.g. 'A' or '1' or 'True'>",
    }

    def default_compare(
        self,
        llm_output_dict: Dict[str, Any],
        dataset_ground_truth_dict: Dict[str, Any],
    ) -> float:
        """
        单条样本级比对函数。
        
        仅当模型输出与真值完全一致时判定为 1.0 的得分，否则为 0.0。
        """
        pred_text = llm_output_dict.get("accuracy_answer", "")
        gold_text = dataset_ground_truth_dict.get("accuracy_answer", "")

        score = 1.0 if pred_text == gold_text else 0.0
        
        return score

    def _build_summary(
        self,
        records: List[EvluationRecord],
    ) -> Dict[str, Any]:
        """
        构建评估摘要信息。
        
        计算本次评估中的全部命中题数、未命中题数，并计算宏观平均准确率（Accuracy）。
        """
        # 复用 Base 提取的基础元数据（如 total_samples）
        summary = super()._build_summary(
            records,
        )
        
        # 统计得分大于等于 1.0 的判定为答对的题目数
        hit_count = sum(
            1 for r in records if r["score"] >= 1.0
        )
        total_samples = summary.get("total_samples", len(records))
        
        # 边界与异常情况处理
        if total_samples > 0:
            accuracy = hit_count / total_samples
        else:
            accuracy = 0.0
            
        miss_count = total_samples - hit_count
        
        # 将计算获得的细粒度指标填入 summary，用于 Markdown 报告显示
        summary["hit_count"] = hit_count
        summary["miss_count"] = miss_count
        summary["accuracy"] = accuracy
        
        return summary

