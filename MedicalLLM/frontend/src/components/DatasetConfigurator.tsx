import React from "react";
import { Option, DatasetOption, EvaluatorOption, OptionsState, ChatbotConfig } from "../types";

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
    <div className="flex flex-col gap-4 text-sm mt-2">
      <div className="flex items-center justify-between">
        <label className="font-semibold text-gray-700">Datasets</label>
        <button
          type="button"
          onClick={handleAddDataset}
          disabled={disabled}
          className="px-3 py-1 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-md transition-colors disabled:opacity-50 flex items-center gap-1"
        >
          <span className="text-lg leading-none">+</span> Add Dataset
        </button>
      </div>

      <div className="flex flex-wrap gap-4 items-start">
        {configs.map((config, idx) => {
          const currentDsOption = availableDatasets.find(ds => ds.value === config.dataset_type);
          const supportedEvalVals = currentDsOption?.supportedEvaluators || [];
          
          return (
            <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-white flex flex-col gap-3 relative shadow-sm w-full sm:w-[320px] transition-all hover:border-blue-200 hover:shadow">
              <button
                type="button"
                onClick={() => handleRemoveDataset(idx)}
                disabled={disabled}
                className="absolute top-2 right-2 flex items-center justify-center w-6 h-6 rounded-full bg-white border border-gray-200 text-gray-400 hover:text-red-500 hover:border-red-200 disabled:opacity-50"
                title="Remove dataset"
              >
                &#x2715;
              </button>

              <div className="flex flex-col gap-3 pr-6">
                {/* Dataset Type */}
                <div className="flex flex-col gap-1.5">
                  <label className="font-medium text-gray-700 text-xs uppercase tracking-wider">Select Dataset</label>
                  <select
                    value={config.dataset_type}
                    onChange={(e) => updateConfig(idx, { dataset_type: e.target.value })}
                    disabled={disabled}
                    className="border rounded-md p-1.5 w-full bg-gray-50 focus:bg-white"
                  >
                    {availableDatasets.map(ds => (
                      <option key={ds.value} value={ds.value}>{ds.label}</option>
                    ))}
                  </select>
                </div>

                {/* Number of Questions */}
                <div className="flex flex-col gap-1.5">
                  <label className="font-medium text-gray-700 text-xs uppercase tracking-wider">Questions Limit</label>
                  <input
                    type="number"
                    value={config.num_of_questions}
                    onChange={(e) => updateConfig(idx, { num_of_questions: Number(e.target.value) })}
                    min={1}
                    max={50}
                    disabled={disabled}
                    className="border rounded-md p-1.5 w-full bg-gray-50 focus:bg-white"
                  />
                </div>
              </div>

              {/* Evaluators */}
              <div className="flex flex-col gap-2 pt-3 border-t border-gray-100 mt-1">
                <label className="font-medium text-gray-700">Evaluators for {currentDsOption?.label || "this dataset"}</label>
                <div className="flex flex-wrap gap-2">
                  {availableEvaluators.map(ev => {
                    const isSupported = supportedEvalVals.includes(ev.value);
                    const isSelected = config.evaluator_types.includes(ev.value);
                    const isDisabled = disabled || !isSupported;
                    
                    return (
                      <label
                        key={ev.value}
                        title={!isSupported ? "Not supported by this dataset" : ""}
                        className={`flex items-center gap-2 px-3 py-1.5 border rounded-md transition-colors 
                          ${!isSupported ? 'bg-gray-100 border-gray-100 text-gray-400 cursor-not-allowed' : 
                            isSelected ? 'bg-blue-50 border-blue-300 text-blue-700 cursor-pointer' : 
                            'bg-white hover:bg-gray-50 cursor-pointer'}`}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleToggleEvaluator(idx, ev.value)}
                          disabled={isDisabled}
                          className="rounded text-blue-600 focus:ring-blue-500 disabled:opacity-50"
                        />
                        <span>{ev.label}</span>
                      </label>
                    );
                  })}
                </div>
                {supportedEvalVals.length === 0 && (
                  <p className="text-xs text-orange-500 mt-1">Warning: No evaluators supported for this dataset.</p>
                )}

                {/* Per-Evaluator LLM Settings (Only for those requiring LLM and are currently selected) */}
                {availableEvaluators
                  .filter(ev => ev.requiresLLM && config.evaluator_types.includes(ev.value))
                  .map(ev => {
                    const evalConf = config.evaluator_configs?.[ev.value] || { model: "gpt-5.4-nano", temperature: 0.7 };
                    return (
                      <div key={`llmconf-${ev.value}`} className="bg-gray-50 border border-gray-200 mt-2 p-2 rounded flex flex-col gap-2">
                        <span className="text-[10px] uppercase font-bold text-gray-500 tracking-wider">
                          {ev.label} - LLM Settings
                        </span>
                        <div className="flex gap-2">
                          <select
                            disabled={disabled || !options}
                            value={evalConf.model || ""}
                            onChange={(e) => handleUpdateEvaluatorConfig(idx, ev.value, "model", e.target.value)}
                            className="flex-1 text-xs bg-white border border-gray-200 rounded px-2 py-1.5 focus:border-blue-400 focus:outline-none"
                          >
                            <option value="" disabled>Select Model</option>
                            {options?.models?.map((m) => (
                              <option key={m.value} value={m.value}>
                                {m.label}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div className="flex items-center gap-2 mt-1 z-0">
                          <label className="text-[10px] font-bold text-gray-500 w-16">
                            Temp: {evalConf.temperature ?? 0.7}
                          </label>
                          <input
                            type="range"
                            min="0"
                            max="1.0"
                            step="0.1"
                            disabled={disabled}
                            value={evalConf.temperature ?? 0.7}
                            onChange={(e) => handleUpdateEvaluatorConfig(idx, ev.value, "temperature", parseFloat(e.target.value))}
                            className="flex-1 accent-blue-500"
                          />
                        </div>
                      </div>
                    );
                  })
                }
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
    </div>
  );
};