import React from "react";
import { QuestionStatus } from "../types";

interface QuestionDetailViewProps {
  questionDetail: any;
}

export function QuestionDetailView({ questionDetail }: QuestionDetailViewProps) {
  if (!questionDetail) {
    return <div className="text-center p-8 text-gray-500 italic">Loading details...</div>;
  }

  return (
    <div className="flex flex-col gap-4">
      {questionDetail.error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg shadow-sm">
          <h3 className="font-bold mb-2">Execution Error</h3>
          <p className="font-mono text-sm whitespace-pre-wrap">{questionDetail.error}</p>
        </div>
      )}

      {questionDetail.tasks && questionDetail.tasks.length > 0 ? (
        questionDetail.tasks.map((task: any, idx: number) => (
        <div key={task.task_id} className="border border-gray-100 rounded-lg p-4 bg-gray-50 flex flex-col gap-3">
          <h3 className="font-bold text-gray-700 pb-2 border-b border-gray-200">
            {idx + 1}. Task: {task.task_id} <span className="text-xs font-normal text-gray-400 ml-2">({task.task_type})</span>
          </h3>
          
          <div className="grid grid-cols-1 gap-4">
            {/* Inputs Section */}
            <div className="flex flex-col gap-2">
              <h4 className="text-sm font-semibold text-blue-800">Inputs</h4>
              {task.inputs && task.inputs.length > 0 ? (
                task.inputs.map((inMsg: any, i: number) => (
                  <div key={`in-${i}`} className="bg-white p-3 rounded border border-blue-100 shadow-sm">
                    <span className="text-xs font-bold text-blue-600 block mb-1">[{inMsg.role.toUpperCase()}]</span>
                    <pre className="text-xs text-gray-800 whitespace-pre-wrap font-mono overflow-x-auto">{inMsg.content || "N/A"}</pre>
                  </div>
                ))
              ) : (
                <div className="text-xs text-gray-400 italic">N/A</div>
              )}
            </div>
            
            {/* Outputs Section */}
            <div className="flex flex-col gap-2">
              <h4 className="text-sm font-semibold text-green-800">Outputs</h4>
              {task.outputs && task.outputs.length > 0 ? (
                task.outputs.map((outMsg: any, i: number) => (
                  <div key={`out-${i}`} className="bg-white p-3 rounded border border-green-100 shadow-sm">
                    <span className="text-xs font-bold text-green-600 block mb-1">[{outMsg.role.toUpperCase()}]</span>
                    <pre className="text-xs text-gray-800 whitespace-pre-wrap font-mono overflow-x-auto">{outMsg.content || "N/A"}</pre>
                  </div>
                ))
              ) : (
                <div className="text-xs text-gray-400 italic">N/A</div>
              )}
            </div>
          </div>
        </div>
      ))
      ) : (
        <div className="text-gray-500 italic p-4 text-center border rounded">No tasks generated.</div>
      )}
    </div>
  );
}
