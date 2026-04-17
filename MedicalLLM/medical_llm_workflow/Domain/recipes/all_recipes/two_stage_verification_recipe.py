"""两阶段验证推理 Recipe 模块。

基于给定的验证提示集，将复杂的多轮验证和反思过程，
平铺转化为顺序执行的无环流水线任务。流水线涵盖从初始诊断、
到多维度（体征、实验室、影像学）校验比对，
最后综合判决最终选项的完整闭环。
"""

from typing import List

from medical_llm_workflow.Domain.tasks.models import TaskConfig, TaskType
from medical_llm_workflow.Domain.recipes.recipe import Recipe
from medical_llm_workflow.Domain.recipes.models import RecipeMeta, RecipeType
from medical_llm_workflow.Domain.prompts.models import PromptTemplate


class TwoStageVerificationRecipe(Recipe):
    """基于临床验证与多维证据比对的推理策略模版类。"""

    # 配置该 Recipe 的元信息与可视化标签
    meta = RecipeMeta(
        recipe_type=RecipeType.TWO_STAGE_VERIFICATION,
        name="Medical Reasoning - Two Stage Verification",
        description="初始诊断 -> 基本信息评估 -> 症状体格评估 -> 实验室评估 -> 影像评估 -> 最终诊断",
    )

    def build_task_configs(self) -> List[TaskConfig]:
        """构建流水线全流程任务配置对象列表，模拟基于线性链路的复杂验证推理步骤。"""
        
        # 提取各个 Agent 公共的角色定位和系统预设提示词
        profile = (
            "1.You are an experienced clinical medical expert.\n"
            "2.You are familiar with most medical knowledge bases, such as UpToDate/NCCN guidelines /WHO ICD-11, etc.\n"
            "3.You are good at differential diagnosis, especially for different diseases with similar symptoms.\n"
            "4.You are used to verifying the  diagnosis to avoid misdiagnosis. During the verification process, "
            "you have the ability to analyze the patient's symptoms, signs, medical history, and other clinical data, and perform multi-dimensional reasoning."
        )
        
        # 将原始脚本中的患者前缀提问作为上下文基础锚点
        question_prefix = (
            "The patient medical information is as follows. Don't make a diagnosis during the conversation, "
            "just understand and remember the patient's information. You're making a specific diagnosis after I give you the specific diagnostic rules later."
        )
        
        # 固化上下文供所有阶段使用
        base_context = f"{profile}\n\n{question_prefix}\n\nPatient Case:\n{{{{question_task}}}}\n\n"
        
        # 将原始脚本中的多轮提问，转化为独立且具备上下文传递依赖（{{上游Task ID}}）的单个静态任务节点
        return [
            # 步骤 1：初步粗略直觉诊断
            TaskConfig(
                id="Initial Diagnosis Task",
                type=TaskType.SINGLE_AGENT,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[],
                prompt_template=PromptTemplate(
                    text=(
                        f"{base_context}"
                        "Generate an initial diagnosis based on the provided patient information step-by-step, "
                        "and explain the reasoning process in detail."
                    ),
                ),
            ),
            # 步骤 2：人口统计学常识印证
            TaskConfig(
                id="Demographic Analysis Task",
                type=TaskType.SINGLE_AGENT,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[
                    "Initial Diagnosis Task",
                ],
                prompt_template=PromptTemplate(
                    text=(
                        f"{base_context}"
                        "Initial Diagnosis:\n{{Initial Diagnosis Task}}\n\n"
                        "1.**Analyze Patient's Demographic Information**: Confirm whether the patient’s age, gender, occupation, "
                        "and medical history support the initial diagnosis (e.g., femoral fractures, hip dislocation)."
                    ),
                ),
            ),
            # 步骤 3：核心体征症状冲突印证
            TaskConfig(
                id="Clinical Symptoms Analysis Task",
                type=TaskType.SINGLE_AGENT,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[
                    "Initial Diagnosis Task",
                    "Demographic Analysis Task",
                ],
                prompt_template=PromptTemplate(
                    text=(
                        f"{base_context}"
                        "Initial Diagnosis:\n{{Initial Diagnosis Task}}\n\n"
                        "Demographic Verification:\n{{Demographic Analysis Task}}\n\n"
                        "2.**Validate Symptoms and Physical Examination**: Confirm whether the physical findings (e.g., leg shortening, flexion, and rotation) "
                        "align with the initial diagnosis and whether symptoms such as groin pain point towards that diagnosis."
                    ),
                ),
            ),
            # 步骤 4：化验指标解读
            TaskConfig(
                id="Laboratory Analysis Task",
                type=TaskType.SINGLE_AGENT,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[
                    "Initial Diagnosis Task",
                    "Demographic Analysis Task",
                    "Clinical Symptoms Analysis Task",
                ],
                prompt_template=PromptTemplate(
                    text=(
                        f"{base_context}"
                        "Initial Diagnosis:\n{{Initial Diagnosis Task}}\n\n"
                        "Demographic Verification:\n{{Demographic Analysis Task}}\n\n"
                        "Clinical Symptoms Verification:\n{{Clinical Symptoms Analysis Task}}\n\n"
                        "3.**Laboratory Analysis**: Validate the relevance of the abnormality metrics to the candidate diagnosis "
                        "(e.g., the predictive value of elevated CEA for tumor recurrence)."
                    ),
                ),
            ),
            # 步骤 5：医学成像扫描辅助
            TaskConfig(
                id="Imaging Analysis Task",
                type=TaskType.SINGLE_AGENT,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[
                    "Initial Diagnosis Task",
                    "Demographic Analysis Task",
                    "Clinical Symptoms Analysis Task",
                    "Laboratory Analysis Task",
                ],
                prompt_template=PromptTemplate(
                    text=(
                        f"{base_context}"
                        "Initial Diagnosis:\n{{Initial Diagnosis Task}}\n\n"
                        "Demographic Verification:\n{{Demographic Analysis Task}}\n\n"
                        "Clinical Symptoms Verification:\n{{Clinical Symptoms Analysis Task}}\n\n"
                        "Laboratory Verification:\n{{Laboratory Analysis Task}}\n\n"
                        "4.**Medical Imaging Analysis**: If available，resolve whether imaging features (e.g., X-ray, ultrasound calcification, CT enhancement pattern) "
                        "meet initial diagnostic criteria (e.g., femoral neck fracture, hip dislocation)."
                    ),
                ),
            ),
            # 步骤 6：汇总综合评判并给解答
            TaskConfig(
                id="Final Validation Task",
                type=TaskType.SINGLE_AGENT,
                chatbot_config=self.chatbot_config,
                input_msg_sources=[
                    "Initial Diagnosis Task",
                    "Demographic Analysis Task",
                    "Clinical Symptoms Analysis Task",
                    "Laboratory Analysis Task",
                    "Imaging Analysis Task",
                ],
                prompt_template=PromptTemplate(
                    text=(
                        f"{base_context}"
                        "Initial Diagnosis:\n{{Initial Diagnosis Task}}\n\n"
                        "Demographic Verification:\n{{Demographic Analysis Task}}\n\n"
                        "Clinical Symptoms Verification:\n{{Clinical Symptoms Analysis Task}}\n\n"
                        "Laboratory Verification:\n{{Laboratory Analysis Task}}\n\n"
                        "Imaging Verification:\n{{Imaging Analysis Task}}\n\n"
                        "5.**Final Diagnosis**: Based on the comprehensive analysis of the above dimensions, confirm or revise the initial diagnosis as necessary.\n\n"
                        "Based on the entire medical analysis and validation process, please conduct a further analysis of these outcomes. "
                        "Extract the key information and present it in JSON format. The JSON output should adhere to the following structure:\n"
                        " {\n"
                        '     "Initial Answer": "The initial diagnosis answer of the diagnosis question within 8 words in the stage 1",\n'
                        '     "Initial Reasoning": "The diagnosis reasoning process in the stage 1, describe detailed reasoning logic whenever possible", \n'
                        '     "Final Answer": "The final diagnosis answer of the question after check within 8 words in the stage 2.",\n'
                        '     "Validate Reasoning": "The validate reasoning process in the stage 2, describe detailed check logic whenever possible"\n'
                        " }\n"
                    ),
                ),
            ),
        ]