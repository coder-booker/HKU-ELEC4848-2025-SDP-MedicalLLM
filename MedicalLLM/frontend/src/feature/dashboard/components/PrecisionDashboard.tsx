import { EvluationBatchResult, PrecisionSummary } from "@/types";


/**
 * PrecisionDashboardProps
 * Contains Precision-specific summary result props.
 */
interface PrecisionDashboardProps {
  result: EvluationBatchResult<PrecisionSummary>,
}


/**
 * PrecisionDashboard
 * A tailored visualizer for the Precision Evaluator, displaying precision per class with clean progress bars.
 */
export function PrecisionDashboard({ result }: PrecisionDashboardProps) {
  const summary = result.summary;
  
  // Transform and sort precision data: standard options first, empty/unmatched last
  const summaryData = Object.entries(summary.precision_per_class || {})
    .sort(([keyA], [keyB]) => {
      // Push empty strings to the bottom of the list
      if (keyA === "") return 1;
      if (keyB === "") return -1;
      return keyA.localeCompare(keyB);
    })
    .map(([className, precisionValue]) => ({
      // Provide a fallback explicit label for unmatched/empty predictions
      name: className.trim() === "" ? "N/A" : className,
      // Convert fraction to percentage for readability
      precision: Number((Number(precisionValue) * 100).toFixed(1)),
    }));

  return (
    <div className="w-96 h-[22rem] flex flex-col p-6 bg-white rounded-xl border border-gray-100 shadow-sm relative transition-shadow hover:shadow-md overflow-hidden">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-800 capitalize leading-tight">
            {result.evaluator_name.replace(/_/g, ' ')}
          </h3>
          <span className="text-xs text-gray-400">Class Precision Breakdown</span>
        </div>
        <div className="bg-gray-50 text-gray-600 px-2.5 py-1 rounded text-xs font-medium border border-gray-100">
          {summary.total_samples} samples
        </div>
      </div>
      
      <div className="flex flex-col gap-3 mb-4">
        <div className="bg-blue-50 text-blue-800 px-4 py-2 rounded-lg border border-blue-100 flex flex-col justify-center items-start text-left w-full">
          <span className="text-[10px] uppercase font-semibold text-blue-400">Macro Precision</span>
          <span className="text-2xl font-bold">{(summary.macro_precision * 100).toFixed(1)}%</span>
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto pr-2 flex flex-col gap-4">
        {summaryData.length > 0 ? (
          summaryData.map((item, idx) => (
            <div key={idx} className="flex flex-col gap-1.5">
              <div className="flex justify-between text-xs font-semibold items-center">
                <span className="text-gray-700">
                  {item.name === "N/A" ? (
                    <span className="bg-red-50 text-red-600 border border-red-200 px-1.5 py-0.5 rounded text-[10px]">
                      Unmatched (N/A)
                    </span>
                  ) : (
                    `Option ${item.name}`
                  )}
                </span>
                <span className="text-indigo-600">{item.precision}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div
                  className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${item.precision}%` }}
                />
              </div>
            </div>
          ))
        ) : (
          <div className="text-sm text-gray-400 flex items-center justify-center h-full">
            No class data available.
          </div>
        )}
      </div>
    </div>
  );
}