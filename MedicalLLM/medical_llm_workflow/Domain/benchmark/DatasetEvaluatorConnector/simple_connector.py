

from typing import Dict
from medical_llm_workflow.Domain.benchmark.Dataset import DatasetType, MedQADatasetQuestion




class DatasetSimpleEvaluatorConnector:
    def __init__(self, dataset_evaluator):
        self.dataset_evaluator = dataset_evaluator

    @classmethod
    def dataset_to_evaluator_protocol(
        self,
        dataset_type: DatasetType,
        dataset_json_question: Dict[str, str],
    ) -> Dict[str, str]:
        """根据 dataset 类型和 evaluator 列表，将"""
        protocol: Dict[str, str] = {}
        
        if dataset_type == DatasetType.MED_QA:   # 获得 exact answer 就行
            medqa_question: MedQADatasetQuestion = dataset_json_question
            protocol['answer'] = medqa_question.answer  # simple evaluator 必定只会读 answer

        return protocol
    