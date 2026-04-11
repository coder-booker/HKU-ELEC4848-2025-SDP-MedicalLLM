"use client";

import { useState, useEffect } from "react";

import { DATASET_CONTEXT_ID } from "../components/PromptEditor";
import { TaskCard } from "../components/TaskCard";

type ChatbotConfig = {
  chatbot_type: string;
  model: string;
  temperature: number;
  max_tokens: number;
};

type PromptTemplate = {
  text: string;
};

type TaskConfig = {
  id: string;
  type: string;
  medical_type: string;
  chatbot_config: ChatbotConfig;
  prompt_template?: PromptTemplate;
  input_msg_sources?: string[];
  max_retries?: number;
  timeout?: number;
  connect_to?: string[];
  evaluator_type_list?: string[];
};

type Option = { label: string; value: string };
// 新增带 tasks 的 Recipe 类型
type RecipeOption = Option & { tasks: TaskConfig[] };
type OptionsState = {
  datasets: Option[];
  evaluators: Option[];
  chatbotTypes: Option[];
  models: Option[];
  recipes: RecipeOption[];
};

// 任务执行状态
type TaskState = {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  content?: string;
};

// 工作流运行阶段
type WorkflowPhase = "idle" | "dataset" | "execution" | "evaluation" | "completed";

// 全局工作流状态
type WorkflowState = {
  phase: WorkflowPhase;
  message: string;
  currentQuestion: number;
  totalQuestions: number;
  tasks: Record<string, TaskState>;
};


