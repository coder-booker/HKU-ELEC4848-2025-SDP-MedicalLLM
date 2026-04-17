import { useState, MouseEvent } from "react";
import { TaskConfig, OptionsState } from "@/types";

type SmartExtractorCardProps = {
  config: TaskConfig;
  isRunning: boolean;
  options: OptionsState | null;
  evaluatorsEnablingExtraction: string[];
  onChange: (field: string, value: any) => void;
};

export function SmartExtractorCard({
  config,
  isRunning,
  options,
  evaluatorsEnablingExtraction,
  onChange,
}: SmartExtractorCardProps) {
  const [configOpen, setConfigOpen] = useState(false);

  const handleOpenConfig = (e: MouseEvent<HTMLDivElement>) => {
    if ((e.target as HTMLElement).tagName === 'BUTTON' || (e.target as HTMLElement).tagName === 'SELECT' || (e.target as HTMLElement).tagName === 'INPUT') {
      return;
    }
    setConfigOpen(true);
  };

  return (
    <>
    <div
      onClick={handleOpenConfig}
      className={`relative border rounded-xl p-5 flex flex-col gap-4 transition-colors shrink-0 snap-center w-[350px] cursor-pointer hover:shadow-md h-full ${
        isRunning
          ? "bg-purple-50 border-purple-300 shadow-[0_0_15px_rgba(192,132,252,0.3)]"
          : "bg-gradient-to-br from-indigo-50 to-purple-50 border-purple-200 shadow-sm"
      }`}
    >
      {/* Header */}
      <div className="flex flex-col gap-3 pb-3 border-b border-purple-200/80">
        <div className="flex justify-between items-start w-full">
          <div className="flex items-center gap-2">
            <span className="text-xs bg-purple-200 text-purple-900 px-2 py-1 rounded-md font-extrabold whitespace-nowrap uppercase tracking-wider">
              Smart Extractor
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-extrabold px-2 py-1 rounded shadow-sm bg-purple-500 text-white">
              LOCKED
            </span>
          </div>
        </div>

        <div className="text-sm font-bold text-gray-800 break-all leading-snug">
          Data Extractor (Auto)
        </div>
      </div>
    </div>

      {/* Configuration Popover */}
      {configOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm transition-opacity"
          onClick={(e) => { e.stopPropagation(); setConfigOpen(false); }}
        >
          <div 
            className="w-[450px] max-w-[90vw] max-h-[90vh] bg-white border border-gray-200 shadow-2xl rounded-xl p-5 flex flex-col gap-4 animate-[fadeIn_0.2s_ease-out]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-1 shrink-0">
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-gray-800">Smart Extractor Config</h3>
                <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-gray-200 text-gray-600">
                  LOCKED
                </span>
              </div>
              <button 
                onClick={(e) => { e.stopPropagation(); setConfigOpen(false); }}
                className="text-gray-400 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 rounded p-1.5 transition-colors focus:outline-none"
                title="Close"
              >
                ✕
              </button>
            </div>
            
            <div className="flex flex-col gap-5 overflow-y-auto px-1 snap-y custom-scrollbar text-sm pb-2">
              
              {/* LLM Settings */}
              <div className="flex flex-col gap-3 p-4 bg-gray-50 rounded-lg border border-gray-100">
                <span className="text-xs uppercase font-bold text-gray-500 tracking-wider border-b border-gray-200 pb-2 mb-1">
                  LLM Settings
                </span>
                
                <div className="flex flex-col gap-2 text-gray-700">
                  <label className="font-semibold text-xs text-gray-600 block">Model</label>
                  <select
                    disabled={isRunning || !options}
                    value={config.chatbot_config?.model || ""}
                    onChange={(e) =>
                      onChange("chatbot_config", {
                        ...config.chatbot_config,
                        model: e.target.value,
                      })
                    }
                    className="bg-white border border-gray-300 rounded px-2 py-1.5 focus:border-purple-400 focus:outline-none w-full"
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
                    Temp: <span className="bg-white border rounded px-1">{config.chatbot_config?.temperature}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1.0"
                    step="0.1"
                    disabled={isRunning}
                    value={config.chatbot_config?.temperature || 0}
                    onChange={(e) =>
                      onChange("chatbot_config", {
                        ...config.chatbot_config,
                        temperature: parseFloat(e.target.value),
                      })
                    }
                    className="flex-1 accent-purple-500 w-full"
                  />
                </div>
              </div>

              {/* Locked Prompt Info */}
              <div className="flex flex-col gap-4 p-4 bg-purple-50/50 rounded-lg border border-purple-100">
                <div className="flex flex-col gap-2">
                  <span className="text-xs uppercase font-bold text-purple-800 tracking-wider flex items-center gap-1.5 border-b border-purple-200 pb-2 mb-1">
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                    Prompt Template
                  </span>
                  
                  <div className="text-xs text-gray-700 bg-white/70 p-3 rounded border border-purple-100 shadow-sm mt-1">
                    <p className="font-semibold text-purple-800 mb-1">Extraction Scope:</p>
                    {evaluatorsEnablingExtraction.length > 0 ? (
                      <p>
                        Extracts necessary structure data targeting: 
                        <span className="font-bold text-purple-700 ml-1">
                          {evaluatorsEnablingExtraction.join(", ")}
                        </span>
                      </p>
                    ) : (
                      <p className="italic text-gray-500">
                        No evaluators selected currently.
                      </p>
                    )}
                  </div>
                  
                  <p className="text-gray-600 leading-relaxed text-xs mt-1">
                    Prompt details and constraints are <span className="font-bold text-gray-700">generated dynamically</span> and hidden from manual edits.
                  </p>
                </div>
                <div className="text-[10px] text-gray-400 italic">
                  * This task automatically forms instructions based on constraints from connected Evaluators.
                </div>
              </div>

            </div>
          </div>
        </div>
      )}
    </>
  );
}