from typing import List
from medical_llm_workflow.Domain.benchmark.models import BenchmarkConfig
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorConfig



def _build_evaluate_config(evaluator_list: List[List[EvaluatorConfig]]) -> EvaluationTaskConfig:
    """根据 evaluator 配置构建评测任务列表"""
    # steps:
    # 1. 得到每个 evaluator 的要求结构，组合成 prompt
    evaluator_type_list = self.config.benchamrk_config.evaluator_list
    
    
    # 2. 根据 prompt 构建对应的 TaskConfig