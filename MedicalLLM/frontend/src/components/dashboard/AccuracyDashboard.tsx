import React from "react";


import { EvluationBatchResult, AccuracySummary } from "../../types";


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
      
      <div className="flex flex-col items-center justify-center flex-1 py-4">
        <span className="text-5xl font-extrabold text-indigo-600 drop-shadow-sm">
          {(summary.accuracy * 100).toFixed(2)}%
        </span>
        <div className="mt-6 flex gap-5 text-sm text-gray-500 font-medium">
           <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-green-500"></span>
              Correct: {summary.hit_count || 0}
           </div>
           <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-red-500"></span>
              Incorrect: {summary.miss_count || 0}
           </div>
        </div>
      </div>
    </div>
  );
}
