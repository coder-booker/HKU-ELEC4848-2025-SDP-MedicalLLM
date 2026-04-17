import React from "react";


// ============================================================================
// 文件级注释：QuestionDetailModal 展示问答日志日志追踪页详情
// 支持侧边靠左滑出、点击背景遮罩区消失的常规 Modal
// ============================================================================

export interface QuestionDetailModalProps {
  questionDetail: any,
  onClose: () => void,
}

/**
 * 侧边悬浮详细弹窗
 * @param props 详情数据和关闭回调
 */
export function QuestionDetailModal(props: QuestionDetailModalProps) {
  const { questionDetail, onClose } = props;
  console.log("Opening QuestionDetailModal with data:", questionDetail);

  return (
    <div
      className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm transition-opacity"
      onClick={onClose}
    >
      <div
        className="absolute top-0 left-0 bottom-0 w-[600px] max-w-[90vw] bg-white shadow-2xl flex flex-col animate-[slideInLeft_0.3s_ease-out]"
        onClick={(e) => e.stopPropagation()} // 阻止冒泡
      >
        <div className="flex justify-between items-center p-4 border-b border-gray-100 bg-gray-50 shrink-0">
          <h2 className="text-lg font-bold text-gray-800">Detail Log</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 bg-gray-200 hover:bg-gray-300 rounded p-1.5 transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 bg-gray-50 text-sm">
          {!questionDetail ? (
            <div className="flex items-center justify-center h-40 text-gray-500">
              Loading...
            </div>
          ) : (
            <div className="flex flex-col gap-6">
              {questionDetail.error && (
                <div className="text-red-500 bg-red-50 p-4 rounded-md border border-red-200 shadow-sm whitespace-pre-wrap flex flex-col gap-2">
                  <h3 className="font-bold text-red-700">Execution Error</h3>
                  <div>{questionDetail.error}</div>
                </div>
              )}

              {questionDetail.answer && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-2">Reference Answer</span>
                  <p className="text-green-700 font-medium">
                    {questionDetail.answer}
                  </p>
                </div>
              )}

              {questionDetail.extractor_result && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-2">Extractor Mapping</span>
                  <pre className="text-[11px] bg-gray-50 p-3 rounded text-gray-700 overflow-x-auto border border-gray-100">
                    {JSON.stringify(questionDetail.extractor_result, null, 2)}
                  </pre>
                </div>
              )}

              {questionDetail.evaluator_results && Object.keys(questionDetail.evaluator_results).length > 0 && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-2">Evaluator Outcomes</span>
                  <div className="flex flex-col gap-3 mt-2">
                    {Object.entries(questionDetail.evaluator_results).map(([key, res]: [string, any], idx) => (
                      <div key={`${key}-${idx}`} className="bg-blue-50/50 p-3 rounded border border-blue-100 text-xs">
                        <span className="font-bold text-blue-800 uppercase text-[10px] bg-blue-100 px-1.5 py-0.5 rounded mr-2">{key.toUpperCase()}</span>
                        <span className="font-medium text-gray-700">Score: {res.score}</span>
                        {res.reason && <p className="text-gray-600 mt-1 italic">{res.reason}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 中间任务过程 / Intermediate Tasks Process Logs */}
              {questionDetail.tasks && questionDetail.tasks.length > 0 ? (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-4">Intermediate Tasks Log</span>
                  <div className="flex flex-col gap-4">
                    {questionDetail.tasks.map((task: any, idx: number) => (
                      <div key={task.task_id || idx} className="border border-gray-100 rounded-lg p-4 bg-gray-50 flex flex-col gap-3">
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
                                    <span className="text-xs font-bold text-green-600 block mb-1">[{outMsg.role?.toUpperCase() || "UNKNOWN"}]</span>
                                    <pre className="text-xs text-gray-800 whitespace-pre-wrap font-mono overflow-x-auto">{outMsg.content || "N/A"}</pre>
                                  </div>
                                ))
                            ) : (
                              <div className="text-xs text-gray-400 italic">N/A</div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-gray-500 italic p-4 text-center border rounded">No tasks generated.</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
