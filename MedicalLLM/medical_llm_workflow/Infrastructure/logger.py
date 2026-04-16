"""
日志记录模块，用于解耦文件级的高效日志逻辑。

提供 WorkflowLogger 处理运行过程中生成的具体内容，确保各类日志的统一下盘机制。
"""

import json
from collections import defaultdict
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from medical_llm_workflow.utils import get_run_dir, print_log
from medical_llm_workflow.Service.storage_service import StorageService

if TYPE_CHECKING:
    from medical_llm_workflow.Domain.workflow_context.models import WorkflowContextPort
    from medical_llm_workflow.Service.workflow.workflow import DatasetInletItem, EvaluationResultItemForReport


class WorkflowLogger:
    """
    工作流日志记录器，统一处理整个系统在 Question 以及 Evaluator Report 维度上的落盘。
    """

    @classmethod
    def log_question(
        cls,
        dataset_type: str,
        question_index: int,
        workflow_context: "WorkflowContextPort",
        error: Optional[str] = None,
    ) -> None:
        """
        保存每道题单独的运行记录。
        同时涵盖生成易于呈现的 Markdown 文件与用于前端的 JSON 文件。
        包含了针对该题目的 Smart Extractor 以及各 Evaluator 对本题的评估结果。
        
        参数:
        - dataset_type: 当前所属的数据集名称，
        - question_index: 题目的标号/索引，
        - workflow_context: 当前题目的完整上下文记录，
        - error: 可选的错误信息，
        """
        run_dir = get_run_dir()
        
        content_lines = []
        content_lines.append(f"# Question {question_index} in {dataset_type}")
        content_lines.append("")
        
        if error:
            content_lines.append("## Error Processing This Question")
            content_lines.append(f"**Error Message:** {error}")
            content_lines.append("")
            
        structured_data = {
            "dataset_type": dataset_type,
            "question_index": question_index,
            "error": error,
            "tasks": [],
        }
        
        for task_record in workflow_context.get_all_records():
            task_config = task_record["task_config"]
            task_context = task_record["task_context"]
            
            task_id = getattr(task_config, "id", "Unnamed")
            type_str = task_config.type.value if hasattr(task_config, "type") else "Unknown"
            
            content_lines.append(f"## Task: {task_id} ({type_str})")
            
            input_msgs = []
            content_lines.append("### Inputs:")
            for msg in task_context.get("input", []):
                role_str = getattr(msg.get("role"), "value", msg.get("role", "UNKNOWN"))
                msg_content = str(msg.get("content", "")).strip()
                
                input_msgs.append({
                    "role": role_str,
                    "content": msg_content,
                })
                content_lines.append(f"**{role_str}**:\n```\n{msg_content}\n```\n")
                
            output_msgs = []
            content_lines.append("### Outputs:")
            for msg in task_context.get("output", []):
                role_str = getattr(msg.get("role"), "value", msg.get("role", "UNKNOWN"))
                msg_content = str(msg.get("content", "")).strip()
                
                output_msgs.append({
                    "role": role_str,
                    "content": msg_content,
                })
                content_lines.append(f"**{role_str}**:\n```\n{msg_content}\n```\n")
                
            structured_data["tasks"].append({
                "task_id": task_id,
                "task_type": type_str,
                "inputs": input_msgs,
                "outputs": output_msgs,
            })
            
        StorageService.write_question_run_data(
            run_dir=run_dir,
            dataset_type=dataset_type,
            question_index=question_index,
            structured_data=structured_data,
            markdown_content="\n".join(content_lines),
        )

    @classmethod
    def append_evaluation_log(
        cls,
        dataset_type: str,
        question_index: int,
        evaluator_name: str,
        input_msgs: List[Dict[str, Any]],
        output_msgs: List[Dict[str, Any]],
    ) -> None:
        """
        在评估阶段将 LLM-as-a-judge 的 I/O 内容单独追加到对应的题目日志中。
        """
        run_dir = get_run_dir()
        content_lines = []
        
        content_lines.append(f"## Task: evaluator_{evaluator_name} (llm_judge)")
        
        content_lines.append("### Inputs:")
        extracted_inputs = []
        for msg in input_msgs:
            role_str = str(msg.get("role", "UNKNOWN"))
            msg_content = str(msg.get("content", "")).strip()
            
            extracted_inputs.append({
                "role": role_str,
                "content": msg_content,
            })
            content_lines.append(f"**{role_str}**:\n```\n{msg_content}\n```\n")
            
        content_lines.append("### Outputs:")
        extracted_outputs = []
        for msg in output_msgs:
            role_str = str(msg.get("role", "UNKNOWN"))
            msg_content = str(msg.get("content", "")).strip()
            
            extracted_outputs.append({
                "role": role_str,
                "content": msg_content,
            })
            content_lines.append(f"**{role_str}**:\n```\n{msg_content}\n```\n")
            
        task_data = {
            "task_id": f"evaluator_{evaluator_name}",
            "task_type": "llm_judge",
            "inputs": extracted_inputs,
            "outputs": extracted_outputs,
        }
        
        StorageService.append_question_run_data(
            run_dir=run_dir,
            dataset_type=dataset_type,
            question_index=question_index,
            task_data=task_data,
            markdown_snippet="\n".join(content_lines),
        )

    @classmethod
    def log_evaluation_report(
        cls,
        evaluation_result_list: List["EvaluationResultItemForReport"],
        dataset_inlet_item_list: List["DatasetInletItem"],
    ) -> Dict[str, Any]:
        """
        基于评估结果，组织并落地最终合并后的测评总日志。
        
        参数:
        - evaluation_result_list: 所有包含评估细项的报告内容，
        - dataset_inlet_item_list: 数据集来源集合，
        """
        merged_report_lines: List[str] = []
        merged_report_lines.append("# Comprehensive Evaluation Report")
        merged_report_lines.append("")
        
        total_samples = len(dataset_inlet_item_list)
        merged_report_lines.append(f"- Total Samples Run: {total_samples}")
        merged_report_lines.append(f"- Total Evaluation Tasks: {len(evaluation_result_list)}")
        merged_report_lines.append("")

        dataset_eval_map = defaultdict(list)
        for item in evaluation_result_list:
            dataset_eval_map[item["dataset_type"]].append(item)

        for dataset_type, eval_items in dataset_eval_map.items():
            merged_report_lines.append(f"# Dataset: {dataset_type}")
            merged_report_lines.append("")
            
            for evaluation_item in eval_items:
                report_text = evaluation_item["report_text"]
                merged_report_lines.append(report_text)
                merged_report_lines.append("")

            merged_report_lines.append("## Details with Questions (Workflow Level)")
            merged_report_lines.append("")
            
            matched_inlet_items = [
                inlet 
                for inlet in dataset_inlet_item_list 
                if getattr(inlet.dataset_type, "value", str(inlet.dataset_type)) == dataset_type
            ]
            
            first_evaluator_records = eval_items[0]["result"]["records"]

            for idx, first_record in enumerate(first_evaluator_records):
                inlet_item = matched_inlet_items[idx]
                short_question = inlet_item.text_question.replace("\n", " ")
                
                pred = str(first_record.get("prediction", "No prediction"))
                truth = str(first_record.get("ground_truth", "Unknown"))
                
                scores_str = []
                for ev_item in eval_items:
                    ev_name = ev_item["evaluator_name"]
                    ev_record = ev_item["result"]["records"][idx]
                    scores_str.append(f"{ev_name}: {ev_record['score']}")
                
                merged_report_lines.append(f"**Sample {idx + 1}**")
                merged_report_lines.append(f"- **Scores**: {', '.join(scores_str)}")
                merged_report_lines.append(f"- **Question**: {short_question}")
                merged_report_lines.append(f"- **LLM Prediction**: {pred}")
                merged_report_lines.append(f"- **Ground Truth**: {truth}")
                merged_report_lines.append("")
        
        print_log("Evaluation Report Generated", prefix="[EVALUATOR]", debug=True)
        
        run_dir = get_run_dir()
        
        merged_report_path = StorageService.write_evaluation_report(
            run_dir=run_dir,
            report_content="\n".join(merged_report_lines),
        )

        return {
            "report_path": merged_report_path,
            "results": evaluation_result_list,
        }