export default function Home() {
  // 追踪流程执行情况
  const [isRunning, setIsRunning] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [evaluationReport, setEvaluationReport] = useState<string>("");
  const [error, setError] = useState<string>("");

  // 模块化显示状态管理
  const [workflowState, setWorkflowState] = useState<WorkflowState>({
    phase: "idle",
    message: "",
    currentQuestion: 0,
    totalQuestions: 0,
    tasks: {},
  });

  // 获取和管理可用选项
  const [options, setOptions] = useState<OptionsState | null>(null);

  // 基础运行选项
  const [datasetConfig, setDatasetConfig] = useState({
    dataset_type: "med_qa",
    num_of_questions: 4,
  });
  const [evaluatorType, setEvaluatorType] = useState("accuracy");
  const [globalModel] = useState("gpt-5.4-nano");
  const [globalChatbotType] = useState("poe");
  const [recipeType, setRecipeType] = useState("medical_reasoning_3_steps");

  // 管理任务列表配置，前端自治
  const [tasks, setTasks] = useState<TaskConfig[]>([]);

  // 获取可用选项列表
  useEffect(() => {
    fetch("http://localhost:8000/api/options")
      .then((res) => res.json())
      .then((data) => {
        setOptions(data);
        // 初始化时自动填充默认 Recipe 的配置
        const defaultRecipe = data.recipes?.find((r: RecipeOption) => r.value === "medical_reasoning_3_steps");
        if (defaultRecipe && defaultRecipe.tasks) {
          setTasks(JSON.parse(JSON.stringify(defaultRecipe.tasks)));
        }
      })
      .catch((err) => console.error("Failed to fetch options", err));
  }, []);

    // 选择不同 recipe 时，暂时仅保存 state，等待 apply
    const handleRecipeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      setRecipeType(e.target.value);
    };

    const handleReset = () => {
      setHasRun(false);
      setIsRunning(false);
      setEvaluationReport("");
      setError("");
      setWorkflowState({
        phase: "idle",
        message: "",
        currentQuestion: 0,
        totalQuestions: 0,
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
    setEvaluationReport("");
    setError("");

    // 初始化卡片流状态
    setWorkflowState({
      phase: "idle",
      message: "Starting workflow...",
      currentQuestion: 0,
      totalQuestions: 0,
      tasks: {},
    });

    // 组装给后端的纯配置组合
    const payload = {
      datasets: [datasetConfig],
      evaluator_types: [evaluatorType],
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
                setEvaluationReport(payload.evaluation_report);
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

                if (eventType === "PHASE_START") {
                  newState.phase = eventData.phase;
                  newState.message = eventData.message;
                  if (eventData.total_questions) {
                    newState.totalQuestions = eventData.total_questions;
                  }
                } else if (eventType === "QUESTION_COMPLETED") {
                  newState.currentQuestion = eventData.completed_questions;
                  newState.totalQuestions = eventData.total_questions;
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
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm mt-2">
              <div className="flex flex-col gap-1">
                <label className="font-semibold text-gray-700">Dataset</label>
                <select
                  value={datasetConfig.dataset_type}
                  onChange={e => setDatasetConfig({ ...datasetConfig, dataset_type: e.target.value })}
                  className="border rounded-md p-1.5" disabled={isRunning || hasRun}
                >
                  {options?.datasets.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <label className="font-semibold text-gray-700">Questions (Sample limit)</label>
                <input
                  type="number"
                  value={datasetConfig.num_of_questions}
                  onChange={e => setDatasetConfig({ ...datasetConfig, num_of_questions: Number(e.target.value) })}
                  min={1} max={10}
                  disabled={isRunning || hasRun}
                  className="border rounded-md p-1.5"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="font-semibold text-gray-700">Evaluator</label>
                <select
                  value={evaluatorType}
                  onChange={e => setEvaluatorType(e.target.value)}
                  className="border rounded-md p-1.5" disabled={isRunning}
                >
                  {options?.evaluators.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              </div>

              <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-gray-100 md:col-span-4">
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
          </details>

          {/* 全局状态条，折叠配置后依然可见 */}
          <div className="flex items-center justify-between bg-blue-50 p-3 rounded-lg border border-blue-100">
            <div className="flex items-center gap-4">
              <span className="text-xs font-semibold text-blue-700 uppercase tracking-wider block">Phase:</span>
              <span className="text-sm font-bold text-blue-900">
                {workflowState.phase === 'idle' ? 'Ready to Start' :
                  workflowState.phase === 'dataset' ? 'Processing Dataset' :
                    workflowState.phase === 'execution' ? 'Executing Tasks' :
                      workflowState.phase === 'evaluation' ? 'Evaluating Results' :
                        'Completed'}
              </span>
              <span className="text-sm text-blue-600 block ml-4 border-l border-blue-200 pl-4">{workflowState.message || "Waiting state..."}</span>
            </div>

            {workflowState.totalQuestions > 0 && (
              <div className="flex items-center gap-3">
                <span className="text-xs font-semibold text-blue-700 uppercase tracking-wider">Completed:</span>
                <span className="text-sm font-bold text-blue-900 bg-white px-2 py-0.5 rounded shadow-sm">
                  {workflowState.currentQuestion} / {workflowState.totalQuestions}
                </span>
              </div>
            )}
          </div>
        </div>

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

        {/* 错误提示框 */}
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-200 shadow-sm">
            <span className="font-semibold">Error: </span>{error}
          </div>
        )}

        {/* 最终评估报告折叠面板 */}
        <details className="group bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100" open={!!evaluationReport}>
          <summary className="px-6 py-4 border-b border-gray-100 bg-gray-50 font-bold text-gray-800 cursor-pointer select-none hover:bg-gray-100 transition-colors">
            Final Evaluation Report
          </summary>

          <div className="p-6 overflow-y-auto max-h-[50vh]">
            {evaluationReport ? (
              <div className="prose prose-sm max-w-none text-gray-700">
                <pre className="bg-gray-800 text-gray-100 p-5 rounded-lg whitespace-pre-wrap text-sm shadow-inner font-mono">
                  {evaluationReport}
                </pre>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-8 text-gray-400 italic">
                {isRunning
                  ? "Workflow is executing... Awaiting final report payload."
                  : "No report generated yet."}
              </div>
            )}
          </div>
        </details>

      </div>
    </main>
  );
}
