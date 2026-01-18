from medical_llm_workflow.config import PromptTemplate, PromptType, LanguageType
from typing import List, Optional


SYSTEM_PROMPT = {
    "en": (
        "You are a cautious internal medicine resident doctor. You provide educational explanations only and do not give prescriptions.\n"
    ),
    "zh": (
        "你现在的角色是一名谨慎的内科住院医生。你只提供教育性的解释，不给出处方建议。\n"
    )
}

QUESTION_PROMPT = {
    "en": (
        "Given the following patient case information, please provide an initial diagnostic opinion.\n"
    ),
    "zh": (
        "给定以下病例信息，请给出初步诊断意见。\n"
    ),
}

PATIENT_CASE_PROMPT = {
    "en": (
        "Patient Case:\n"
        "{{CASE}}\n\n"
    ),
    "zh": (
        "病例信息：\n"
        "{{CASE}}\n\n"
    ),
}

STRUCTURED_PROMPT = {
    "en": (
        "Please structure your answer as follows:\n"
        "1. Key information summary: Use 2–4 sentences to summarize the patient’s main symptoms, physical findings, and key investigation results.\n"
        "2. Problem list: List 3–6 clinical problems you consider most important, including relevant diseases, mechanisms, or key guideline points.\n"
        "3. Differential diagnosis list: List 3–5 possible diagnoses, ordered from most urgent / high‑risk to less urgent.\n"
        "4. Evidence analysis: For each possible diagnosis, list the evidence supporting this diagnosis and the evidence not supporting or arguing against this diagnosis.\n"
        "5. Suggested further investigations: List 2–5 additional investigations you think should be performed, and for each one, explain the key clinical question it is intended to answer.\n"
        "6. Initial working diagnosis: Provide the diagnosis you consider most likely, and explain your reasoning in 3–5 sentences.\n"
    ),
    "zh": (
        "请按以下结构输出你的最终回答：\n"
        "1. 关键信息摘要：用 2–4 句话总结患者的主要症状、体征和关键检查结果。\n"
        "2. 问题列表（Problem list）：列出 3–6 条你认为最重要的临床问题，请包含相关的疾病 / 机制的知识关键点。\n"
        "3. 鉴别诊断列表：列出 3–5 个可能诊断，按危重程度从高到低排序。\n"
        "4. 证据分析：对每个可能诊断，分别列出“支持该诊断的依据”和“不支持或反对该诊断的依据”。\n"
        "5. 建议的进一步检查：列出 2–5 项你认为应当进行的进一步检查，并说明每一项检查希望回答的关键临床问题。\n"
        "6. 初步工作诊断：给出你认为最可能的诊断，并用 3–5 句话解释理由。\n"
    ),
}

COT_PROMPT = {
    "en": (
        "Please show your full reasoning process, do not skip steps or provide a brief conclusion only.\n"
    ),
    "zh": (
        "请展示你的完整推理过程，不要跳过推理过程或只给出简短结论\n"
    ),
}

SELF_REFINE_REVIEW_PROMPT = {
    "en": (
        "You are now an experienced senior physician whose task is to critically review a resident doctor's diagnostic reasoning and conclusions.\n"
        "Pay special attention to: missed critical diagnoses, reasoning that contradicts the history/signs, overconfidence or dangerous recommendations.\n"
        "Please review and critique the following answer to the patient case information.\n\n"
        f'{PATIENT_CASE_PROMPT["en"]}'
        "Resident Doctor's Diagnosis:\n"
        "{{INITIAL_ANSWER}}\n\n"
    ),
    "zh": (
        "你现在的角色是一名经验丰富的上级医生，你的任务是严格审查一名住院医生写的病例诊断思路与结论。\n"
        "请特别关注：是否遗漏危重诊断、是否有与病史/体征矛盾的推理、是否出现过度自信或危险建议。\n"
        "请审查并批评以下对病例信息的回答。\n\n"
        f'{PATIENT_CASE_PROMPT["zh"]}'
        "住院医生的诊断：\n"
        "{{INITIAL_ANSWER}}\n\n"
    ),
}

