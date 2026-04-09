"use client";

import { useState, useRef, useEffect } from "react";

// 定义后端获取的选项类型
type Option = { label: string; value: string };
type OptionsState = {
  datasets: Option[];
  evaluators: Option[];
  chatbotTypes: Option[];
  models: Option[];
  recipes: Option[];
};


export default function Home() {
  // 追踪流程执行情况
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<string>("");
  const [evaluationReport, setEvaluationReport] = useState<string>("");
  const [error, setError] = useState<string>("");

  // 获取和管理可用选项
  const [options, setOptions] = useState<OptionsState | null>(null);

  // 管理表单值
  const [config, setConfig] = useState({
    dataset_type: "med_qa",
    num_of_questions: 4,
    evaluator_types: ["accuracy"],
    chatbot_type: "poe",
    model: "gpt-5.4-nano",
    temperature: 0.7,
    max_tokens: 2048,
    recipe_type: "medical_reasoning_3_steps",
  });

  // 获取可用选项列表
  useEffect(() => {
    fetch("http://localhost:8000/api/options")
      .then((res) => res.json())
      .then((data) => setOptions(data))
      .catch((err) => console.error("Failed to fetch options", err));
  }, []);

  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : type === "checkbox" ? [value] : value,
    }));
  };

  const handleStartWorkflow = async () => {
    setIsRunning(true);
    setLogs("");
    setEvaluationReport("");
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
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
              } else if (payload.status === "ERROR") {
                setError(payload.message);
              }
              break;
            }
            
            // 后端不断吐来的单行控制台日志流
            let parsed;
            try {
              parsed = JSON.parse(dataStr);
            } catch (e) {
              // 非常偶然的截断无法转 JSON，无需生硬抛出打断主线
              continue;
            }
            
            if (parsed.status === "STREAMING" && parsed.log) {
              // 累加字符串呈现终端效果
              setLogs((prev) => prev + parsed.log + "\n");
            }
          }
        }
      }
    } catch (err: any) {
      setError("Workflow failed to connect or execute: " + err.message);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <main className="min-h-screen p-8 bg-gray-50 text-gray-900 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* 顶部控制面板 */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Medical LLM Workflow</h1>
              <p className="text-sm text-gray-500 mt-1">Configure and observe the reasoning pipeline.</p>
            </div>
            <button
              onClick={handleStartWorkflow}
              disabled={isRunning || !options}
              className={`px-6 py-2.5 rounded-lg font-medium transition-all ${
                isRunning || !options
                  ? "bg-gray-300 text-gray-500 cursor-not-allowed" 
                  : "bg-blue-600 text-white hover:bg-blue-700 shadow-sm"
              }`}
            >
              {isRunning ? "Running pipeline..." : "Start Workflow"}
            </button>
          </div>
          
          {/* 动态选项表单 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-gray-700">Dataset</label>
              <select name="dataset_type" value={config.dataset_type} onChange={handleChange} className="border rounded-md p-1.5" disabled={isRunning}>
                {options?.datasets.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-gray-700">Recipe</label>
              <select name="recipe_type" value={config.recipe_type} onChange={handleChange} className="border rounded-md p-1.5" disabled={isRunning}>
                {options?.recipes.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-gray-700">Target Model</label>
              <select name="model" value={config.model} onChange={handleChange} className="border rounded-md p-1.5" disabled={isRunning}>
                {options?.models.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-gray-700">Questions limit (Sample)</label>
              <input 
                name="num_of_questions" type="number" 
                value={config.num_of_questions} 
                onChange={handleChange} 
                min={1} max={10} 
                disabled={isRunning} 
                className="border rounded-md p-1.5"
              />
            </div>
            
            <div className="flex flex-col gap-1">
              <label className="font-semibold text-gray-700">Evaluator</label>
              <select name="evaluator_types" value={config.evaluator_types[0]} onChange={handleChange} className="border rounded-md p-1.5" disabled={isRunning}>
                {options?.evaluators.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* 错误提示框 */}
        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-200">
            <span className="font-semibold">Error: </span>{error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-20">
          
          {/* 左侧：实时终端日志大屏 */}
          <div className="bg-[#1e1e1e] rounded-xl shadow-sm overflow-hidden flex flex-col h-[75vh]">
            <div className="bg-[#2d2d2d] px-4 py-3 flex items-center border-b border-gray-800">
              <div className="flex space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <span className="ml-4 text-xs text-gray-400 font-mono">Backend Terminal Live Stream</span>
            </div>
            
            <div className="flex-1 p-4 overflow-y-auto font-mono text-sm text-gray-300 whitespace-pre-wrap">
              {logs || <span className="text-gray-600 italic">Logs will stream here upon starting...</span>}
              <div ref={logsEndRef} />
            </div>
          </div>

          {/* 右侧：Markdown 格式评估结果 */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden flex flex-col h-[75vh]">
            <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
              <h2 className="text-lg font-bold text-gray-800">Final Evaluation Report</h2>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              {evaluationReport ? (
                <div className="prose prose-sm max-w-none text-gray-700">
                  <pre className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap text-xs shadow-inner">
                    {evaluationReport}
                  </pre>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-400 italic">
                  {isRunning 
                    ? "Evaluating... Awaiting final report payload." 
                    : "No report generated yet."}
                </div>
              )}
            </div>
          </div>
          
        </div>
      </div>
    </main>
  );
}
