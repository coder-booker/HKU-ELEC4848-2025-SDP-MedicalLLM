import asyncio
import json
from contextvars import ContextVar
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from medical_llm_workflow.Domain.workflow_context.models import WorkflowContextPort

from medical_llm_workflow.app_settings import AppSettings
from medical_llm_workflow.Service.storage_service import StorageService


_IS_LOG_INITIALIZED = False

# 全局上下文变量：承载针对单一工作流运行生命周期的 SSE 队列
sse_queue_var: ContextVar[asyncio.Queue | None] = ContextVar("sse_queue", default=None)
# 全局上下文变量：承载针对单一工作流运行的独立输出目录
run_dir_var: ContextVar[str] = ContextVar("run_dir", default=AppSettings.RESULT_DIR)

def get_run_dir() -> str:
    return run_dir_var.get()


def emit_event(
    event_type: str,
    data: Optional[Dict[str, Any]] = None,
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


def print_log(message: Any, prefix: str = "", debug: bool = False) -> None:
    """
    统一的打印封装函数。

    参数:
    - message: 要打印的信息内容
    - prefix: 打印信息前缀，如 "[WORKFLOW]", "[TASK]", "[EVALUATOR]" 等
    - debug: 是否受 debug 控制。当前项目中默认设为 False 等等。

    说明:
    将所有 \n 正确渲染出换行，并封装 debug 开关。
    如果信息是多行也会统一前缀。
    """
    global _IS_LOG_INITIALIZED
    # if debug and not getattr(AppSettings, "DEBUG", False):
    #     return

    # 将非字符串类型转换为字符串以进行替换
    msg_str = str(message)
    
    # 替换无法渲染的字面量 \n 为实际换行符
    msg_str = msg_str.replace("\\n", "\n")
    
    # 移除其他多余的反斜杠（如转义字符等）
    msg_str = msg_str.replace("\\", "")
    
    # 提取无前缀纯文本以供 Markdown 文件渲染使用
    if debug and AppSettings.DEBUG:
        print(msg_str)
    
    # 根据是否有前缀进行排版处理
    if prefix:
        lines = msg_str.split("\n")
        msg_str = "\n".join(f"{prefix} {line}" if line.strip() else line for line in lines)
        
    
    # 如果协程上下文内有被激活的队列，无阻塞地将排版后的字元塞入队列发给前端 SSE
    try:
        queue = sse_queue_var.get()
        if queue is not None:
            queue.put_nowait(msg_str)
    except (LookupError, asyncio.QueueFull):
        pass
    
    # 获取写入模式，只在当次程序运行的第一次写入采用覆写 (w)，后续追加 (a)
    overwrite = not _IS_LOG_INITIALIZED
    _IS_LOG_INITIALIZED = True
    
    run_dir = get_run_dir()
    
    # 将日志具体写入硬盘的逻辑委派给存储服务
    StorageService.write_workflow_log(
        run_dir=run_dir,
        msg_str=msg_str,
        overwrite=overwrite,
    )


def save_question_log(
    dataset_type: str,
    question_index: int,
    workflow_context: "WorkflowContextPort",
    error: Optional[str] = None,
) -> None:
    """
    保存每道题单独的运行记录。
    不仅会生成易于人类阅读的 Markdown 文件，还会生成用于前端结构化展示的 JSON 文件。

    参数:
    - dataset_type: 字符串，当前所属的数据集名称
    - question_index: 整数，题目的标号/索引
    - workflow_context: 当前题目的完整上下文记录，含有所有的任务执行流
    - error: 可选，如果有错误发生则传入错误信息
    """
    run_dir = get_run_dir()
    
    # ---------------- 构建前置数据：Markdown 与结构化 JSON ----------------
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
        
        # 提取各个关键信息，为前端展示作准备
        task_id = getattr(task_config, 'id', 'Unnamed')
        type_str = task_config.type.value if hasattr(task_config, 'type') else "Unknown"
        
        content_lines.append(f"## Task: {task_id} ({type_str})")
        
        # 整理输入
        input_msgs = []
        content_lines.append("### Inputs:")
        for msg in task_context.get("input", []):
            role_str = getattr(msg.get('role'), 'value', msg.get('role', 'UNKNOWN'))
            msg_content = str(msg.get('content', '')).strip()
            
            input_msgs.append({
                "role": role_str,
                "content": msg_content,
            })
            content_lines.append(f"**{role_str}**:\n{msg_content}\n")
            
        # 整理输出
        output_msgs = []
        content_lines.append("### Outputs:")
        for msg in task_context.get("output", []):
            role_str = getattr(msg.get('role'), 'value', msg.get('role', 'UNKNOWN'))
            msg_content = str(msg.get('content', '')).strip()
            
            output_msgs.append({
                "role": role_str,
                "content": msg_content,
            })
            content_lines.append(f"**{role_str}**:\n{msg_content}\n")
            
        # 增加一笔结构化记录
        structured_data["tasks"].append({
            "task_id": task_id,
            "task_type": type_str,
            "inputs": input_msgs,
            "outputs": output_msgs,
        })
        
    # ---------------- 委派给具体存储服务以落盘 ----------------
    StorageService.write_question_run_data(
        run_dir=run_dir,
        dataset_type=dataset_type,
        question_index=question_index,
        structured_data=structured_data,
        markdown_content="\n".join(content_lines),
    )
