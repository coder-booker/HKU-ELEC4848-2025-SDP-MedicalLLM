import asyncio
import json
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import datetime

from medical_llm_workflow.main import run_core_workflow, DEFAULT_CHATBOT_CONFIG
from medical_llm_workflow.utils import sse_queue_var, run_dir_var, emit_event, print_log

from medical_llm_workflow.Domain.benchmark.Dataset import DatasetType, DatasetConfig
from medical_llm_workflow.Domain.benchmark.Evaluator.models import EvaluatorType
from medical_llm_workflow.Domain.benchmark.EvaluatorAdaptor.evaluator_adaptor import DATASET_EVALUATOR_SCHEMA_MAP
from medical_llm_workflow.Domain.tasks import TaskConfig
from medical_llm_workflow.Infrastructure.LLM_client.models import ChatbotType, PoeChatbotModel
from medical_llm_workflow.Domain.recipes.models import RecipeType
from medical_llm_workflow.Domain.recipes.recipe_factory import RecipeFactory
from medical_llm_workflow.app_settings import AppSettings
from medical_llm_workflow.Service.storage_service import StorageService


app = FastAPI(title="Medical LLM Workflow Backend Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 方便开发期间跨域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DatasetConfigPayload(BaseModel):
    """
    单个数据集与问题数量配置。
    - dataset_type: str, 数据集类型
    - num_of_questions: int, 该数据集抽样问题数量
    - evaluator_types: List[str], 该数据集所需的评测器类型列表
    """

    dataset_type: str = DatasetType.MED_QA.value
    num_of_questions: int = 4
    evaluator_types: List[str] = [EvaluatorType.ACCURACY.value]


class RunConfigPayload(BaseModel):
    """
    工作流运行请求参数配置。
    - datasets: List[DatasetConfigPayload], 数据集与题目数及各自评测器配置列表
    - chatbot_type: str, 聊天机器人类型
    - model: str, 模型类型
    - temperature: float, 生成温度
    - max_tokens: int, 最大输出 Token 数
    - tasks: List[dict], 实际执行的任务配置列表
    """

    datasets: List[DatasetConfigPayload] = [DatasetConfigPayload()]
    chatbot_type: str = ChatbotType.POE.value
    model: str = PoeChatbotModel.GPT_5_4_NANO.value
    temperature: float = 0.7
    max_tokens: int = 2048
    tasks: List[dict] = []



@app.get("/api/options")
async def get_workflow_options():
    """提供给前端所有可用的工作流配置选项，包含解析完成的 Recipe"""
    print_log("Received request for workflow options.", prefix="[API /api/options]", debug=True)
    
    # 构建基础默认的 LLM 配置，用于实例化默认 Recipe 任务
    recipes_list = []
    for r_type in RecipeType:
        # 获取预设 Recipe 并解析为 task list
        recipe = RecipeFactory.get_recipe(
            recipe_type=r_type,
            chatbot_config=DEFAULT_CHATBOT_CONFIG,
        )
        task_configs = recipe.build_task_configs()
        
        recipes_list.append({
            "label": r_type.name,
            "value": r_type.value,
            # 将任务配置全量暴露给前端，允许前端自由查看与修改
            "tasks": [t.model_dump(exclude_none=True) for t in task_configs],
        })

    def get_supported_evaluators(dataset_val: str) -> List[str]:
        # 从 evaluator_adaptor 里面的 MAP 动态获取某数据集支持的 evaluator 类型
        supported = []
        try:
            dataset_enum = DatasetType(dataset_val)
            if dataset_enum in DATASET_EVALUATOR_SCHEMA_MAP:
                # 获取该数据集下有 schema 定义的 evaluator 列表 (键)
                supported = [eval_type.value for eval_type in DATASET_EVALUATOR_SCHEMA_MAP[dataset_enum].keys()]
        except ValueError:
            pass  # 如果传入未知的 dataset_val，直接忽略
        
        # 兼容性处理：如果 MAP 尚未覆盖到或没写，也可选择全部或者空列表
        return supported

    response_body = {
        "datasets": [
            {
                "label": e.name,
                "value": e.value,
                "supportedEvaluators": get_supported_evaluators(e.value)
            } for e in DatasetType
        ],
        "evaluators": [{"label": e.name, "value": e.value} for e in EvaluatorType],
        "chatbotTypes": [{"label": e.name, "value": e.value} for e in ChatbotType],
        "models": [{"label": e.name, "value": e.value} for e in PoeChatbotModel if e != PoeChatbotModel.EMPTY_MODEL],
        "recipes": recipes_list,
    }
    
    print_log(f"Response for /api/options:\n{json.dumps(response_body, indent=2, ensure_ascii=False)}", prefix="[API /api/options]", debug=True)
    return response_body


@app.get("/api/results/{run_id}/{dataset_type}/{question_index}")
async def get_question_result(
    run_id: str,
    dataset_type: str,
    question_index: int,
):
    """
    提供给前端的 API 接口。
    用于在点击题目列表项后，从指定的运行记录文件夹中读取某道题目的结构化 JSON 日志数据。
    """
    print_log(f"Received request for details: run_id={run_id}, dataset_type={dataset_type}, question_index={question_index}", prefix="[API /api/results]", debug=True)
    
    data = StorageService.read_question_json(
        run_id=run_id,
        dataset_type=dataset_type,
        question_index=question_index,
    )
    
    # 检查题目数据文件是否存在，如果不存在直接抛出 404
    if data is None:
        error_resp = {"error": "Result not found"}
        print_log(f"Response for /api/results: {error_resp} (404)", prefix="[API /api/results]", debug=True)
        return error_resp, 404
        
    print_log(f"Response for /api/results: Successfully returning structured data. (Payload omitted for brevity)", prefix="[API /api/results]", debug=True)
    return data

@app.post("/api/run")
async def run_workflow(config: RunConfigPayload):
    """
    单点傻瓜式调用接口：执行由前端传入的配置参数的 workflow。
    通过 Server-Sent Events (SSE) 向前端实时反馈控制台所生成的日志，
    并在最后一并返回评估报告和纯净工作流 md 文件。
    """
    print_log(f"Received request to run workflow. Body:\n{json.dumps(config.model_dump(), indent=2, ensure_ascii=False)}", prefix="[API /api/run]", debug=True)
    
    # 建立一条协程间通信的消息队列
    queue = asyncio.Queue()

    # 为工作流配置前端可见的时间戳
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 让存储服务进行单目录覆写以释放硬盘
    run_dir = StorageService.init_run_dir()

    async def workflow_runner():
        """执行流的具体后台任务。"""
        # 将这个队列绑定进当前新起的 Task 子上下文中。整个堆栈往下共享此状态。
        token = sse_queue_var.set(queue)
        dir_token = run_dir_var.set(run_dir)
        try:
            # 建立记录上下文事件，方便前端知晓本次请求实际记录存放位置
            emit_event(
                "WORKFLOW_STARTED", 
                {"run_id": ts},
            )
            # raise Exception("测试异常捕获机制")
            
            # 组装传入的评测集配置
            dataset_config_list = [
                DatasetConfig(
                    dataset_type=DatasetType(d.dataset_type),
                    num_of_questions=d.num_of_questions,
                    evaluator_type_list=[EvaluatorType(e) for e in d.evaluator_types],
                )
                for d in config.datasets
            ]
            
            # 后端不再处理 recipe 和 custom_tasks 的判断
            # 所有任务相关参数全由前端通过 `tasks` 数组传入，确保真正的配置自治

            task_config_list = [
                TaskConfig.model_validate(task_dict) 
                for task_dict in config.tasks
            ]
            
            # 执行工作流，参数已被完整处理
            contexts, report_info = await run_core_workflow(
                task_config_list=task_config_list,
                dataset_config_list=dataset_config_list,
            )
            
            # Workflow 执行完后，统一组装返回
            eval_report_path = os.path.join(run_dir, AppSettings.EVALUATION_REPORT_FILENAME)
            workflow_log_path = os.path.join(run_dir, AppSettings.WORKFLOW_LOG_FILENAME)
            
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
                "evaluation_data": report_info["results"] if report_info else None,
            }
            
            print_log(f"Workflow completely done. Emitting [DONE] payload buffer: {json.dumps(final_payload)[:500]}...", prefix="[API Response /api/run]", debug=True)
            await queue.put(f"[DONE] {json.dumps(final_payload)}")
            
        except Exception as e:
            error_payload = {
                "status": "ERROR",
                "message": str(e),
            }
            print_log(f"Workflow error. Emitting ERROR payload: {json.dumps(error_payload)}", prefix="[API Response /api/run]", debug=True)
            await queue.put(f"[DONE] {json.dumps(error_payload)}")
        finally:
            sse_queue_var.reset(token)
            run_dir_var.reset(dir_token)

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
                
            # 捕获结构化事件 [[EVENT]]
            if message.startswith("[[EVENT]] "):
                event_json_str = message[len("[[EVENT]] "):]
                event_data = json.loads(event_json_str)
                
                # 重新包装为 STREAMING 包含事件载荷
                yield f"data: {json.dumps({'status': 'STREAMING', 'event': event_data})}\n\n"
                continue
                
            # SSE 规范：普通日志必须按 data: [内容] \n\n 格式推流
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
        },
    )


@app.get("/api/download/latest-report")
async def download_latest_report():
    """
    获取最新的测试报告文件夹并打包为 zip 格式返回。
    
    业务逻辑委托给了 StorageService 的 get_latest_report_zip 方法。
    """
    try:
        zip_buffer, dir_name = StorageService.get_latest_report_zip()
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="report_{dir_name}.zip"',
        },
    )


if __name__ == "__main__":
    uvicorn.run("medical_llm_workflow.server:app", host="0.0.0.0", port=8000, reload=True)

