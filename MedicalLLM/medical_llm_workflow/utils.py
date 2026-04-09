from typing import Any
from medical_llm_workflow.serect import Secrets


_IS_LOG_INITIALIZED = False


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
    
    # 获取写入模式，只在当次程序运行的第一次写入采用覆写 (w)，后续追加 (a)
    mode = "a" if _IS_LOG_INITIALIZED else "w"
    _IS_LOG_INITIALIZED = True
    
    # 写入根目录下的 log 文件
    with open("workflow.log", mode, encoding="utf-8") as f:
        f.write(msg_str + "\n")
        
    # 写入根目录下的 md 文件，内容不带前缀
    with open("workflow.md", mode, encoding="utf-8") as f:
        f.write(raw_msg_str + "\n\n")
