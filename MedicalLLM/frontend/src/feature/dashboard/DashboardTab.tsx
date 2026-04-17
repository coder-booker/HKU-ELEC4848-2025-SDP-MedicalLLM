"use client";

import React from "react";
import { QuestionStatusList } from "./components/QuestionStatusList";
import { EvaluationDashboard } from "./components/EvaluationDashboard";
import { QuestionStatus } from "@/types";
import { QuestionDetailModal } from "./components/QuestionDetailModal";

// ============================================================================
// 文件级注释：本组件负责 Dashboard 面板显示（Dashboard Tab）。
// 它包含了左侧的题目流转运行进度日志和右侧的评估看板。
// ============================================================================

export interface DashboardTabProps {
  selectedQuestion: QuestionStatus | null,
  questions: QuestionStatus[],
  handleBackToList: () => void,
  error: string,
  handleViewDetail: (qStatus: QuestionStatus) => void,
  questionDetail: any,
  hasRun: boolean,
  handleDownloadLatestReport: (e: React.MouseEvent) => void,
  evaluationData: any,
}

// ============================================================================
// 函数级注释：DashboardTab 组件
// 左侧显示运行进度态 UI，右侧显示 Evaluation Dashboard 评测汇总面板
// ============================================================================
export function DashboardTab(props: DashboardTabProps) {
  if (!props) {
    return <div className="p-4 text-red-500">属性参数为空错误</div>;
  }

  const {
    selectedQuestion,
    questions,
    handleBackToList,
    error,
    handleViewDetail,
    questionDetail,
    hasRun,
    handleDownloadLatestReport,
    evaluationData,
  } = props;

  return (
    <div className="absolute inset-0 flex gap-4 p-4">
      {/* 左半区：中间态UI（各题目标态与日志） */}
      <div className="w-1/2 flex flex-col gap-4 bg-white p-5 rounded-xl shadow-sm border border-gray-100 overflow-hidden h-full relative">
        <div className="flex items-center justify-between shrink-0">
          <h2 className="text-lg font-bold text-gray-800">
            Execution Progress
          </h2>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200 shadow-sm shrink-0">
            <h3 className="font-bold mb-1 flex items-center gap-2">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Workflow Error
            </h3>
            <p className="text-sm font-mono whitespace-pre-wrap ml-7">{error}</p>
          </div>
        )}

        {/* 使得内部列表或详情能够通过系统自身的滚动条来渲染而不断扩大父级组件 */}
        <div className="flex-1 overflow-y-auto border-t border-gray-100 pt-2 min-h-0 relative">
          <QuestionStatusList
            questions={questions}
            onViewDetail={handleViewDetail}
          />
        </div>
      </div>

      {selectedQuestion && (
        <QuestionDetailModal
          questionDetail={questionDetail}
          onClose={handleBackToList}
        />
      )}

      {/* 右半区：评测中心 */}
      <div className="w-1/2 flex flex-col bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden h-full relative">
        
        {/* 评测仪表板头部区 */}
        <div className="px-6 py-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center shrink-0">
          <span className="font-bold text-gray-800 text-lg">Evaluation Dashboard</span>
          {hasRun && (
            <button
              type="button"
              onClick={handleDownloadLatestReport}
              className="px-4 py-1.5 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-md shadow-sm transition-all focus:outline-none focus:ring-2 flex items-center justify-center gap-2"
              title="Download the latest evaluation report folder as ZIP"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              DL Report (.zip)
            </button>
          )}
        </div>

        {/* 数据区域 */}
        <div className="flex-1 overflow-y-auto bg-gray-50/50 p-6 min-h-0 relative">
          {evaluationData && evaluationData.length > 0 ? (
            <EvaluationDashboard evaluationData={evaluationData} />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <svg className="w-16 h-16 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              <p className="text-sm">No evaluation results have been output yet.</p>
              <p className="text-xs text-gray-400 mt-1">Please wait for the workflow to complete.</p>
            </div>
          )}
        </div>
      </div>
      
    </div>
  );
}