SELF_REFINE_REFINE_PROMPT = {
    "en": (
        "Please refine your answer to the patient case information based on the provided critique.\n\n"
        f'{PATIENT_CASE_PROMPT["en"]}'
        "Your Previous Initial Diagnosis:\n"
        "{{INITIAL_ANSWER}}\n\n"
        "Senior Physician's Critique:\n"
        "{{CRITIQUE}}\n\n"
        "Please provide a final, improved diagnostic opinion.\n"
    ),
    "zh": (
        "请根据所提供的批评意见，改进你对病例信息的回答。\n\n"
        f'{PATIENT_CASE_PROMPT["zh"]}'
        "你此前的初步诊断：\n"
        "{{INITIAL_ANSWER}}\n\n"
        "上级医生的批评意见：\n"
        "{{CRITIQUE}}\n\n"
        "最后总结一份更完善的诊断意见。\n"
    ),
}


def prompt_factory(prompts_type_list: Optional[List[PromptType]], language: LanguageType) -> List[PromptTemplate]:
    """根据提示词类型列表生成复合提示词模板。

    Args:
        prompts_type_list: 提示词类型列表，按顺序组合。目前只支持 structured、cot、self_refine 三种类型的任意组合。
    
    后续可以支持自定义 prompt
    """
    if prompts_type_list == None or len(prompts_type_list) == 0:
        return [PromptTemplate(
            system=SYSTEM_PROMPT[language],
            user=(
                f'{QUESTION_PROMPT[language]}'
                f'{PATIENT_CASE_PROMPT[language]}'
            ),
        )]
    elif prompts_type_list == [PromptType.STRUCTURED]:
        return [PromptTemplate(
            system=SYSTEM_PROMPT[language],
            user=(
                f'{QUESTION_PROMPT[language]}'
                f'{PATIENT_CASE_PROMPT[language]}'
                f'{STRUCTURED_PROMPT[language]}'
            ),
        )]
    elif prompts_type_list == [PromptType.COT]:
        return [PromptTemplate(
            system=SYSTEM_PROMPT[language],
            user=(
                f'{QUESTION_PROMPT[language]}'
                f'{PATIENT_CASE_PROMPT[language]}'
                f'{COT_PROMPT[language]}'
            ),
        )]
    elif prompts_type_list == [PromptType.STRUCTURED, PromptType.COT] or prompts_type_list == [PromptType.COT, PromptType.STRUCTURED]:
        return [PromptTemplate(
            system=SYSTEM_PROMPT[language],
            user=(
                f'{QUESTION_PROMPT[language]}'
                f'{PATIENT_CASE_PROMPT[language]}'
                f'{COT_PROMPT[language]}'
                f'{STRUCTURED_PROMPT[language]}'
            ),
        )]
    elif PromptType.SELF_REFINE in prompts_type_list:
        # 生成三个提示词模板，供 Self-Refine 任务使用
        # 同步判断是否包含 STRUCTURED 和 COT
        has_structured = PromptType.STRUCTURED in prompts_type_list
        has_cot = PromptType.COT in prompts_type_list
        
        initial_user = (
            f'{QUESTION_PROMPT[language]}'
            f'{PATIENT_CASE_PROMPT[language]}'
            f'{STRUCTURED_PROMPT[language]}' if has_structured else ''
            f'{COT_PROMPT[language]}' if has_cot else ''
        )
        review_user = SELF_REFINE_REVIEW_PROMPT[language]
        refine_user = (
            f'{SELF_REFINE_REFINE_PROMPT[language]}'
            f'{STRUCTURED_PROMPT[language]}' if has_structured else ''
            f'{COT_PROMPT[language]}' if has_cot else ''
        )
        
        return [
            PromptTemplate(
                system=SYSTEM_PROMPT[language],
                user=initial_user,
            ),
            PromptTemplate(
                system=SYSTEM_PROMPT[language],
                user=review_user,
            ),
            PromptTemplate(
                system=SYSTEM_PROMPT[language],
                user=refine_user,
            ),
        ]
        
        