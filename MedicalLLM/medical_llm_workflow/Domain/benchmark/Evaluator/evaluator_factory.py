"""评估器工厂。"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .base_evaluator import BaseEvaluator
from .all_evaluators.accuracy import AccuracyEvaluator
from .models import EvaluatorType


class EvaluatorFactory:
    """评估器工厂。"""

    _registry: Dict[EvaluatorType, type[BaseEvaluator]] = {
        EvaluatorType.ACCURACY: AccuracyEvaluator,
    }

    @classmethod
    def register(cls, evaluator_type: EvaluatorType, evaluator_cls: type[BaseEvaluator]) -> None:
        """注册自定义评估器。"""
        cls._registry[evaluator_type] = evaluator_cls

    @classmethod
    def create(
        cls,
        evaluator_type: EvaluatorType,
        params: Optional[Dict[str, Any]] = None,
        compare_fn: Optional[Callable[[Any, Any, Dict[str, Any]], float]] = None,
    ) -> BaseEvaluator:
        """创建评估器实例。

        compare_fn 不为空时，将覆盖该评估器默认 compare 逻辑。
        """
        evaluator_cls = cls._registry.get(evaluator_type)
        if evaluator_cls is None:
            raise ValueError(f"Unsupported evaluator type: {evaluator_type}")
        return evaluator_cls(params=params, compare_fn=compare_fn)

