import asyncio
import json
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from medical_llm_workflow.main import run_workflow, DEFAULT_DATASET_CONFIG, DEFAULT_EVALUATOR_TYPE_LIST, DEFAULT_CHATBOT_CONFIG, DEFAULT_RECIPE_TYPE
from medical_llm_workflow.utils import sse_queue_var

from medical_llm_workflow.Domain.benchmark.Dataset.models import DatasetType
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType
from medical_llm_workflow.Infrastructure.LLM_client.models import ChatbotType, PoeChatbotModel
from medical_llm_workflow.Domain.recipes.models import RecipeType

app = FastAPI(title="Medical LLM Workflow Backend Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 方便开发期间跨域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunConfigPayload(BaseModel):
    dataset_type: str = DatasetType.MED_QA.value
    num_of_questions: int = 4
    evaluator_types: List[str] = [EvaluatorType.ACCURACY.value]
    chatbot_type: str = ChatbotType.POE.value
    model: str = PoeChatbotModel.GPT_5_4_NANO.value
    temperature: float = 0.7
    max_tokens: int = 2048
    recipe_type: Optional[str] = None
    custom_tasks: Optional[List[dict]] = None



@app.get("/api/options")
async def get_workflow_options():
    """提供给前端所有可用的工作流配置选项"""
    return {
        "datasets": [{"label": e.name, "value": e.value} for e in DatasetType],
        "evaluators": [{"label": e.name, "value": e.value} for e in EvaluatorType],
        "chatbotTypes": [{"label": e.name, "value": e.value} for e in ChatbotType],
        "models": [{"label": e.name, "value": e.value} for e in PoeChatbotModel if e != PoeChatbotModel.EMPTY_MODEL],
        "recipes": [{"label": e.name, "value": e.value} for e in RecipeType],
    }


@app.post("/api/run")
async def run_workflow(config: RunConfigPayload):
    """
    单点傻瓜式调用接口：执行由前端传入的配置参数的 workflow。
    通过 Server-Sent Events (SSE) 向前端实时反馈控制台所生成的日志，
    并在最后一并返回评估报告和纯净工作流 md 文件。
    """
    
    # 建立一条协程间通信的消息队列
    queue = asyncio.Queue()

    async def workflow_runner():
        """执行流的具体后台任务。"""
        # 将这个队列绑定进当前新起的 Task 子上下文中。整个堆栈往下共享此状态。
        token = sse_queue_var.set(queue)
        try:
            # 组装传入的配置
            dataset_kwargs = {
                "dataset_type": DatasetType(config.dataset_type),
                "num_of_questions": config.num_of_questions,
            }
            evaluator_types = [EvaluatorType(e) for e in config.evaluator_types]
            chatbot_config = {
                "chatbot_type": ChatbotType(config.chatbot_type),
                "model": PoeChatbotModel(config.model),
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }
            
            # 支持通过 recipe 或者 custom_tasks 来执行工作流
            recipe_type = None
            if config.recipe_type:
                recipe_type = RecipeType(config.recipe_type)
                
            custom_task_config_list = None
            if config.custom_tasks:
                from medical_llm_workflow.Domain.tasks import TaskConfig
                custom_task_config_list = [TaskConfig.model_validate(task_dict) for task_dict in config.custom_tasks]
            
            # 执行工作流
            await run_workflow(
                dataset_kwargs=dataset_kwargs,
                evaluator_type_list=evaluator_types,
                chatbot_config=chatbot_config,
                recipe_type=recipe_type,
                custom_task_config_list=custom_task_config_list
            )
            
            # Workflow 执行完后，统一组装返回
            eval_report_path = "evaluation_report.md"
            workflow_log_path = "workflow.md"
            
            eval_content = ""
            if os.path.exists(eval_report_path):
                with open(eval_report_path, "r", encoding="utf-8") as f:
                    eval_content = f.read()
                    
            log_content = ""
            if os.path.exists(workflow_log_path):
                with open(workflow_log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()
                    
            # 通过 [DONE] 标签结束并传递文件内容
            final_payload = {
                "status": "DONE",
                "evaluation_report": eval_content,
                "workflow_log": log_content,
            }
            await queue.put(f"[DONE] {json.dumps(final_payload)}")
            
        except Exception as e:
            error_payload = {
                "status": "ERROR",
                "message": str(e),
            }
            await queue.put(f"[DONE] {json.dumps(error_payload)}")
        finally:
            sse_queue_var.reset(token)

    async def event_generator():
        """源源不断取数据推送 SSE。"""
        
        # 启动 workflow worker
        asyncio.create_task(workflow_runner())
        
        while True:
            # 拿到队列消息
            message = await queue.get()
            
            # [DONE] 标志流结束
            if message.startswith("[DONE] "):
                yield f"data: {message}\n\n"
                break
                
            # SSE 规范：必须按 data: [内容] \n\n 格式推流
            yield f"data: {json.dumps({'status': 'STREAMING', 'log': message})}\n\n"

    # 以长连接建立数据传输响应
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # 为了防止某些浏览器/代理默认缓冲，开启以下选项
            "X-Accel-Buffering": "no",
        }
    )


if __name__ == "__main__":
    uvicorn.run("medical_llm_workflow.server:app", host="0.0.0.0", port=8000, reload=True)

