"""评估器工厂。"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .base_evaluator import BaseEvaluator
from .simpleEvaluator.accuracy import AccuracyEvaluator
from .simpleEvaluator.precision import PrecisionEvaluator
from .llmEvaluator.consistency import ConsistencyEvaluator
from .llmEvaluator.clarity import ClarityEvaluator
from .models import EvaluatorType


class EvaluatorFactory:
    """评估器工厂。"""

    _registry: Dict[EvaluatorType, type[BaseEvaluator]] = {
        EvaluatorType.ACCURACY: AccuracyEvaluator,
        EvaluatorType.PRECISION: PrecisionEvaluator,
        EvaluatorType.CONSISTENCY: ConsistencyEvaluator,
        EvaluatorType.CLARITY: ClarityEvaluator,
    }

    @classmethod
    def register(cls, evaluator_type: EvaluatorType, evaluator_cls: type[BaseEvaluator]) -> None:
        """注册自定义评估器。"""
        cls._registry[evaluator_type] = evaluator_cls

    @classmethod
    def create(
        cls,
        evaluator_type: EvaluatorType,
        # params: Optional[Dict[str, Any]] = None,
        compare_fn: Optional[Callable[[Any, Any, Dict[str, Any]], float]] = None,
        chatbot_config: Optional[Dict[str, Any]] = None,
    ) -> BaseEvaluator:
        """创建评估器实例。

        compare_fn 不为空时，将覆盖该评估器默认 compare 逻辑。
        """
        evaluator_cls = cls._registry.get(evaluator_type)
        if evaluator_cls is None:
            return None # 卫语句兜底，返回 None（实际调用处需处理缺失情况）
        return evaluator_cls(compare_fn=compare_fn, chatbot_config=chatbot_config)

    @classmethod
    def get_evaluator_llm_protocol(cls, evaluator_type: EvaluatorType) -> Dict[str, str]:
        """获取指定评估器的结构化输出提示词。"""
        evaluator_cls = cls._registry.get(evaluator_type)
        if evaluator_cls is None:
            raise ValueError(f"Unsupported evaluator type: {evaluator_type}")
        return evaluator_cls.protocol