"""SmartExtractor 工厂与解析工具。"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from medical_llm_workflow.Domain.benchmark.Evaluator.evaluator_factory import EvaluatorFactory
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType
from medical_llm_workflow.Domain.benchmark.Dataset import DatasetType
from medical_llm_workflow.Domain.benchmark.Dataset import BaseNormalizedQuestion


# 将 dataset 的 protocol 映射到 evaluator 需要的字段，形成一个适配器，方便 evaluator 进行评测。
# 考虑了 dataset 种类的 evaluator 种类的二维 mapping
# dataset 必须用一个额外的 map 来适配 evaluator
DATASET_EVALUATOR_SCHEMA_MAP = {
    DatasetType.MED_QA: {
        # accuracy evaluator 用以测评的字段是 'accuracy_answer'。对于 MED_QA 数据集，这个 'accuracy_answer' 就是 'ground_truth' 字段
        EvaluatorType.ACCURACY: ["ground_truth", "accuracy_answer"],
        EvaluatorType.PRECISION: ["ground_truth", "precision_answer"],
    },
    DatasetType.PUBMED: {
        EvaluatorType.ACCURACY: ["ground_truth", "accuracy_answer"],
        EvaluatorType.PRECISION: ["ground_truth", "precision_answer"],
    },
}


class EvaluatorAdaptor:
    """
    与其他工厂不同，不会返回一个实例，仅负责 schema 拼装与抽取结果解析的方法提供。
    """
    @classmethod
    def build_expected_schema(cls, evaluator_type_list: List[EvaluatorType]) -> Dict[str, str]:
        """根据 evaluator 列表动态拼装结构化输出 schema。"""
        final_schema: Dict[str, str] = {}

        # 每个 evaluator 都能定义自己的结构化字段，最终合并为一个统一 schema。
        for evaluator_type in evaluator_type_list:
            schema = EvaluatorFactory.get_evaluator_llm_protocol(evaluator_type)
            # print(f"Schema for evaluator {evaluator_type.value}:\n{schema}")
            for schema_key in schema:
                if schema_key not in final_schema:
                    final_schema.update(schema)
        # print(f"Current final schema after processing:\n{final_schema}")

        return final_schema
    
    @classmethod
    def parse_dataset_question_to_evaluator_schema(
        cls,
        dataset_type: DatasetType,
        dataset_json_question: BaseNormalizedQuestion,
        evaluator_type_list: List[EvaluatorType],
    ) -> Dict[str, str]:
        """根据 dataset 类型和 evaluator 列表，获取 dataset 中的金标答案，并适配为 evaluator 需要的格式以方便 evaluator 对比 llm 的预测进行评估。"""
        result_dict: Dict[str, str] = {} # 应该和 evaluation_schema 的 key 一一对应
        for evaluator_type in evaluator_type_list:
            dataset_key, evaluator_key = DATASET_EVALUATOR_SCHEMA_MAP[dataset_type][evaluator_type]
            result_dict[evaluator_key] = dataset_json_question[dataset_key]  # simple evaluator 必定只会读 answer。MedQA 的金标答案在 ground_truth 字段里。
        
        return result_dict
    
    @classmethod
    def parse_extracted_data_to_evaluator_schema(
        cls,
        text_json_response: str,
        expected_schema: Dict[str, str],    # TODO：可以和simple/complex connector的 protocol 共用
    ) -> Dict[str, str]:
        """
        将 llm 的输出文本按照 expected_schema 定义的字段进行提取和补齐。
        llm 的最终输出文本在 smart extractor 任务下会是一个和 expected_schema 一样的 Json 字符串
        """
        response_dict: Dict[str, Any] = {}

        # 优先按照 JSON 结构化结果解析。
        try:
            parsed = json.loads(text_json_response)
            if isinstance(parsed, dict):
                response_dict = parsed
                response_dict.update(
                    {
                        "success": True,
                    },
                )
        except Exception:
            response_dict = {
                "success": False,
            }

        # 补齐 schema 中缺失字段，保证下游 evaluator 消费时字段稳定。
        for schema_key in expected_schema:
            if schema_key not in response_dict:
                response_dict[schema_key] = ""

        return response_dict
