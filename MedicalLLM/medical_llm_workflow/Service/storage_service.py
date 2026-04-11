"""本地文件存取服务封装。

此模块封装了所有的路径拼接与文件读写操作，避免 I/O 逻辑污染工作流的业务代码。
将存储细节隔离开，保证扩展性和整洁性。
"""

import os
import json
from typing import Any, Dict, Optional

from medical_llm_workflow.serect import Secrets


class StorageService:
    """存储服务类，统一负责本地文件系统生命周期的维护、读写与路径组装。"""

    @staticmethod
    def read_question_json(
        run_id: str,
        dataset_type: str,
        question_index: int,
    ) -> Optional[Dict[str, Any]]:
        """读取指定题目运行的结构化 JSON 日志。"""
        json_path = os.path.join(
            Secrets.RESULT_DIR,
            run_id,
            dataset_type,
            f"question_{question_index}.json",
        )
        
        if not os.path.exists(json_path):
            return None
            
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def write_question_run_data(
        run_dir: str,
        dataset_type: str,
        question_index: int,
        structured_data: Dict[str, Any],
        markdown_content: str,
    ) -> None:
        """把单次题目的运行结果同时写为 JSON 与 Markdown 双语文件落地。"""
        target_dir = os.path.join(
            run_dir,
            dataset_type,
        )
        os.makedirs(target_dir, exist_ok=True)

        # 写入前端所需的 JSON 数据
        json_path = os.path.join(
            target_dir,
            f"question_{question_index}.json",
        )
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(
                structured_data,
                jf,
                ensure_ascii=False,
                indent=2,
            )

        # 写入人类可读 Markdown
        md_path = os.path.join(
            target_dir,
            f"question_{question_index}.md",
        )
        with open(md_path, "w", encoding="utf-8") as mf:
            mf.write(markdown_content)

    @staticmethod
    def write_workflow_log(
        run_dir: str,
        msg_str: str,
        overwrite: bool = False,
    ) -> None:
        """追加或覆盖写入工作流的全局运行日志。"""
        log_path = os.path.join(
            run_dir,
            Secrets.WORKFLOW_LOG_FILENAME,
        )
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        # 根据传入标志选用覆写或是追加
        mode = "w" if overwrite else "a"
        
        with open(log_path, mode, encoding="utf-8") as f:
            f.write(msg_str + "\n")
    
    @staticmethod
    def read_workflow_log(
        run_dir: str,
    ) -> str:
        """读取工作流全局运行日志内容。"""
        log_path = os.path.join(
            run_dir,
            Secrets.WORKFLOW_LOG_FILENAME,
        )
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    @staticmethod
    def write_evaluation_report(
        run_dir: str,
        report_content: str,
    ) -> str:
        """写入总结性的 Markdown 评测报告并返回路径。"""
        report_path = os.path.join(
            run_dir,
            Secrets.EVALUATION_REPORT_FILENAME,
        )
        os.makedirs(run_dir, exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        return report_path
        
    @staticmethod
    def read_evaluation_report(
        run_dir: str,
    ) -> str:
        """读取总结性的评测报告内容。"""
        report_path = os.path.join(
            run_dir,
            Secrets.EVALUATION_REPORT_FILENAME,
        )
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
