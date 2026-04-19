import React from "react";
import { QuestionStatus } from "../../../types";

interface QuestionStatusListProps {
  questions: QuestionStatus[];
  onViewDetail: (q: QuestionStatus) => void;
}

export function QuestionStatusList({ questions, onViewDetail }: QuestionStatusListProps) {
  console.log("Rendering QuestionStatusList with questions:", questions);
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {questions.length === 0 && (
        <div className="text-gray-400 text-sm italic col-span-full">Awaiting questions to start...</div>
      )}
      {questions.map((q) => (
        <div
          key={`${q.datasetType}-${q.index}`}
          onClick={() => q.status === "completed" || q.status === "failed" ? onViewDetail(q) : null}
          className={`p-4 rounded-lg border flex flex-col gap-2 transition-all ${
            q.status === "completed" ? "bg-green-50 border-green-200 hover:bg-green-100 cursor-pointer hover:shadow-md" :
            q.status === "running" ? "bg-blue-50 border-blue-200 shadow-sm" :
            q.status === "failed" ? "bg-red-50 border-red-200 cursor-pointer" :
            "bg-gray-50 border-gray-200"
          }`}
        >
          <div className="flex justify-between items-center">
            <span className="font-semibold text-sm">Question #{q.index}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              q.status === "completed" ? "bg-green-200 text-green-800" :
              q.status === "running" ? "bg-blue-200 text-blue-800 animate-pulse" :
              q.status === "failed" ? "bg-red-200 text-red-800" :
              "bg-gray-200 text-gray-800"
            }`}>
              {q.status.toUpperCase()}
            </span>
          </div>
          <div className="text-xs text-gray-500">From: {q.datasetType}</div>
        </div>
      ))}
    </div>
  );
}
