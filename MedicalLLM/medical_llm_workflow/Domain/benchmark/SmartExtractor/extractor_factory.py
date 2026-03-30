"""SmartExtractor 工厂与解析工具。"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from medical_llm_workflow.Domain.benchmark.Evaluator.evaluator_factory import EvaluatorFactory
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType
from medical_llm_workflow.Domain.benchmark.SmartExtractor.models import (
    SmartExtractionResult,
    SmartExtractorStrategy,
)


class SmartExtractorFactory:
    """SmartExtractor 工厂，负责 schema 拼装与抽取结果解析。"""

    @classmethod
    def build_expected_schema(cls, evaluator_list: List[EvaluatorType]) -> Dict[str, str]:
        """根据 evaluator 列表动态拼装结构化输出 schema。"""
        schema: Dict[str, str] = {}

        # 每个 evaluator 都能定义自己的结构化字段，最终合并为一个统一 schema。
        for evaluator_type in evaluator_list:
            protocol = EvaluatorFactory.get_evaluator_llm_protocol(evaluator_type)
            for protocol_key in protocol:
                if protocol_key not in schema:
                    schema.update(protocol)

        return schema

    @classmethod
    def parse_result(
        cls,
        raw_response: str,
        expected_schema: Dict[str, str],    # TODO：可以和simple/complex connector的 protocol 共用
    ) -> SmartExtractionResult:
        """解析 SmartExtractor 的 LLM 输出，仅接受结构化 JSON。"""
        extracted: Dict[str, Any] = {}

        # 优先按照 JSON 结构化结果解析。
        try:
            parsed = json.loads(raw_response)
            if isinstance(parsed, dict):
                extracted = parsed
                extracted.update(
                    {
                        "success": True,
                    },
                )
        except Exception:
            extracted = {
                "success": False,
            }

        # 补齐 schema 中缺失字段，保证下游 evaluator 消费时字段稳定。
        for schema_key in expected_schema:
            if schema_key not in extracted:
                extracted[schema_key] = ""

        return {
            "raw_response": raw_response,
            "extracted": extracted,
        }
