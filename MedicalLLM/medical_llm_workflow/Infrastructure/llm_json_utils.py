"""基础设施层工具函数。"""

import json
from typing import Any, Dict, List

from medical_llm_workflow.schemas.models import ConversationMessage, ConversationMessageRole, ConversationMessageStatus
from medical_llm_workflow.utils import print_log


async def call_llm_with_json_retry(
    client: Any,
    messages: List[ConversationMessage],
    chatbot_config: Dict[str, Any],
    max_retries: int = 1,
) -> Dict[str, Any]:
    """
    调用大语言模型并强制将其响应解析为 JSON 字典。
    包含规则过滤（提取首尾大括号内的内容）和指定的重试次数。
    
    参数:
    - client: LLM 调用的客户端实例
    - messages: 对话消息列表
    - chatbot_config: 聊天机器人配置
    - max_retries: 最大重试次数
    
    返回:
    - 解析成功后的字典；如果失败则包含 "error" 键
    """
    # 拷贝一份以防污染原始 messages
    current_messages = list(messages)
    last_error = ""

    for attempt in range(max_retries + 1):
        try:
            response = await client.call_chatbot(current_messages, chatbot_config)
            
            # Rule base filtering: 忽略不是花括号的内容
            text = response.strip()
            
            # 去除可能包含的 markdown 标签
            if "```json" in text:
                text = text.split("```json")[-1]
            if "```" in text:
                text = text.split("```")[0]
                
            start_idx = text.find("{")
            end_idx = text.rfind("}")
            
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                json_str = text[start_idx:end_idx+1]
            else:
                json_str = text
                
            parsed = json.loads(json_str)
            return parsed
            
        except json.JSONDecodeError as e:
            last_error = f"JSON parsing failed: {str(e)} | Raw response: {response}"
            if attempt < max_retries:
                current_messages.append(
                    {
                        "role": ConversationMessageRole.BOT,
                        "content": response,
                        "status": ConversationMessageStatus.NORMAL,
                    }
                )
                current_messages.append(
                    {
                        "role": ConversationMessageRole.USER,
                        "content": "Your previous response was not a valid JSON. Please strictly output ONLY a valid JSON object without markdown or extra text.",
                        "status": ConversationMessageStatus.NORMAL,
                    }
                )
                print_log(f"LLM returned invalid JSON, initiating retry {attempt + 1}/{max_retries}...", prefix="[WARN]")

        except Exception as e:
            # 对于网络或其他直接异常不进行 JSON 格式的重复尝试
            last_error = f"Execution error during LLM call: {str(e)}"
            break
            
    print_log(f"Failed to get valid JSON from LLM. Chain: {last_error}", prefix="[ERROR]")
    
    return {
        "error": last_error,
    }
