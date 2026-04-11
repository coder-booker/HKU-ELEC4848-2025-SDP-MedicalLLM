import asyncio
import json
import os
from contextvars import ContextVar
from typing import Any, Dict
from datetime import datetime


from medical_llm_workflow.serect import Secrets


_IS_LOG_INITIALIZED = False

# 全局上下文变量：承载针对单一工作流运行生命周期的 SSE 队列
sse_queue_var: ContextVar[asyncio.Queue | None] = ContextVar("sse_queue", default=None)
# 全局上下文变量：承载针对单一工作流运行的独立输出目录
run_dir_var: ContextVar[str] = ContextVar("run_dir", default=Secrets.RESULT_DIR)

def get_run_dir() -> str:
    return run_dir_var.get()


def emit_event(
    event_type: str,
    data: Dict[str, Any] = None,
) -> None:
    """
    向前端发送结构化状态事件。

    参数:
    - event_type: 字符串，表示事件名称（如 "WORKFLOW_START", "TASK_START"）
    - data: 字典，包含该事件的具体荷载数据（如 task 结果，当前处理到第几个 dataset 等）
    """
    if data is None:
        data = {}
        
    try:
        queue = sse_queue_var.get()
        
        if queue is not None:
            # 通过特定前缀 [[EVENT]] 与传统 print_log 字符串区分
            event_payload = {
                "type": event_type,
                "data": data,
            }
            
            queue.put_nowait(f"[[EVENT]] {json.dumps(event_payload, ensure_ascii=False)}")
            
    except (LookupError, asyncio.QueueFull):
        pass


def print_log(message: Any, prefix: str = "", debug_only: bool = False) -> None:
    """
    统一的打印封装函数。

    参数:
    - message: 要打印的信息内容
    - prefix: 打印信息前缀，如 "[WORKFLOW]", "[TASK]", "[EVALUATOR]" 等
    - debug_only: 是否受 debug 控制。当前项目中默认设为 False 等等。

    说明:
    将所有 \n 正确渲染出换行，并封装 debug 开关。
    如果信息是多行也会统一前缀。
    """
    global _IS_LOG_INITIALIZED
    if debug_only and not getattr(Secrets, "DEBUG", False):
        return

    # 将非字符串类型转换为字符串以进行替换
    msg_str = str(message)
    
    # 替换无法渲染的字面量 \n 为实际换行符
    msg_str = msg_str.replace("\\n", "\n")
    
    # 移除其他多余的反斜杠（如转义字符等）
    msg_str = msg_str.replace("\\", "")
    
    # 提取无前缀纯文本以供 Markdown 文件渲染使用
    raw_msg_str = msg_str
    
    # 根据是否有前缀进行排版处理
    if prefix:
        lines = msg_str.split("\n")
        msg_str = "\n".join(f"{prefix} {line}" if line.strip() else line for line in lines)
        
    print(msg_str)
    
    # 如果协程上下文内有被激活的队列，无阻塞地将排版后的字元塞入队列发给前端 SSE
    try:
        queue = sse_queue_var.get()
        if queue is not None:
            queue.put_nowait(msg_str)
    except (LookupError, asyncio.QueueFull):
        pass
    
    # 获取写入模式，只在当次程序运行的第一次写入采用覆写 (w)，后续追加 (a)
    mode = "a" if _IS_LOG_INITIALIZED else "w"
    _IS_LOG_INITIALIZED = True
    
    run_dir = get_run_dir()
    workflow_log_path = os.path.join(run_dir, Secrets.WORKFLOW_LOG_FILENAME)
    
    # 写入根目录下的 log 文件
    os.makedirs(os.path.dirname(workflow_log_path), exist_ok=True)
    with open(workflow_log_path, mode, encoding="utf-8") as f:
        f.write(msg_str + "\n")


def save_question_log(
    dataset_type: str,
    question_index: int,
    workflow_context: Any,
) -> None:
    """
    保存每道题单独的运行记录，形成独立的 Markdown 文件。

    参数:
    - dataset_type: 字符串，当前所属的数据集名称
    - question_index: 整数，题目的标号/索引
    - workflow_context: 当前题目的完整上下文记录，含有所有的任务执行流
    """
    run_dir = get_run_dir()
    # 构建当前数据集的文件存储目录
    target_dir = os.path.join(run_dir, dataset_type)
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = os.path.join(target_dir, f"question_{question_index}.md")
    
    # 构建内容报告字符串
    content_lines = [
        f"# Workflow Exeuction Record - Question {question_index}",
        f"\n**Dataset**: `{dataset_type}`\n",
    ]
    
    for task_record in workflow_context.get_all_records():
        task_config = task_record["task_config"]
        task_context = task_record["task_context"]
        
        task_id = getattr(task_config, 'id', 'Unnamed')
        type_str = task_config.type.value if hasattr(task_config, 'type') else "Unknown"
        
        content_lines.append(f"## Task: {task_id} (Type: {type_str})\n")
        
        # 记录输入
        content_lines.append("### Input Messages\n")
        input_msgs = task_context.get("input", [])
        for idx, msg in enumerate(input_msgs):
            role_str = getattr(msg.get('role'), 'value', msg.get('role', 'UNKNOWN'))
            content_lines.append(f"**[{role_str.upper()}]**")
            content_lines.append("```text\n" + str(msg.get('content', '')).strip() + "\n```\n")
            
        # 记录输出
        content_lines.append("### Output Messages\n")
        output_msgs = task_context.get("output", [])
        for idx, msg in enumerate(output_msgs):
            role_str = getattr(msg.get('role'), 'value', msg.get('role', 'UNKNOWN'))
            content_lines.append(f"**[{role_str.upper()}]**")
            content_lines.append("```text\n" + str(msg.get('content', '')).strip() + "\n```\n")
            
        content_lines.append("---\n")
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content_lines))
