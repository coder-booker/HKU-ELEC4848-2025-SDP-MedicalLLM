

from typing import List, Dict
from medical_llm_workflow.Domain.benchmark.Evaluator.evaluator_factory import EvaluatorFactory
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType
from medical_llm_workflow.Domain.benchmark.Dataset.models import DatasetType


class DatasetComplexEvaluatorConnector:
    def __init__(self, dataset_evaluator):
        self.dataset_evaluator = dataset_evaluator

    def dataset_to_evaluator_protocol(
        self,
        dataset_type: DatasetType,
        evalutor_type_list: List[EvaluatorType],
    ) -> Dict[str, str]:
        """根据 dataset 类型和 evaluator 列表，将"""
        protocol: Dict[str, str] = {}

        # 不同 dataset 可能需要不同的 evaluator 输出字段，具体逻辑可以根据实际需求调整。
        # for evaluator_type in evalutor_type_list:
        #     protocol.update(
        #         EvaluatorFactory.get_evaluator_llm_protocol(
        #             evaluator_type,
        #         ),
        #     )

        return protocol
        