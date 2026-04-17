import React, { useState, useMemo } from "react";


import { EvaluationRunOutput } from "../../../types";
import { AccuracyDashboard } from "./AccuracyDashboard";
import { PrecisionDashboard } from "./PrecisionDashboard";
import { BaseDashboard } from "./BaseDashboard";


/**
 * Evaluator Registry
 * Statically maps known evaluator names from the backend to specialized React components.
 */
const EVALUATOR_MAP: Record<string, React.FC<{ result: any }>> = {
  accuracy: AccuracyDashboard,
  precision: PrecisionDashboard,
  accuracy_evaluator: AccuracyDashboard,
  precision_evaluator: PrecisionDashboard,
};

/**
 * Props for the main Dashboard waterfall layout
 */
interface EvaluationDashboardProps {
  evaluationData: EvaluationRunOutput[],
}


/**
 * EvaluationDashboard
 * Master container orchestrating all evaluator dashboards in a waterfall layout.
 */
export function EvaluationDashboard({ evaluationData }: EvaluationDashboardProps) {
  // Use a state to manage visibly checked evaluators
  const [hiddenEvaluators, setHiddenEvaluators] = useState<Record<string, boolean>>({});

  if (!evaluationData || evaluationData.length === 0) {
    return null;
  }

  // Toggle utility: Flip boolean flag.
  const toggleEvaluator = (evalName: string) => {
    setHiddenEvaluators((prev) => ({
      ...prev,
      [evalName]: !prev[evalName],
    }));
  };

  // Group evaluation data by dataset_type
  const groupedData = useMemo(() => {
    const map = new Map<string, EvaluationRunOutput[]>();
    evaluationData.forEach((data) => {
      const type = data.dataset_type || "Unknown Dataset";
      if (!map.has(type)) {
        map.set(type, []);
      }
      map.get(type)!.push(data);
    });
    return Array.from(map.entries());
  }, [evaluationData]);

  // Extract all unique evaluators across all datasets for the filter
  const allEvaluatorNames = useMemo(() => {
    return Array.from(new Set(evaluationData.map((d) => d.evaluator_name)));
  }, [evaluationData]);

  return (
    <div className="mb-8 w-full flex flex-col gap-6">
      {/* 
        Filter Control Panel
        Provides simple pill-buttons to switch specific dashboards on/off
      */}
      <div className="flex gap-3 mb-2 flex-wrap">
        {allEvaluatorNames.map((evalName, idx) => {
          const isHidden = hiddenEvaluators[evalName] || false;
          
          return (
            <button
              key={`filter-${idx}`}
              onClick={() => toggleEvaluator(evalName)}
              className={`
                px-3 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider border transition-colors
                ${isHidden 
                  ? "bg-gray-50 text-gray-400 border-gray-200" 
                  : "bg-indigo-50 text-indigo-700 border-indigo-200 shadow-sm"
                }
              `}
            >
              {evalName.replace(/_/g, ' ')}
            </button>
          );
        })}
      </div>

      {/* 
        Waterfall Output Flow
        Renders the available sub-dashboards top-to-bottom if not hidden by toggle.
        Grouped by dataset.
      */}
      <div className="flex flex-col gap-6 w-full">
        {groupedData.map(([datasetType, datasetEvaluationData], idx) => (
          <div key={`dataset-group-${idx}`} className="flex flex-col gap-4">
            <h3 className="text-xl font-bold border-b pb-2 capitalize tracking-wide">{datasetType.replace(/_/g, ' ')}</h3>
            <div className="flex flex-wrap gap-6 w-full items-start content-start">
              {datasetEvaluationData.map((data, i) => {
                const evalResult = data.result;
                const evalName = data.evaluator_name;
                
                if (hiddenEvaluators[evalName]) {
                  return null;
                }

                // Fallback to BaseDashboard if current evaluator is unmapped
                const RenderComponent = EVALUATOR_MAP[evalName] || BaseDashboard;

                return (
                  <RenderComponent key={`eval-${idx}-${i}`} result={evalResult} />
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
