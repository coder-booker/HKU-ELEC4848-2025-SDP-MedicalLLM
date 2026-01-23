from . import Task, PlainTextTask, ProblemRepresentationTask, HypothesisGenerationTask, HypothesisEvaluationTask
from medical_llm_workflow.schemas import (
    TaskConfig, TaskType, TaskStepType,
    PoeChatbotConfig, PoeChatbotModel, PromptTemplate
)


class TaskFactory:
    
    @staticmethod
    def create_task(task_config: TaskConfig) -> Task:
        if task_config.step_type == TaskStepType.PROBLEM_REPRESENTATION:
            return ProblemRepresentationTask(config=task_config)
        elif task_config.step_type == TaskStepType.HYPOTHESIS_GENERATION:
            return HypothesisGenerationTask(config=task_config)
        elif task_config.step_type == TaskStepType.HYPOTHESIS_EVALUATION:
            return HypothesisEvaluationTask(config=task_config)
        
        if task_config.type == TaskType.SINGLE_AGENT:
            return Task(config=task_config)
        
        elif task_config.type == TaskType.PLAIN_TEXT:
            return PlainTextTask(config=task_config)
        
        # TODO: self-refine, multi-agent 等等，还得思考怎么和 step_type 结合来制作 task
        
        else:
            raise ValueError(f"Unsupported task type: {task_config.type}")
    
    @staticmethod
    def create_empty_task_config() -> TaskConfig:
        """创建一个空的占位符任务配置。"""
        return TaskConfig(
            type=TaskType.PLAIN_TEXT,
            chatbot_config=PoeChatbotConfig(model=PoeChatbotModel.EMPTY_MODEL),
        )
    
    @staticmethod
    def create_plain_task_config(text: str) -> TaskConfig:
        """创建一个用于纯文本任务的占位符任务配置。"""
        return TaskConfig(
            type=TaskType.PLAIN_TEXT,
            chatbot_config=PoeChatbotConfig(model=PoeChatbotModel.EMPTY_MODEL),
            prompt_template=PromptTemplate(text=text),
        )