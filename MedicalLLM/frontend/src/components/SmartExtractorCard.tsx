import { TaskConfig, OptionsState } from "../types";

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
  return (
    <div
      className={`border rounded-xl p-5 flex flex-col gap-4 transition-colors shrink-0 snap-center w-[350px] ${
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

      <div className="text-xs text-gray-600 bg-white/50 p-3 rounded-md border border-purple-100">
        <p className="font-semibold text-purple-800 mb-1">Extraction Scope:</p>
        {evaluatorsEnablingExtraction.length > 0 ? (
          <p>
            It will extract necessary structure data for these evaluators: 
            <span className="font-bold text-purple-700 ml-1">
              {evaluatorsEnablingExtraction.join(", ")}
            </span>.
          </p>
        ) : (
          <p className="italic text-gray-500">
            No evaluators selected currently.
          </p>
        )}
        <p className="italic mt-2 text-[10px] text-gray-400">
          * Prompt details and schema are generated dynamically and hidden.
        </p>
      </div>

      {/* Configuration */}
      <details className="group">
        <summary className="text-xs font-bold text-gray-500 cursor-pointer select-none hover:text-gray-700 pb-1">
          Extractor LLM Configuration
        </summary>
        <div className="flex flex-col gap-3 mt-2 ml-2 border-l-2 border-purple-200 pl-3">
          <div className="flex flex-col gap-2 p-2 bg-white/80 rounded border border-purple-100">
            <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">LLM Settings</span>
            <div className="flex gap-2">
              <select
                disabled={isRunning || !options}
                value={config.chatbot_config?.model || ""}
                onChange={(e) =>
                  onChange("chatbot_config", {
                    ...config.chatbot_config,
                    model: e.target.value,
                  })
                }
                className="flex-1 text-xs bg-white border border-gray-200 rounded px-2 py-1.5 focus:border-purple-400 focus:outline-none"
              >
                <option value="" disabled>Select Model</option>
                {options?.models?.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2 mt-1">
              <label className="text-[10px] font-bold text-gray-500 w-16">Temp: {config.chatbot_config?.temperature}</label>
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
                className="flex-1 accent-purple-500"
              />
            </div>
          </div>
        </div>
      </details>
    </div>
  );
}
