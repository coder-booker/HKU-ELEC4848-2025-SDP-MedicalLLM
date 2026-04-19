import { EvluationBatchResult, AccuracySummary } from "@/types";


/**
 * Props tailored for Accuracy components.
 */
interface AccuracyDashboardProps {
  result: EvluationBatchResult<AccuracySummary>,
}


/**
 * AccuracyDashboard
 * Displays accuracy metrics, featuring correct and incorrect sample counts.
 */
export function AccuracyDashboard({ result }: AccuracyDashboardProps) {
  const summary = result.summary;

  return (
    <div className="w-96 h-[22rem] flex flex-col p-6 bg-white rounded-xl border border-gray-100 shadow-sm relative transition-shadow hover:shadow-md">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-800 capitalize leading-tight">
            {result.evaluator_name.replace(/_/g, ' ')}
          </h3>
          <span className="text-xs text-gray-400">Score Dashboard</span>
        </div>
        <div className="bg-gray-50 text-gray-600 px-2.5 py-1 rounded text-xs font-medium border border-gray-100">
          {summary.total_samples} samples
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-3 mt-2 overflow-y-auto pr-1 pb-1 flex-1">
        <div className="bg-blue-50 text-blue-800 px-4 py-2 rounded-lg border border-blue-100 flex flex-col justify-center items-start text-left col-span-2">
          <span className="text-[10px] uppercase font-semibold text-blue-400">Accuracy</span>
          <span className="text-2xl font-bold">{(summary.accuracy * 100).toFixed(2)}%</span>
        </div>
        
        <div className="bg-green-50 text-green-800 px-4 py-2 rounded-lg border border-green-100 flex flex-col justify-center items-start text-left">
          <span className="text-[10px] uppercase font-semibold text-green-500">Hits</span>
          <span className="text-lg font-bold">{summary.hit_count || 0}</span>
        </div>

        <div className="bg-red-50 text-red-800 px-4 py-2 rounded-lg border border-red-100 flex flex-col justify-center items-start text-left">
          <span className="text-[10px] uppercase font-semibold text-red-400">Miss</span>
          <span className="text-lg font-bold">{summary.miss_count || 0}</span>
        </div>
      </div>
    </div>
  );
}