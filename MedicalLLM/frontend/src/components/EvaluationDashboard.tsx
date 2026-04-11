import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface EvaluationDashboardProps {
  evaluationData: any[];
}

export function EvaluationDashboard({ evaluationData }: EvaluationDashboardProps) {
  if (!evaluationData || evaluationData.length === 0) {
    return null;
  }

  return (
    <div className="mb-8 flex flex-wrap gap-6">
      {evaluationData.map((result: any, i: number) => {
        const evalResult = result.result;
        const summaryData = Object.entries(evalResult.summary).map(([k, v]) => ({
          name: k,
          count: v,
        }));

        if (evalResult.display_type === "percentage") {
          return (
            <div key={`eval-${i}`} className="w-80 flex flex-col p-6 bg-white rounded-xl border border-gray-100 shadow-sm relative">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="text-lg font-bold text-gray-800 capitalize leading-tight">{result.evaluator_name.replace(/_/g, ' ')}</h3>
                  <span className="text-xs text-gray-400">Score Dashboard</span>
                </div>
                <div className="bg-gray-50 text-gray-600 px-2.5 py-1 rounded text-xs font-medium border border-gray-100">
                  {evalResult.total_samples} samples
                </div>
              </div>
              
              <div className="flex flex-col items-center justify-center flex-1 py-4">
                <span className="text-5xl font-extrabold text-indigo-600 drop-shadow-sm">
                  {(evalResult.average_score * 100).toFixed(2)}%
                </span>
                <div className="mt-6 flex gap-5 text-sm text-gray-500 font-medium">
                   <div className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded-full bg-green-500"></span>
                      Correct: {evalResult.summary.hit_count || 0}
                   </div>
                   <div className="flex items-center gap-1.5">
                      <span className="w-3 h-3 rounded-full bg-red-500"></span>
                      Incorrect: {evalResult.total_samples - (evalResult.summary.hit_count || 0)}
                   </div>
                </div>
              </div>
            </div>
          );
        }

        return (
          <div key={`eval-${i}`} className="w-full border rounded-xl p-5 shadow-sm bg-white">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-800 capitalize">{result.evaluator_name.replace(/_/g, ' ')} Dashboard</h3>
              <div className="flex gap-4">
                <div className="bg-blue-50 text-blue-800 px-4 py-2 rounded-lg border border-blue-100 flex flex-col items-center">
                  <span className="text-xs uppercase font-semibold">Total Samples</span>
                  <span className="text-xl font-bold">{evalResult.total_samples}</span>
                </div>
                <div className="bg-green-50 text-green-800 px-4 py-2 rounded-lg border border-green-100 flex flex-col items-center">
                  <span className="text-xs uppercase font-semibold">Avg Score</span>
                  <span className="text-xl font-bold">{(evalResult.average_score * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {summaryData.length > 0 && (
              <div className="w-full h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={summaryData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} />
                    <Tooltip
                      cursor={{fill: '#F3F4F6'}}
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                    />
                    <Bar dataKey="count" fill="#4F46E5" radius={[4, 4, 0, 0]} maxBarSize={60} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
