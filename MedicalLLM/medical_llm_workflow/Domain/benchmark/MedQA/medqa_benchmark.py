import json
from typing import List
import random as rd


from medical_llm_workflow.schemas import MedQABenchmarkProtocal

class MedQABenchmark:
    """MedQA 基准测试协议。"""
    
    @staticmethod
    def get_json_questions(random: bool, num: int) -> List[MedQABenchmarkProtocal]:
        """
        获取指定数量的医学问答问题。

        Args:
            num: 问题数量

        Returns:
            问题列表
        """
        data = None
        
        # 加载 json 文件
        json_data_list = []
        with open(r"D:\learning\SDP\MedicalLLM\dataset\med\data_clean\questions\US\train.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                parsed_line = json.loads(line)
                # print(parsed_line)
                # exit(0)
                json_data_list.append(parsed_line)
        
        selected_json_data_list = json_data_list[:num] if not random else rd.sample(json_data_list, num)
        
        # {"question": "A 23-year-old pregnant woman at 22 weeks gestation presents with burning upon urination. She states it started 1 day ago and has been worsening despite drinking more water and taking cranberry extract. She otherwise feels well and is followed by a doctor for her pregnancy. Her temperature is 97.7°F (36.5°C), blood pressure is 122/77 mmHg, pulse is 80/min, respirations are 19/min, and oxygen saturation is 98% on room air. Physical exam is notable for an absence of costovertebral angle tenderness and a gravid uterus. Which of the following is the best treatment for this patient?", "answer": "Nitrofurantoin", "options": {"A": "Ampicillin", "B": "Ceftriaxone", "C": "Ciprofloxacin", "D": "Doxycycline", "E": "Nitrofurantoin"}, "meta_info": "step2&3", "answer_idx": "E"}
        json_questions: List[MedQABenchmarkProtocal] = []
        for item in selected_json_data_list:
            json_questions.append(MedQABenchmarkProtocal(
                question=item["question"],
                options=[
                    item["options"]["A"],
                    item["options"]["B"],
                    item["options"]["C"],
                    item["options"]["D"],
                    item["options"]["E"],
                ],
                answer=item["answer"],
            ))
        
        return json_questions
    
    @staticmethod
    def get_text_questions(random: bool, num: int) -> List[str]:
        """
        获取指定数量的医学问答问题（文本格式）。

        Args:
            num: 问题数量

        Returns:
            问题列表（文本格式）
        """
        json_questions = MedQABenchmark.get_json_questions(random, num)
        
        text_questions = []
        for item in json_questions:
            question_text = f"Question: \n{item.question}\n"
            for idx, option in enumerate(item.options):
                question_text += f"{chr(65 + idx)}. {option}\n"
            
            text_questions.append(question_text)
        
        return text_questions
    