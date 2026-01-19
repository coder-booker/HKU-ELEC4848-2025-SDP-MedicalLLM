# 其他模块可以从这个模块中获取想要的 benchmark
from typing import List

from medical_llm_workflow.schemas import BenchmarkType, MedQABenchmarkProtocal
from .MedQA.medqa_benchmark import MedQABenchmark


class BenchmarkManager:
    
    @staticmethod
    def get_json_questions(benchmark_id: BenchmarkType, num: int):
        if benchmark_id == BenchmarkType.MED_QA:
            questions: List[MedQABenchmarkProtocal] = MedQABenchmark.get_questions(num=num)
            return questions
        
        # TODO: 可以添加更多的 benchmark 类型
        
        raise ValueError(f"Unknown benchmark ID: {benchmark_id}")
    
    @staticmethod
    def get_text_questions(benchmark_id: BenchmarkType, num: int):
        if benchmark_id == BenchmarkType.MED_QA:
            questions: List[str] = MedQABenchmark.get_text_questions(num=num)
            return questions
        
        # TODO: 可以添加更多的 benchmark 类型
        
        raise ValueError(f"Unknown benchmark ID: {benchmark_id}")