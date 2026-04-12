"use client";

import { useState, useEffect } from "react";


import { DATASET_CONTEXT_ID } from "../components/PromptEditor";
import { TaskCard } from "../components/TaskCard";
import { QuestionStatusList } from "../components/QuestionStatusList";
import { QuestionDetailView } from "../components/QuestionDetailView";
import { EvaluationDashboard } from "../components/EvaluationDashboard";
import { DatasetConfigurator, DatasetConfigPayload } from "../components/DatasetConfigurator";
import { TaskConfig, QuestionStatus, TaskState, OptionsState, RecipeOption } from "../types";

type WorkflowPhase = "idle" | "dataset" | "execution" | "evaluation" | "completed";

// 全局工作流状态
type WorkflowState = {
  phase: WorkflowPhase;
  message: string;
  currentQuestion: number;
  totalQuestions: number;
  runId: string;
  questions: QuestionStatus[];
  tasks: Record<string, TaskState>;
};


export default function Home() {
  // 追踪流程执行情况
  const [isRunning, setIsRunning] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [evaluationData, setEvaluationData] = useState<any>(null);
  const [error, setError] = useState<string>("");
  
  // 对于新需求：点击列表进入详细弹层
  const [selectedQuestion, setSelectedQuestion] = useState<QuestionStatus | null>(null);
  const [questionDetail, setQuestionDetail] = useState<any>(null); // 保存请求来的结构化日志

  // 模块化显示状态管理
  const [workflowState, setWorkflowState] = useState<WorkflowState>({
    phase: "idle",
    message: "",
    currentQuestion: 0,
    totalQuestions: 0,
    runId: "",
    questions: [],
    tasks: {},
  });

  // 获取和管理可用选项
  const [options, setOptions] = useState<OptionsState | null>(null);

  // 基础运行选项：数组组合
  const [datasetConfigs, setDatasetConfigs] = useState<DatasetConfigPayload[]>([
    {
      dataset_type: "med_qa",
      num_of_questions: 4,
      evaluator_types: ["accuracy"]
    }
  ]);
  
  const [globalModel] = useState("gpt-5.4-nano");
  const [globalChatbotType] = useState("poe");
  const [recipeType, setRecipeType] = useState("medical_reasoning_3_steps");

  // 管理任务列表配置，前端自治
  const [tasks, setTasks] = useState<TaskConfig[]>([]);

  // 获取可用选项列表
  useEffect(() => {
    fetch("http://localhost:8000/api/options")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setOptions(data);
        // 初始化时自动填充默认 Recipe 的配置
        const defaultRecipe = data.recipes?.find((r: RecipeOption) => r.value === "medical_reasoning_3_steps");
        if (defaultRecipe && defaultRecipe.tasks) {
          setTasks(JSON.parse(JSON.stringify(defaultRecipe.tasks)));
        }
        setError(""); // Clear error if fetch is successful
      })
      .catch((err) => {
        console.error("Failed to fetch options", err);
        setError("无法连接到后端服务获取数据项，已加载兜底本地配置(Fallback)。请检查后端服务是否启动。");
        // 兜底配置 Fallback
        setOptions({
          datasets: [{ label: "MedQA (Fallback)", value: "med_qa", supportedEvaluators: ["accuracy"] }],
          evaluators: [{ label: "Accuracy (Fallback)", value: "accuracy" }],
          chatbotTypes: [{ label: "Poe Chatbot", value: "poe" }],
          models: [{ label: "GPT-4", value: "gpt-4" }],
          recipes: [],
        });
      });
  }, []);

    // 选择不同 recipe 时，暂时仅保存 state，等待 apply
    const handleRecipeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      setRecipeType(e.target.value);
    };

    const handleReset = () => {
      setHasRun(false);
      setIsRunning(false);
      setError("");
      setSelectedQuestion(null);
      setQuestionDetail(null);
      setWorkflowState({
        phase: "idle",
        message: "",
        currentQuestion: 0,
        totalQuestions: 0,
        runId: "",
        questions: [],
        tasks: {},
      });
    };

    const handleApplyRecipe = () => {
      const confirmMessage = "Are you sure you want to apply this recipe?\n\nLoading a new recipe will completely OVERWRITE and REPLACE your current task pipeline.";
      if (!window.confirm(confirmMessage)) return;

      if (options && options.recipes) {
        const selected = options.recipes.find(r => r.value === recipeType);
        if (selected && selected.tasks) {
          setTasks(JSON.parse(JSON.stringify(selected.tasks)));
          handleReset();
        }
      }
    };

  // 添加自定义任务，并自动生成不重复的 `untitled task {x}` ID
  const handleAddTask = () => {
    let index = 1;
    let generatedId = `untitled task ${index}`;
    while (tasks.some(t => t.id === generatedId)) {
      index++;
      generatedId = `untitled task ${index}`;
    }

    const newTask = {
      id: generatedId,
      type: "single_agent",
      medical_type: "default",
      chatbot_config: {
        chatbot_type: globalChatbotType,
        model: globalModel,
        temperature: 0.7,
        max_tokens: 2048,
      },
      prompt_template: {
        text: "You are a helpful medical assistant.\n\n",
      },
      input_msg_sources: [],
    };

    setTasks(prev => [...prev, newTask]);
    setRecipeType("custom");
  };

  const getAvailableTags = (currentIdx: number) => {
    const tags = [DATASET_CONTEXT_ID];
    tasks.forEach((t, i) => {
      // 只有在当前任务之前的任务才能作为依赖来源 (不能选用还没跑的任务输出)
      if (i < currentIdx && t.id) {
        tags.push(t.id);
      }
    });
    return tags;
  };

  const handleMoveTask = (index: number, direction: 'up' | 'down') => {
    setTasks(prev => {
      const newTasks = [...prev];
      if (direction === 'up' && index > 0) {
        [newTasks[index - 1], newTasks[index]] = [newTasks[index], newTasks[index - 1]];
      } else if (direction === 'down' && index < newTasks.length - 1) {
        [newTasks[index], newTasks[index + 1]] = [newTasks[index + 1], newTasks[index]];
      }
      return newTasks;
    });
    setRecipeType("custom");
  };

  const handleRemoveTask = (index: number) => {
    const taskToRemove = tasks[index];
    const confirmMessage = `Are you sure you want to remove this task (${taskToRemove.id})?\n\nAny corresponding tags/variables used in other tasks will also be deleted.`;
    
    if (!window.confirm(confirmMessage)) {
      return;
    }

    setTasks(prev => {
      // Remove the task itself
      const newTasks = prev.filter((_, i) => i !== index);
      
      // Clean up references to the removed task's id in remaining tasks
      const removedId = taskToRemove.id;
      if (removedId) {
        newTasks.forEach(task => {
          // 1. Remove from input_msg_sources
          if (task.input_msg_sources) {
            task.input_msg_sources = task.input_msg_sources.filter(sourceId => sourceId !== removedId);
          }
          // 2. Remove {{removedId}} from prompt_template
          if (task.prompt_template && task.prompt_template.text) {
            const regex = new RegExp(`\\{\\{${removedId}\\}\\}`, 'g');
            task.prompt_template.text = task.prompt_template.text.replace(regex, '');
          }
        });
      }
      
      return newTasks;
    });
    setRecipeType("custom");
  };

  // 修改某个具体的任务内的属性
  const handleTaskChange = (index: number, field: string, value: string | string[]) => {
    setTasks(prev => {
      const newTasks = [...prev];
      const task = newTasks[index];
      if (field === "id" && typeof value === "string") {
        task.id = value;
      } else if (field === "prompt" && typeof value === "string") {
        if (!task.prompt_template) {
          task.prompt_template = { text: "" };
        }
        task.prompt_template.text = value;
      } else if (field === "input_msg_sources") {
        // 如果传入的是数组，直接赋值（对应改造成新UI）
        if (Array.isArray(value)) {
          task.input_msg_sources = value;
        } else if (typeof value === "string") {
          // 兼容之前的 string 逗号拼接
          task.input_msg_sources = value.split(',').map((s: string) => s.trim()).filter(Boolean);
        }
      }
      return newTasks;
    });
    setRecipeType("custom");
  };

  const handleStartWorkflow = async () => {
    setIsRunning(true);
    setHasRun(true);
    setError("");

    // 初始化卡片流状态
    setWorkflowState({
      phase: "idle",
      message: "Starting workflow...",
      currentQuestion: 0,
      totalQuestions: 0,
      runId: "",
      questions: [],
      tasks: {},
    });
    setSelectedQuestion(null);
    setQuestionDetail(null);

    // 组装给后端的纯配置组合
    const payload = {
      datasets: datasetConfigs,
      tasks: tasks,
    };

    try {
      const response = await fetch("http://localhost:8000/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.body) {
        throw new Error("No response body returned from backend.");
      }

      // 利用原生 API 逐端读取 SSE (Server-Sent Events) 流式数据
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let buffer = "";

      // 不断截流并解析
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, {
          stream: true,
        });

        // SSE 规定的格式是由连续两个换行符作为数据块分隔
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || ""; // 最后一个部分可能还不完整，塞回 buffer 里继续等

        for (const part of parts) {
          if (part.startsWith("data: ")) {
            const dataStr = part.replace("data: ", "").trim();

            // 后端执行闭环传来的最终结果块
            if (dataStr.startsWith("[DONE]")) {
              const payloadStr = dataStr.replace("[DONE] ", "").trim();
              const payload = JSON.parse(payloadStr);

              if (payload.status === "DONE") {
                setEvaluationData(payload.evaluation_data);
                setWorkflowState((prev) => ({
                  ...prev,
                  phase: "completed",
                  message: "Workflow finished successfully.",
                }));
                setHasRun(true);
              } else if (payload.status === "ERROR") {
                setError(payload.message);
                setWorkflowState((prev) => ({
                  ...prev,
                  phase: "completed",
                  message: "Workflow failed.",
                }));
                setHasRun(true);
              }
              break;
            }

            let parsed;
            try {
              parsed = JSON.parse(dataStr);
            } catch {
              // 非常偶然的截断无法转 JSON，等待下一个部分合并，不粗暴中断流
              continue;
            }

            // 解析由后端 utils.emit_event 发出的结构化事件
            if (parsed.status === "STREAMING" && parsed.event) {
              const eventType = parsed.event.type;
              const eventData = parsed.event.data;

              setWorkflowState((prev) => {
                const newState = { ...prev };

                if (eventType === "WORKFLOW_STARTED") {
                  newState.runId = eventData.run_id;
                } else if (eventType === "PHASE_START") {
                  newState.phase = eventData.phase;
                  newState.message = eventData.message;
                  if (eventData.total_questions) {
                    newState.totalQuestions = eventData.total_questions;
                  }
                } else if (eventType === "QUESTION_STARTED") {
                  // 这里可以用来构建或更新某个问题处于执行中的状态
                  const qIdx = eventData.question_index;
                  const dType = eventData.dataset_type;
                  
                  // 初始化新题目的状态，或更新状态为 running
                  const existingQuestion = newState.questions.find(q => q.index === qIdx && q.datasetType === dType);
                  if (existingQuestion) {
                    existingQuestion.status = "running";
                  } else {
                    newState.questions.push({
                      index: qIdx,
                      datasetType: dType,
                      status: "running"
                    });
                  }
                } else if (eventType === "QUESTION_COMPLETED") {
                  newState.currentQuestion = eventData.completed_questions;
                  newState.totalQuestions = eventData.total_questions;
                  
                  const qIdx = eventData.question_index;
                  const dType = eventData.dataset_type;
                  
                  // 将完成的题目标记为 completed
                  const existingQuestion = newState.questions.find(q => q.index === qIdx && q.datasetType === dType);
                  if (existingQuestion) {
                    existingQuestion.status = "completed";
                  } else {
                    // 以防万一 STARTED 没有生效
                    newState.questions.push({
                      index: qIdx,
                      datasetType: dType,
                      status: "completed"
                    });
                  }
                } else if (eventType === "QUESTION_FAILED") {
                  const qIdx = eventData.question_index;
                  const dType = eventData.dataset_type;
                    const errorMsg = eventData.error || "Unknown Error";
                    
                    const existingQuestion = newState.questions.find(q => q.index === qIdx && q.datasetType === dType);
                    if (existingQuestion) {
                      existingQuestion.status = "failed";
                      existingQuestion.error = errorMsg;
                    } else {
                      newState.questions.push({
                        index: qIdx,
                        datasetType: dType,
                        status: "failed",
                        error: errorMsg
                      });
                    }
                  }

                return newState;
              });
            }
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError("Workflow failed to connect or execute: " + err.message);
      } else {
        setError("Workflow failed to connect or execute: unknown error");
      }
    } finally {
      setIsRunning(false);
    }
  };

  const handleViewDetail = async (qStatus: QuestionStatus) => {
    setSelectedQuestion(qStatus);
    setQuestionDetail(null); // Clear previous detail first
    try {
      const response = await fetch(`http://localhost:8000/api/results/${workflowState.runId}/${qStatus.datasetType}/${qStatus.index}`);
      if (response.ok) {
        const data = await response.json();
        setQuestionDetail(data);
      } else {
        console.error("Failed to fetch question detail.");
        setQuestionDetail({ error: qStatus.error || "Failed to load details. The backend might have crashed before saving." });
      }
    } catch (err) {
      console.error("Error fetching detail:", err);
      setQuestionDetail({ error: qStatus.error || "Network error fetching details." });
    }
  };

  const handleBackToList = () => {
    setSelectedQuestion(null);
  };

  const hasFailedQuestion = workflowState.questions.some(q => q.status === "failed");
  const isWorkflowError = !!error;
  const isFailure = hasFailedQuestion || isWorkflowError;

  return (
    <main className="min-h-screen p-4 bg-gray-50 text-gray-900 font-sans">
      <div className="max-w-7xl mx-auto flex flex-col gap-4">

        {/* 顶部控制面板及工作流全局状态 */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Medical LLM Workflow</h1>
              <p className="text-sm text-gray-500 mt-1">Configure and observe the reasoning pipeline.</p>
            </div>
            <div className="flex gap-2">
              {hasRun && (
                <button
                  onClick={handleReset}
                  className="px-6 py-2 rounded-lg font-medium transition-all bg-gray-50 text-red-600 border border-red-200 hover:bg-red-50 hover:border-red-300 shadow-sm"
                >
                  Reset Pipeline
                </button>
              )}
              <button
                onClick={handleStartWorkflow}
                disabled={isRunning || !options || hasRun}
                className={`px-6 py-2 rounded-lg font-medium transition-all ${isRunning || !options || hasRun
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-blue-600 text-white hover:bg-blue-700 shadow-sm"
                  }`}
              >
                {isRunning ? "Running pipeline..." : "Start Workflow"}
              </button>
            </div>
          </div>

          <details className="group mb-4" open={!isRunning && !hasRun}>
            <summary className="text-sm font-bold text-gray-700 cursor-pointer select-none pb-2 border-b border-gray-100 mb-4 hover:text-blue-600 transition-colors">
              Configuration Options
            </summary>
            
            {/* Disabled UI Wrapper */}
            <div className={`relative transition-all duration-300 ${isRunning || hasRun ? 'opacity-40 grayscale pointer-events-none' : ''}`}>
              
              {/* Invisible overlay capturing pointer events to show cursor and tooltip */}
              {(isRunning || hasRun) && (
                <div 
                  className="absolute inset-0 z-10 pointer-events-auto cursor-not-allowed" 
                  title="运行已开始或已完成，请重置 Workflow 才能修改配置"
                />
              )}

              <div className="flex flex-col gap-6 text-sm mt-2">
                <DatasetConfigurator 
                  configs={datasetConfigs}
                  onChange={setDatasetConfigs}
                  availableDatasets={options?.datasets || []}
                  availableEvaluators={options?.evaluators || []}
                  disabled={isRunning || hasRun}
                />

                {/* Recipe Strategy */}
                <div className="flex flex-col gap-2 mt-2 pt-4 border-t border-gray-100">
                  <label className="font-semibold text-gray-700">Load Recipe Strategy</label>
                  <div className="flex items-center gap-3">
                    <select
                      value={recipeType}
                      onChange={handleRecipeChange}
                      className="border rounded-md p-1.5 flex-1 max-w-sm"
                      disabled={isRunning || hasRun}
                    >
                      <option value="custom" disabled hidden>-- Custom Pipeline (Unsaved) --</option>
                      {options?.recipes.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                    <button
                      onClick={handleApplyRecipe}
                      disabled={isRunning || hasRun || recipeType === "custom"}
                      className="px-4 py-1.5 bg-indigo-600 text-white rounded hover:bg-indigo-700 font-medium transition-colors disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed shadow-sm"
                    >
                      Apply & Overwrite Tasks
                    </button>
                  </div>
                  <p className="text-xs text-gray-500">Applying a recipe will completely replace your current tasks setup.</p>
                </div>
              </div>
            </div>
          </details>

          {/* 全局状态条，折叠配置后依然可见 */}
          <div className={`relative overflow-hidden flex items-center justify-between p-3 rounded-lg border transition-colors ${
            isFailure ? 'border-red-500 bg-red-500' :
            workflowState.phase === 'completed' ? 'border-green-500 bg-green-500' : 'border-blue-100 bg-blue-50'
          }`}>
            {/* 进度条层 */}
            <div 
              className={`absolute left-0 top-0 bottom-0 transition-all duration-500 ease-out ${
                isFailure 
                ? 'bg-red-500' 
                : workflowState.phase === 'completed' 
                  ? 'bg-green-500'
                  : 'bg-green-300 opacity-60'
              }`}
              style={{ 
                width: isFailure && workflowState.phase !== 'completed'
                  ? '100%' 
                  : workflowState.phase === 'completed' || workflowState.phase === 'evaluation' 
                    ? '100%' 
                    : `${workflowState.totalQuestions > 0 ? (workflowState.currentQuestion / workflowState.totalQuestions) * 100 : 0}%`
              }}
            />

            <div className="relative z-10 flex items-center gap-4">
              <span className={`text-xs font-semibold uppercase tracking-wider block ${
                isFailure ? 'text-red-100' :
                workflowState.phase === 'completed' ? 'text-green-100' : 'text-blue-700'
              }`}>Phase:</span>
              <span className={`text-sm font-bold ${
                isFailure || workflowState.phase === 'completed' ? 'text-white' : 'text-blue-900'
              }`}>
                {isWorkflowError ? 'Workflow Stopped on Error' :
                workflowState.phase === 'idle' ? 'Ready to Start' :
                  workflowState.phase === 'dataset' ? 'Processing Dataset' :
                    workflowState.phase === 'execution' ? 'Executing Tasks' :
                      workflowState.phase === 'evaluation' ? 'Evaluating Results' :
                        (hasFailedQuestion ? 'Completed with Errors' : 'Successfully Completed')}
              </span>
              <span className={`text-sm block ml-4 border-l pl-4 ${
                isFailure ? 'text-red-100 border-red-400' :
                workflowState.phase === 'completed' ? 'text-green-100 border-green-300' : 'text-blue-600 border-blue-200'
              }`}>{workflowState.message || "Waiting state..."}</span>
            </div>

            {workflowState.totalQuestions > 0 && (
              <div className="relative z-10 flex items-center gap-3">
                <span className={`text-xs font-semibold uppercase tracking-wider ${
                  isFailure ? 'text-red-100' :
                  workflowState.phase === 'completed' ? 'text-green-100' : 'text-blue-700'
                }`}>Completed:</span>
                <span className={`text-sm font-bold bg-white px-2 py-0.5 rounded shadow-sm ${
                  isFailure ? 'text-red-700' :
                  workflowState.phase === 'completed' ? 'text-green-600' : 'text-blue-900'
                }`}>
                  {workflowState.currentQuestion} / {workflowState.totalQuestions}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Question Execution Status Section (Only visible when workflow has run/is running) */}
        {(hasRun || isRunning) && (
          <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-gray-800">
                {selectedQuestion ? `Question Detail: ${selectedQuestion.datasetType} #${selectedQuestion.index}` : "Execution Progress (Per Question)"}
              </h2>
              {selectedQuestion && (
                <button
                  onClick={handleBackToList}
                  className="px-3 py-1.5 rounded-md text-sm font-medium bg-gray-100 hover:bg-gray-200 text-gray-800 transition"
                >
                  ← Back to List
                </button>
              )}
            </div>

            {/* 全局顶部错误提示框 */}
            {error && !selectedQuestion && (
              <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200 shadow-sm">
                <h3 className="font-bold mb-1 flex items-center gap-2">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  Workflow Error
                </h3>
                <p className="text-sm font-mono whitespace-pre-wrap ml-7">{error}</p>
              </div>
            )}

            {!selectedQuestion ? (
              <QuestionStatusList
                questions={workflowState.questions}
                onViewDetail={handleViewDetail}
              />
            ) : (
              <QuestionDetailView questionDetail={questionDetail} />
            )}
          </div>
        )}

        {/* 工作流任务与结果组合区域 */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-800">Tasks Pipeline & Details</h2>
            <button
              onClick={handleAddTask}
              disabled={isRunning || hasRun}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${isRunning || hasRun ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-gray-100 hover:bg-gray-200 text-gray-800'}`}
            >
              + Add Task
            </button>
          </div>

          {tasks.length === 0 && (
            <div className="text-gray-400 text-sm italic py-2">No tasks defined. Load a recipe or add a custom task.</div>
          )}

          <div className="flex flex-row gap-5 overflow-x-auto pb-4 snap-x snap-mandatory">
            {tasks.map((task, idx) => (
              <TaskCard
                key={`${task.id}-${idx}`}
                task={task}
                taskState={workflowState.tasks[task.id]}
                idx={idx}
                isRunning={isRunning || hasRun}
                availableTags={getAvailableTags(idx)}
                onTaskChange={handleTaskChange}
                  onRemove={() => handleRemoveTask(idx)}
                onMoveUp={() => handleMoveTask(idx, 'up')}
                onMoveDown={() => handleMoveTask(idx, 'down')}
                isFirst={idx === 0}
                isLast={idx === tasks.length - 1}
              />
            ))}
          </div>
        </div>

        {/* 最终评估报告折叠面板 */}
        {(hasRun || isRunning) && (
          <details className="group bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100" open={evaluationData && evaluationData.length > 0}>
            <summary className="px-6 py-4 border-b border-gray-100 bg-gray-50 font-bold text-gray-800 cursor-pointer select-none hover:bg-gray-100 transition-colors">
              Final Evaluation Report
            </summary>

            <div className="p-6 overflow-y-auto max-h-[70vh]">
              <EvaluationDashboard evaluationData={evaluationData} />
            </div>
          </details>
        )}

      </div>
    </main>
  );
}
