import React from "react";


// ============================================================================
// 文件级注释：ProgressBar 展示整个问答测试流水线的进度状态
// 管理是否失败、是否完成以及当前的题目进度
// ============================================================================

export interface ProgressBarProps {
  isFailure: boolean,
  phase: string,
  currentQuestion: number,
  totalQuestions: number,
  message: string,
  isWorkflowError: boolean,
}

/**
 * 进度条组件
 * @param props 运行状态参数
 * @returns 带有状态样式和动画的进度条UI
 */
export function ProgressBar(props: ProgressBarProps) {
  const {
    isFailure,
    phase,
    currentQuestion,
    totalQuestions,
    message,
    isWorkflowError,
  } = props;

  // 卫语句：如果没有有效的总数，返回一个清晰的兜底状态提示
  if (totalQuestions < 0) {
    return <div className="text-gray-500 text-sm">未能获取题目总数，进度不可用</div>;
  }

  return (
    <div className={`relative overflow-hidden flex items-center justify-between p-2 rounded-lg border transition-colors ${
      isFailure ? 'border-red-500 bg-red-500' :
      phase === 'completed' ? 'border-green-500 bg-green-500' : 'border-blue-100 bg-blue-50'
    }`}>
      {/* 进度条层 */}
      <div 
        className={`absolute left-0 top-0 bottom-0 transition-all duration-500 ease-out ${
          isFailure 
          ? 'bg-red-500' 
          : phase === 'completed' 
            ? 'bg-green-500'
            : 'bg-green-300 opacity-60'
        }`}
        style={{ 
          width: isFailure && phase !== 'completed'
            ? '100%' 
            : phase === 'completed' || phase === 'evaluation' 
              ? '100%' 
              : `${totalQuestions > 0 ? (currentQuestion / totalQuestions) * 100 : 0}%`,
        }}
      />

      <div className="relative z-10 flex items-center gap-4">
        <span className={`text-xs font-semibold uppercase tracking-wider block ${
          isFailure ? 'text-red-100' :
          phase === 'completed' ? 'text-green-100' : 'text-blue-700'
        }`}>Phase:</span>
        <span className={`text-sm font-bold ${
          isFailure || phase === 'completed' ? 'text-white' : 'text-blue-900'
        }`}>
          {isWorkflowError ? 'Workflow Stopped on Error' :
          phase === 'idle' ? 'Ready to Start' :
            phase === 'dataset' ? 'Processing Dataset' :
              phase === 'execution' ? 'Executing Tasks' :
                phase === 'evaluation' ? 'Evaluating Results' :
                  (isFailure ? 'Completed with Errors' : 'Successfully Completed')}
        </span>
        <span className={`text-sm block ml-4 border-l pl-4 ${
          isFailure ? 'text-red-100 border-red-400' :
          phase === 'completed' ? 'text-green-100 border-green-300' : 'text-blue-600 border-blue-200'
        }`}>{message || "Waiting state..."}</span>
      </div>

      {totalQuestions > 0 && (
        <div className="relative z-10 flex items-center gap-3">
          <span className={`text-xs font-semibold uppercase tracking-wider ${
            isFailure ? 'text-red-100' :
            phase === 'completed' ? 'text-green-100' : 'text-blue-700'
          }`}>Completed:</span>
          <span className={`text-sm font-bold bg-white px-2 py-0.5 rounded shadow-sm ${
            isFailure ? 'text-red-700' :
            phase === 'completed' ? 'text-green-600' : 'text-blue-900'
          }`}>
            {currentQuestion} / {totalQuestions}
          </span>
        </div>
      )}
    </div>
  );
}
