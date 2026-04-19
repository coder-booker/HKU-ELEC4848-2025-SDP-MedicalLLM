import React, { useState } from "react";
import { Option, DatasetOption, EvaluatorOption, OptionsState, ChatbotConfig } from "@/types";

export type DatasetConfigPayload = {
  dataset_type: string;
  num_of_questions: number;
  evaluator_types: string[];
  evaluator_configs?: Record<string, Partial<ChatbotConfig>>;
};

type DatasetConfiguratorProps = {
  configs: DatasetConfigPayload[];
  onChange: (configs: DatasetConfigPayload[]) => void;
  availableDatasets: DatasetOption[];
  availableEvaluators: EvaluatorOption[];
  options: OptionsState | null;
  disabled: boolean;
};

export const DatasetConfigurator: React.FC<DatasetConfiguratorProps> = ({
  configs,
  onChange,
  availableDatasets,
  availableEvaluators,
  options,
  disabled,
}) => {
  const [activeEvalModal, setActiveEvalModal] = useState<{idx: number, evalVal: string} | null>(null);

  const handleAddDataset = () => {
    if (disabled || availableDatasets.length === 0) return;
    // Pick the first available dataset not already in the list if possible
    const unusedDatasets = availableDatasets.filter(ds => !configs.some(c => c.dataset_type === ds.value));
    const dsToAdd = unusedDatasets.length > 0 ? unusedDatasets[0] : availableDatasets[0];
    const newConfig: DatasetConfigPayload = {
      dataset_type: dsToAdd.value,
      num_of_questions: 4,
      evaluator_types: dsToAdd.supportedEvaluators ? [...dsToAdd.supportedEvaluators] : [],
      evaluator_configs: {},
    };
    onChange([...configs, newConfig]);
  };

  const handleRemoveDataset = (index: number) => {
    if (disabled) return;
    const newConfigs = [...configs];
    newConfigs.splice(index, 1);
    onChange(newConfigs);
  };

  const updateConfig = (index: number, updates: Partial<DatasetConfigPayload>) => {
    if (disabled) return;
    const newConfigs = [...configs];
    
    // If dataset type changes, ensure the evaluator types are still supported
    if (updates.dataset_type && updates.dataset_type !== newConfigs[index].dataset_type) {
      const dsOption = availableDatasets.find(ds => ds.value === updates.dataset_type);
      if (dsOption && dsOption.supportedEvaluators) {
        // Filter out evaluators not supported by the new dataset
         updates.evaluator_types = newConfigs[index].evaluator_types.filter(e => 
           dsOption.supportedEvaluators.includes(e)
         );
      }
    }
    
    newConfigs[index] = { ...newConfigs[index], ...updates };
    onChange(newConfigs);
  };

  const handleToggleEvaluator = (index: number, eVal: string) => {
    if (disabled) return;
    const currentEvaluators = configs[index].evaluator_types;
    if (currentEvaluators.includes(eVal)) {
      updateConfig(index, { evaluator_types: currentEvaluators.filter(v => v !== eVal) });
    } else {
      updateConfig(index, { evaluator_types: [...currentEvaluators, eVal] });
    }
  };

  const handleUpdateEvaluatorConfig = (index: number, evalType: string, field: string, value: any) => {
    if (disabled) return;
    const newConfigs = [...configs];
    const prevConf = newConfigs[index].evaluator_configs || {};
    const evalConf = prevConf[evalType] || { temperature: 0.7, model: "gpt-5.4-nano", chatbot_type: "poe" };
    
    newConfigs[index] = {
      ...newConfigs[index],
      evaluator_configs: {
        ...prevConf,
        [evalType]: {
          ...evalConf,
          [field]: value
        }
      }
    };
    onChange(newConfigs);
  };

  return (
    <div className="flex flex-col gap-3 text-sm mt-2">
      <div className="flex items-center justify-between">
        <label className="font-semibold text-gray-700">Datasets</label>
        <button
          type="button"
          onClick={handleAddDataset}
          disabled={disabled}
          className="px-3 py-1 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-md transition-colors disabled:opacity-50 flex items-center gap-1 shadow-sm"
        >
          <span className="text-lg leading-none">+</span> Add Dataset
        </button>
      </div>

      <div className="flex flex-col gap-4 items-start max-h-[400px] overflow-y-auto w-full pr-2">
        {configs.map((config, idx) => {
          const currentDsOption = availableDatasets.find(ds => ds.value === config.dataset_type);
          const supportedEvalVals = currentDsOption?.supportedEvaluators || [];
          
          return (
            <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-white flex flex-row gap-6 relative shadow-[0_1px_3px_rgb(0,0,0,0.05)] w-full transition-all hover:border-blue-200 hover:shadow-md items-start">
              {/* 删除按钮 */}
              {configs.length > 1 && !disabled && (
                <button
                  onClick={() => handleRemoveDataset(idx)}
                  className="absolute top-2 right-2 text-gray-400 hover:text-red-500 font-bold p-1 leading-none rounded hover:bg-red-50 transition-colors z-10"
                  title="Remove this dataset config"
                >
                  ✕
                </button>
              )}

              <div className="flex flex-col gap-3 w-1/3">
                {/* Dataset Type */}
                <div className="flex items-center justify-between gap-3">
                  <label className="font-medium text-gray-500 text-[11px] uppercase tracking-wider w-20 shrink-0">Dataset</label>
                  <select
                    value={config.dataset_type}
                    onChange={(e) => updateConfig(idx, { dataset_type: e.target.value })}
                    disabled={disabled}
                    className="border rounded-md p-1.5 w-full bg-gray-50 focus:bg-white focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
                  >
                    {availableDatasets.map(ds => (
                      <option key={ds.value} value={ds.value}>{ds.label}</option>
                    ))}
                  </select>
                </div>

                {/* Number of Questions */}
                <div className="flex flex-col gap-1 w-full">
                  <div className="flex items-center justify-between gap-3">
                    <label className="font-medium text-gray-500 text-[11px] uppercase tracking-wider w-20 shrink-0">Limit (#)</label>
                    <input
                      type="number"
                      value={config.num_of_questions}
                      onChange={(e) => updateConfig(idx, { num_of_questions: Math.max(1, Math.min(50, Number(e.target.value))) })}
                      min={1}
                      max={50}
                      disabled={disabled}
                      className="border rounded-md p-1.5 w-full bg-gray-50 focus:bg-white focus:ring-1 focus:ring-blue-500 outline-none transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Evaluators */}
              <div className="flex flex-col gap-2 w-2/3 border-l border-gray-100 pl-6 pr-4">
                <label className="font-medium text-balck-500 text-[15px] uppercase tracking-wider">Active Evaluators</label>
                <div className="flex flex-wrap gap-2">
                  {availableEvaluators.map(ev => {
                    const isSupported = supportedEvalVals.includes(ev.value);
                    const isSelected = config.evaluator_types.includes(ev.value);
                    const isDisabled = disabled || !isSupported;
                    
                    return (
                      <div key={ev.value} className={`flex items-center border rounded-md transition-colors text-xs select-none
                        ${!isSupported ? 'bg-gray-50 border-gray-100 text-gray-400 cursor-not-allowed' : 
                          isSelected ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm font-medium' : 
                          'bg-white hover:border-blue-300 cursor-pointer'}`}>
                        <label
                          title={!isSupported ? "Not supported by this dataset" : ""}
                          className={`flex items-center gap-1.5 px-2.5 py-1 ${!isSupported ? 'cursor-not-allowed' : 'cursor-pointer'} grow`}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => handleToggleEvaluator(idx, ev.value)}
                            disabled={isDisabled}
                            className="rounded text-blue-600 focus:ring-blue-500 disabled:opacity-50 accent-blue-600 pointer-events-none"
                          />
                          <span className={!isSupported ? "line-through text-gray-400" : ""}>{ev.label}</span>
                        </label>
                        
                        {/* ⚙️ 评测器LLM设置按钮 */}
                        {ev.requiresLLM && isSelected && (
                          <button
                            type="button"
                            onClick={() => setActiveEvalModal({ idx, evalVal: ev.value })}
                            className="px-2 py-1 text-blue-500 hover:text-blue-800 hover:bg-blue-100 border-l border-blue-200 focus:outline-none transition-colors"
                            title="Configure Evaluator LLM Provider"
                          >
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
                {supportedEvalVals.length === 0 && (
                  <p className="text-[10px] text-orange-500 mt-1">Warning: No evaluators supported for this dataset.</p>
                )}
              </div>
            </div>
          );
        })}
        {configs.length === 0 && (
          <div className="text-center p-8 text-gray-400 border border-dashed rounded-lg">
            No datasets configured. Click "Add Dataset" to start evaluating.
          </div>
        )}
      </div>

      {/* Evaluator LLM Settings Modal */}
      {activeEvalModal !== null && (() => {
        const { idx, evalVal } = activeEvalModal;
        if (idx >= configs.length) return null;
        const config = configs[idx];
        const ev = availableEvaluators.find(e => e.value === evalVal);
        if (!ev) return null;
        
        const evalConf = config.evaluator_configs?.[ev.value] || { model: "gpt-5.4-nano", temperature: 0.7 };

        return (
          <>
            <div 
              className="fixed inset-0 z-[90] bg-black/5"
              onClick={(e) => { e.stopPropagation(); setActiveEvalModal(null); }}
            />
            <div 
              className="fixed z-[100] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] max-w-[90vw] bg-white border border-gray-200 shadow-xl rounded-xl p-5 flex flex-col gap-4 animate-[fadeIn_0.1s_ease-out]"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-1">
                <h3 className="text-base font-bold text-gray-800">{ev.label} Settings</h3>
                <button 
                  onClick={() => setActiveEvalModal(null)}
                  className="text-gray-400 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 rounded p-1.5 transition-colors focus:outline-none"
                >
                  ✕
                </button>
              </div>
              
              <div className="flex flex-col gap-4">
                <div className="flex flex-col gap-3 p-4 bg-gray-50 rounded-lg border border-gray-100 text-sm">
                  <span className="text-xs uppercase font-bold text-gray-500 tracking-wider border-b border-gray-200 pb-2 mb-1">
                    LLM Configuration
                  </span>
                  
                  <div className="flex flex-col gap-2 text-gray-700">
                    <label className="font-semibold text-xs text-gray-600 block">Model</label>
                    <select
                      disabled={disabled || !options}
                      value={evalConf.model || ""}
                      onChange={(e) => handleUpdateEvaluatorConfig(idx, ev.value, "model", e.target.value)}
                      className="bg-white border border-gray-300 rounded px-2 py-1.5 focus:border-blue-400 focus:outline-none w-full"
                    >
                      <option value="" disabled>Select Model</option>
                      {options?.models?.map((m) => (
                        <option key={m.value} value={m.value}>
                          {m.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="flex items-center justify-between gap-3 mt-2 text-gray-700">
                    <label className="font-semibold text-xs text-gray-600 w-16 shrink-0">
                      Temp: <span className="bg-white border rounded px-1">{evalConf.temperature ?? 0.7}</span>
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1.0"
                      step="0.1"
                      disabled={disabled}
                      value={evalConf.temperature ?? 0.7}
                      onChange={(e) => handleUpdateEvaluatorConfig(idx, ev.value, "temperature", parseFloat(e.target.value))}
                      className="flex-1 accent-blue-500 w-full"
                    />
                  </div>
                </div>
              </div>
            </div>
          </>
        );
      })()}
    </div>
  );
};