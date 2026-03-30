"""Recipe 抽象定义。

用于把“工作流模板”统一抽象为可生成 TaskConfig 列表的对象，
上层可通过 recipe 名称快速组装任务链。
"""
from abc import ABC, abstractmethod
from typing import List

from medical_llm_workflow.Infrastructure.LLM_client import BaseChatbotConfig
from medical_llm_workflow.Domain.tasks.models import TaskConfig
from medical_llm_workflow.Domain.recipes.models import RecipeMeta


class Recipe(ABC):
	"""Recipe 抽象基类。"""

	meta: RecipeMeta

	@abstractmethod
	def build_task_configs(self, chatbot_config: BaseChatbotConfig) -> List[TaskConfig]:
		"""基于 chatbot 配置生成任务链。"""
