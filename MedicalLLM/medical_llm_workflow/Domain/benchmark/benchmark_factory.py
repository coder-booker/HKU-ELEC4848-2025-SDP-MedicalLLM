# """Benchmark 工厂。

# 该模块负责把声明式配置组装成可运行的 benchmark。
# """
# from __future__ import annotations

# from typing import Any, Dict, Optional

# from medical_llm_workflow.Domain.benchmark.models import BenchmarkConfig
# from medical_llm_workflow.Domain.benchmark.Dataset import BaseDataset, DatasetFactory, DatasetType
# from medical_llm_workflow.Domain.benchmark.Evaluator import BaseEvaluator, EvaluatorFactory, EvaluatorType

# # 暂时不用

# class Benchmark:
#     """Benchmark 运行对象。"""

#     def __init__(
#         self,
#         config: BenchmarkConfig,
#         dataset: BaseDataset[Any],
#         evaluator: BaseEvaluator,
#     ) -> None:
#         """保存 benchmark 的核心组件。"""
#         self.config = config
#         self.dataset = dataset
#         self.evaluator = evaluator

#     def get_json_questions(self) -> list[Any]:
#         """按配置获取结构化题目。"""
#         return self.dataset.get_json_questions(
#             random=self.config.select_random,
#             num=self.config.num_of_questions,
#         )

#     def get_text_questions(self) -> list[str]:
#         """按配置获取文本题目。"""
#         return self.dataset.get_text_questions(
#             random=self.config.select_random,
#             num=self.config.num_of_questions,
#         )


# # class BenchmarkFactory:
# #     """Benchmark 工厂。"""

# #     @classmethod
# #     def create(
# #         cls,
# #         config: BenchmarkConfig,
# #     ) -> Benchmark:
# #         """根据配置创建 Benchmark。"""
        
# #         if resolved_dataset_type is None:
# #             # 若配置未声明 dataset 类型，则按 benchmark 类型做固定映射。
# #             resolved_dataset_type = cls._BENCHMARK_TO_DATASET_TYPE_MAP.get(config.id)

# #         if resolved_dataset_type is None:
# #             raise ValueError(f"Unsupported benchmark id: {config.id}")

# #         resolved_evaluator_type = evaluator_type or config.evaluator_type

# #         # 支持“调用时参数覆盖配置参数”，便于不同场景复用同一份配置。
# #         resolved_dataset_params = dict(config.dataset_params)
# #         if dataset_params:
# #             resolved_dataset_params.update(dataset_params)

# #         resolved_evaluator_params = dict(config.evaluator_params)
# #         if evaluator_params:
# #             resolved_evaluator_params.update(evaluator_params)

# #         dataset = DatasetFactory.create(
# #             dataset_type=resolved_dataset_type,
# #             params=resolved_dataset_params,
# #         )
# #         evaluator = EvaluatorFactory.create(
# #             evaluator_type=resolved_evaluator_type,
# #             params=resolved_evaluator_params,
# #         )

# #         return Benchmark(
# #             config=config,
# #             dataset=dataset,
# #             evaluator=evaluator,
# #         )
