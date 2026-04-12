"""Precision 评估器实现。

Precision (精确率): 对于单选题，计算每个选项维度的 TP（True Positive）和 FP（False Positive），
进而分别计算出各个选项的 Precision，最后求取 Macro-Precision。
"""
from __future__ import annotations

from typing import Any, Dict, List

from medical_llm_workflow.Domain.benchmark.Evaluator.base_evaluator import BaseEvaluator
from medical_llm_workflow.Domain.benchmark.Evaluator.models import (
    EvaluatorType,
    EvluationRecord,
    SimpleEvaluatorProtocol,
)
from medical_llm_workflow.Domain.benchmark.EvaluatorAdaptor.evaluator_adaptor import EvaluatorAdaptor


class PrecisionEvaluator(BaseEvaluator):
    """
    Precision 评估器。
    
    主要用于评估单选题（如MEDQA），通过计算各个选项维度的 Precision，并求取 Macro-Precision。
    """
    
    evaluator_name = "precision_evaluator"
    metric_name = EvaluatorType.PRECISION.value
    
    # 指定 llm 用于评测的输出格式协议，提供唯一 key 避免组合时覆盖。
    protocol: Dict[str, str] = {
        "precision_answer": "<The exact option letter/index/word of the final answer, e.g. 'A' or '1' or 'True'>",
    }
    
    def default_compare(
        self,
        llm_output_dict: Dict[str, Any],
        dataset_ground_truth_dict: Dict[str, Any],
    ) -> float:
        """
        单条样本级比对函数。
        """
        # 读取模型预测答案和正确答案
        pred_text = llm_output_dict.get("precision_answer", "")
        gold_text = dataset_ground_truth_dict.get("precision_answer", "")
        
        # 相等则说明当前选项预测正确
        score = 1.0 if pred_text == gold_text else 0.0
        
        return score
        
    def _build_summary(
        self,
        records: List[EvluationRecord],
    ) -> Dict[str, Any]:
        """
        构建评估摘要信息。
        
        统计这批数据里各个类别的 TP 和 FP，产出单一选项维度的 Precision 分析结果，并计算 Macro-Precision。
        """
        # 复用 Base 的基本摘要，如 hit_count 等
        summary = super()._build_summary(
            records,
        )
        
        # 内部统计字典，分别存储所有预测选项中的 TP (真阳) 和 FP (假阳) 频次
        tp_counts: Dict[str, int] = {}
        fp_counts: Dict[str, int] = {}
        
        # 提取真实的 ground_truth 集合，推断预设选项
        ground_truths = set()
        for record in records:
            gt_text = record["ground_truth"].get("precision_answer", "")
            if gt_text:
                ground_truths.add(gt_text)
                
        # 注入预设缺失选项（如MEDQA必定出现 A, B, C, D, E）
        expected_options = EvaluatorAdaptor.infer_precision_options_by_ground_truths(
            ground_truths,
        )
        for opt in expected_options:
            tp_counts[opt] = 0
            fp_counts[opt] = 0
        
        # 遍历全量评测样本记录，统计混淆矩阵中的关键元素
        for record in records:
            pred_text = record["prediction"].get("precision_answer", "")
            gold_text = record["ground_truth"].get("precision_answer", "")
            
            # 初始化不存在的预测类别字典入口
            if pred_text not in tp_counts:
                tp_counts[pred_text] = 0
                fp_counts[pred_text] = 0
                
            # 初始化不存在的标准答案类别字典入口
            if gold_text not in tp_counts:
                tp_counts[gold_text] = 0
                fp_counts[gold_text] = 0
                
            # 当预测值等于真实值，针对该预测类别的真阳数加 1
            if pred_text == gold_text:
                tp_counts[pred_text] += 1
            # 当预测不对，意味着对于所预测的那一个类别产生了一个 FP（假阳）误判
            else:
                fp_counts[pred_text] += 1
                
        precision_per_class: Dict[str, float] = {}
        
        # 分别对每个出现过的选项计算独立精确率
        for cls in tp_counts.keys():
            tp = tp_counts[cls]
            fp = fp_counts[cls]
            
            # 只有模型实际预测了（分母不为 0）该选项才有计算的价值
            if (tp + fp) > 0:
                precision_per_class[cls] = tp / (tp + fp)
            else:
                precision_per_class[cls] = 0.0
                
        macro_precision = 0.0
        
        # 对全部类别的结果求均值聚合成 Macro-Precision 作为综合核心指标
        if precision_per_class:
            macro_precision = sum(precision_per_class.values()) / len(precision_per_class)
            
        # 将自定义的 precision 指标加到最终 summary 字典里，供外层消费并在 Markdown 报告中展现
        summary["macro_precision"] = macro_precision
        summary["precision_per_class"] = precision_per_class
        
        return summary

