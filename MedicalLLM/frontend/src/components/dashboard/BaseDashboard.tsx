import React from "react";


import { EvluationBatchResult } from "../../types";


/**
 * BaseDashboardProps
 * Contains the shared props passed down from the waterfall layout to each evaluator sub-component.
 */
export interface BaseDashboardProps {
  result: EvluationBatchResult<Record<string, any>>,
}


/**
 * BaseDashboard
 * Fallback dashboard component for unknown evaluators. Displays the raw generic summary data.
 */
export function BaseDashboard({ result }: BaseDashboardProps) {
  const summaryEntries = Object.entries(result.summary || {});

  return (
    <div className="w-96 h-[22rem] flex flex-col p-6 bg-white rounded-xl border border-gray-100 shadow-sm relative transition-shadow hover:shadow-md overflow-hidden">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-800 capitalize leading-tight">
            {result.evaluator_name.replace(/_/g, ' ')}
          </h3>
          <span className="text-xs text-gray-400">Generic Dashboard</span>
        </div>
        <div className="bg-gray-50 text-gray-600 px-2.5 py-1 rounded text-xs font-medium border border-gray-100">
          {result.total_samples} samples
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mt-2 overflow-y-auto pr-1 pb-1 flex-1">
        <div className="bg-blue-50 text-blue-800 px-4 py-2 rounded-lg border border-blue-100 flex flex-col justify-center items-start text-left">
          <span className="text-[10px] uppercase font-semibold text-blue-400">Avg Score</span>
          <span className="text-sm font-bold">{(result.average_score * 100).toFixed(1)}%</span>
        </div>
        
        {summaryEntries.map(([key, value], idx) => {
          // If value is an object, stringify it
          const displayValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
          return (
            <div
              key={idx}
              className="bg-gray-50 text-gray-800 px-4 py-2 rounded-lg border border-gray-200 flex flex-col justify-center items-start text-left truncate"
            >
              <span className="text-[10px] uppercase font-semibold capitalize text-gray-400">{key.replace(/_/g, ' ')}</span>
              <span className="font-bold text-sm w-full truncate">{displayValue}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
