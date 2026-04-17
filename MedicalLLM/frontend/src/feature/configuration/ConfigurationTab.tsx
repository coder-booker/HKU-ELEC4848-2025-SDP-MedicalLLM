"use client";

import React from "react";
import { DatasetConfigurator, DatasetConfigPayload } from "./components/DatasetConfigurator";
import { TaskCard } from "./components/TaskCard";
import { SmartExtractorCard } from "./components/SmartExtractorCard";
import { OptionsState, TaskConfig, TaskState } from "@/types";


// ============================================================================
// 文件级注释：本组件负责工作流的配置与任务组装（Configuration Tab）。
// 它包裹了数据集配置、Recipe 套用策略，以及任务流（Pipeline）的定制 UI。
// ============================================================================

export interface ConfigurationTabProps {
  datasetConfigs: DatasetConfigPayload[],
  setDatasetConfigs: React.Dispatch<React.SetStateAction<DatasetConfigPayload[]>>,
  options: OptionsState | null,
  isRunning: boolean,
  hasRun: boolean,
  recipeType: string,
  handleRecipeChange: (e: React.ChangeEvent<HTMLSelectElement>) => void,
  handleApplyRecipe: () => void,
  tasks: TaskConfig[],
  handleAddTask: () => void,
  workflowStateTasks: Record<string, TaskState>,
  getAvailableTags: (idx: number) => string[],
  handleTaskChange: (index: number, field: string, value: any) => void,
  handleRemoveTask: (index: number) => void,
  handleMoveTask: (index: number, direction: 'up' | 'down') => void,
  activeEvaluators: string[],
  extractorConfig: TaskConfig,
  handleExtractorChange: (field: string, value: any) => void,
  handleStartWorkflow: () => void,
  handleReset: () => void,
}

// ============================================================================
// 函数级注释：ConfigurationTab 组件
// 渲染系统配置区块（包括数据集选择和 Recipe 加载），以及 Pipeline 设定。
// ============================================================================
export function ConfigurationTab(props: ConfigurationTabProps) {
  if (!props) {
    return <div className="p-4 text-red-500">属性参数为空错误</div>;
  }

  const {
    datasetConfigs,
    setDatasetConfigs,
    options,
    isRunning,
    hasRun,
    recipeType,
    handleRecipeChange,
    handleApplyRecipe,
    tasks,
    handleAddTask,
    workflowStateTasks,
    getAvailableTags,
    handleTaskChange,
    handleRemoveTask,
    handleMoveTask,
    activeEvaluators,
    extractorConfig,
    handleExtractorChange,
    handleStartWorkflow,
    handleReset,
  } = props;

  return (
    <div className="absolute inset-0 overflow-y-auto p-4 flex flex-col gap-4 max-w-7xl mx-auto pb-10 w-full">
      {/* 顶部配置区块 */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 shrink-0">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-800">Configuration Options</h2>
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
        
        <div className={`relative transition-all duration-300 ${isRunning || hasRun ? 'opacity-40 grayscale pointer-events-none' : ''}`}>
          {(isRunning || hasRun) && (
            <div 
              className="absolute inset-0 z-10 pointer-events-auto cursor-not-allowed" 
              title="The process has already started or completed. Please reset the Pipline before you can modify the configuration."
            />
          )}
          <div className="flex flex-row gap-6 text-sm mt-2">
            
            {/* 左侧：数据集配置 */}
            <div className="flex-1">
              <DatasetConfigurator 
                configs={datasetConfigs}
                onChange={setDatasetConfigs}
                availableDatasets={options?.datasets || []}
                availableEvaluators={options?.evaluators || []}
                options={options}
                disabled={isRunning || hasRun}
              />
            </div>

            {/* 右侧边栏：Recipe Strategy */}
            <div className="border-l border-gray-100 pl-6 w-96 flex flex-col gap-2">
              <label className="font-semibold text-gray-700">Load Recipe Strategy</label>
              <div className="flex flex-col gap-3">
                <select
                  value={recipeType || ""}
                  onChange={handleRecipeChange}
                  className="border rounded-md p-1.5 w-full text-gray-700"
                  disabled={isRunning || hasRun}
                >
                  <option value="" disabled hidden>-- Please select a recipe --</option>
                  <option value="custom" disabled hidden>-- Custom Pipeline (Unsaved) --</option>
                  {options?.recipes.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
                <button
                  onClick={handleApplyRecipe}
                  disabled={isRunning || hasRun || recipeType === "custom"}
                  className="px-4 py-1.5 bg-indigo-600 text-white rounded hover:bg-indigo-700 font-medium transition-colors disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed shadow-sm w-full"
                >
                  Apply & Overwrite Tasks
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2">Applying a recipe will completely replace your current tasks setup.</p>
            </div>
          </div>
        </div>
      </div>

      {/* 底部任务列表区块 */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex flex-col">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-100 shrink-0">
          <h2 className="text-lg font-bold text-gray-800">Tasks Pipeline & Details</h2>
          <button
            onClick={handleAddTask}
            disabled={isRunning || hasRun}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${isRunning || hasRun ? 'bg-gray-200 text-gray-400 cursor-not-allowed' : 'bg-gray-100 hover:bg-gray-200 text-gray-800'}`}
          >
            + Add Task
          </button>
        </div>

        <div className={`relative transition-all duration-300 ${isRunning || hasRun ? 'opacity-40 grayscale pointer-events-none' : ''}`}>
          {(isRunning || hasRun) && (
            <div 
              className="absolute inset-0 z-10 pointer-events-auto cursor-not-allowed" 
              title="The process has already started or completed. Please reset the Pipeline before you can modify tasks."
            />
          )}

          {tasks.length === 0 && (
            <div className="text-gray-400 text-sm italic py-2">No tasks defined. Load a recipe or add a custom task.</div>
          )}

          <div className="flex flex-row gap-5 overflow-x-auto pb-4 snap-x snap-mandatory items-stretch">
          {tasks.map((task, idx) => (
            <TaskCard
              key={`${task.id}-${idx}`}
              task={task}
              taskState={workflowStateTasks[task.id]}
              idx={idx}
              isRunning={isRunning || hasRun}
              availableTags={getAvailableTags(idx)}
              options={options}
              onTaskChange={handleTaskChange}
              onRemove={() => handleRemoveTask(idx)}
              onMoveUp={() => handleMoveTask(idx, 'up')}
              onMoveDown={() => handleMoveTask(idx, 'down')}
              isFirst={idx === 0}
              isLast={idx === tasks.length - 1}
            />
          ))}
          
          {activeEvaluators.length > 0 && (
            <SmartExtractorCard
              config={extractorConfig}
              isRunning={isRunning || hasRun}
              options={options}
              evaluatorsEnablingExtraction={activeEvaluators}
              onChange={handleExtractorChange}
            />
          )}
          </div>
        </div>
      </div>
    </div>
  );
}
