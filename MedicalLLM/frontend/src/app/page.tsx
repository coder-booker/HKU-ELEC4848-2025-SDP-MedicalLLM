"use client";

import { useState, useEffect } from "react";

import { DatasetConfigPayload } from "../feature/configuration/components/DatasetConfigurator";
import { ConfigurationTab } from "../feature/configuration/ConfigurationTab";
import { DashboardTab } from "../feature/dashboard/DashboardTab";
import { TaskConfig, QuestionStatus, TaskState, OptionsState, RecipeOption } from "../types";
import { ProgressBar } from "../core/ProgressBar";

// ============================================================================
// 文件级注释：这是系统的主页面，负责管理整个医疗大语言模型工作流的生命周期和界面展示。
// 目前使用 Tab 切换设计：Config（配置与任务），Dashboard（左右分屏监控态）
// ============================================================================

type WorkflowPhase = "idle" | "dataset" | "execution" | "evaluation" | "completed";

// 全局工作流状态
type WorkflowState = {
  phase: WorkflowPhase,
  message: string,
  currentQuestion: number,
  totalQuestions: number,
  runId: string,
  questions: QuestionStatus[],
  tasks: Record<string, TaskState>,
};


export default function Home() {
  // 追踪流程执行情况
  const [isRunning, setIsRunning] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [evaluationData, setEvaluationData] = useState<any>(null);
  const [error, setError] = useState<string>("");
  
  // 对于新需求：全局控制当前激活的页面 Tab
  const [activeTab, setActiveTab] = useState<"config" | "running">("config");

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
  const [recipeType, setRecipeType] = useState("");

  // 管理任务列表配置，前端自治
  const [tasks, setTasks] = useState<TaskConfig[]>([]);

  const [extractorConfig, setExtractorConfig] = useState<TaskConfig>({
    id: "smart_extractor",
    type: "smart_extractor",
    chatbot_config: {
      chatbot_type: "poe",
      model: "gpt-5.4-nano",
      temperature: 0.7,
      max_tokens: 5096,
    }
  });

  // 获取可用选项列表
  useEffect(() => {
    fetch("http://localhost:8000/api/options")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setOptions(data);
        // 初始化时不自动填充任何 Recipe
        // const defaultRecipe = data.recipes?.find((r: RecipeOption) => r.value === "two_stage_verification");
        // if (defaultRecipe && defaultRecipe.tasks) {
        //   setTasks(JSON.parse(JSON.stringify(defaultRecipe.tasks)));
        // }
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
      setActiveTab("config");
      setSelectedQuestion(null);
      setQuestionDetail(null);
      setEvaluationData(null);
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
    const tags = ["question_task"]; // Dataset Context ID hardcoded temporarily for decoupled import
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
  const handleTaskChange = (index: number, field: string, value: any) => {
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
      } else if (field === "chatbot_config") {
        task.chatbot_config = value;
      }
      return newTasks;
    });
    setRecipeType("custom");
  };

  const handleExtractorChange = (field: string, value: any) => {
    setExtractorConfig((prev: TaskConfig) => ({
      ...prev,
      [field]: value,
    }));
  };

  // computed property
  const activeEvaluators = Array.from(
    new Set(datasetConfigs.flatMap((dc) => dc.evaluator_types || []))
  );

  const handleStartWorkflow = async () => {
    if (activeEvaluators.length === 0) {
      alert("Please select at least one evaluator before starting the workflow.");
      return;
    }

    setIsRunning(true);
    setHasRun(true);
    setError("");
    setActiveTab("running");

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

    // 动态生成 SmartExtractor 的所需依赖（来源列表+评测器列表）
    const finalExtractorConfig = {
      ...extractorConfig,
      input_msg_sources: ["question_task", ...tasks.map((t) => t.id)],
      evaluator_type_list: activeEvaluators,
    };

    // 组装给后端的纯配置组合
    const payload = {
      datasets: datasetConfigs,
      tasks: activeEvaluators.length > 0 ? [...tasks, finalExtractorConfig] : tasks,
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
                  if (eventData.completed_questions !== undefined) {
                    newState.currentQuestion = eventData.completed_questions;
                  }
                  if (eventData.total_questions !== undefined) {
                    newState.totalQuestions = eventData.total_questions;
                  }
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
        
        // 检查所有任务的 output 是否包含 error 字样，如果有，更新当前题目的视觉状态
        let hasTaskError = false;
        if (data.tasks && Array.isArray(data.tasks)) {
          for (const task of data.tasks) {
            if (task.outputs && Array.isArray(task.outputs)) {
              for (const outMsg of task.outputs) {
                if (outMsg.content && typeof outMsg.content === 'string' && outMsg.content.toLowerCase().includes('error')) {
                  hasTaskError = true;
                  break;
                }
              }
            }
          }
        }
        
        if (hasTaskError && qStatus.status !== "failed") {
          // 如果找到了任务中的错误，我们在前端强制将此题状态也打上 failed，方便 UI 渲染
          setWorkflowState(prev => {
            const newState = { ...prev };
            const q = newState.questions.find(q => q.index === qStatus.index && q.datasetType === qStatus.datasetType);
            if (q) {
              q.status = "failed";
              if (!q.error) q.error = "A task reported an error during execution.";
            }
            return newState;
          });
          data.error = data.error || "A task reported an error during execution.";
        }
        
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

  const handleDownloadLatestReport = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.location.href = "http://localhost:8000/api/download/latest-report";
  };

  const hasFailedQuestion = workflowState.questions.some(q => q.status === "failed");
  const isWorkflowError = !!error;
  const isFailure = hasFailedQuestion || isWorkflowError;

  return (
    <main className="h-screen flex flex-col bg-gray-50 text-gray-900 font-sans overflow-hidden">
      {/* 顶部控制面板及工作流全局状态（固定高度） */}
      <div className="bg-white px-4 pt-4 shadow-sm shrink-0 z-10 flex flex-col gap-3">
        <div className="max-w-7xl mx-auto w-full flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Medical LLM Workflow</h1>
              <p className="text-sm text-gray-500 mt-1">Configure and observe the reasoning pipeline.</p>
            </div>
            {/* 顶栏留空或放一些全局配置信息 */}
          </div>

          {/* 全局状态条，使用单独提取的组件 */}
          <ProgressBar
            isFailure={isFailure}
            phase={workflowState.phase}
            currentQuestion={workflowState.currentQuestion}
            totalQuestions={workflowState.totalQuestions}
            message={workflowState.message}
            isWorkflowError={isWorkflowError}
          />

          {/* 顶层页签切换区 - 类似浏览器Tab放置于下方 */}
          <div className="flex mt-1 -mb-px">
            <button
              onClick={() => setActiveTab("config")}
              className={`px-5 py-2 text-sm font-medium transition-all rounded-t-lg border-t border-l border-r ${
                activeTab === "config" 
                  ? "bg-gray-50 text-blue-600 border-gray-200 border-b-gray-50 -mb-px" 
                  : "bg-white text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              Configuration
            </button>
            <button
              onClick={() => setActiveTab("running")}
              disabled={!isRunning && !hasRun}
              className={`px-5 py-2 text-sm font-medium transition-all rounded-t-lg border-t border-l border-r ml-2 ${
                !isRunning && !hasRun ? "opacity-50 cursor-not-allowed" : ""
              } ${
                activeTab === "running" 
                  ? "bg-gray-50 text-blue-600 border-gray-200 border-b-gray-50 -mb-px" 
                  : "bg-white text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* 主工作区 - 以相对定位支持内部 Tab 控制 */}
      <div className="flex-1 relative overflow-hidden bg-gray-50 border-t border-gray-200">

        {/* Tab 1: Configuration */}
        {activeTab === "config" && (
          <ConfigurationTab
            datasetConfigs={datasetConfigs}
            setDatasetConfigs={setDatasetConfigs}
            options={options}
            isRunning={isRunning}
            hasRun={hasRun}
            recipeType={recipeType}
            handleRecipeChange={handleRecipeChange}
            handleApplyRecipe={handleApplyRecipe}
            tasks={tasks}
            handleAddTask={handleAddTask}
            workflowStateTasks={workflowState.tasks}
            getAvailableTags={getAvailableTags}
            handleTaskChange={handleTaskChange}
            handleRemoveTask={handleRemoveTask}
            handleMoveTask={handleMoveTask}
            activeEvaluators={activeEvaluators}
            extractorConfig={extractorConfig}
            handleExtractorChange={handleExtractorChange}
            handleStartWorkflow={handleStartWorkflow}
            handleReset={handleReset}
          />
        )}

        {/* Tab 2: Dashboard (Running & Eval) */}
        {activeTab === "running" && (
          <DashboardTab
            selectedQuestion={selectedQuestion}
            questions={workflowState.questions}
            handleBackToList={handleBackToList}
            error={error}
            handleViewDetail={handleViewDetail}
            questionDetail={questionDetail}
            hasRun={hasRun}
            handleDownloadLatestReport={handleDownloadLatestReport}
            evaluationData={evaluationData}
          />
        )}

      </div>
    </main>
  );
}
