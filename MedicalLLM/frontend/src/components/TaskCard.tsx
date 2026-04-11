import { useState, useRef, useEffect } from "react";
import { PromptEditor } from "./PromptEditor";
import { TaskConfig, TaskState } from "../types";

type TaskCardProps = {
  task: TaskConfig;
  taskState: TaskState | undefined;
  idx: number;
  isRunning: boolean;
  availableTags: string[];
  onTaskChange: (idx: number, field: string, value: string | string[]) => void;
  onRemove: () => void;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  isFirst?: boolean;
  isLast?: boolean;
};

export function TaskCard({
  task,
  taskState,
  idx,
  isRunning,
  availableTags,
  onTaskChange,
  onRemove,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast,
}: TaskCardProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div
      className={`border rounded-xl p-5 flex flex-col gap-4 transition-colors shrink-0 snap-center w-[350px] ${
        taskState?.status === "running"
          ? "bg-yellow-50 border-yellow-300 shadow-[0_0_15px_rgba(253,224,71,0.3)]"
          : taskState?.status === "completed"
          ? "bg-green-50 border-green-300"
          : taskState?.status === "failed"
          ? "bg-red-50 border-red-300"
          : "bg-white border-gray-200 shadow-sm"
      }`}
    >
      {/* 头部（无内边框隔离，仅用底部分隔线） */}
      <div className="flex flex-col gap-3 pb-3 border-b border-gray-200/80">
        <div className="flex justify-between items-start w-full">
          <div className="flex items-center gap-2">
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-md font-extrabold whitespace-nowrap">
              Step {idx + 1}
            </span>
            <div className="flex items-center gap-1">
              <button
                type="button"
                disabled={isRunning || isFirst}
                onClick={onMoveUp}
                className="flex items-center text-[10px] font-bold px-1.5 py-1 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded disabled:opacity-30 transition-colors"
                title="Move Left"
              >
                ◀ 前移
              </button>
              <button
                type="button"
                disabled={isRunning || isLast}
                onClick={onMoveDown}
                className="flex items-center text-[10px] font-bold px-1.5 py-1 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded disabled:opacity-30 transition-colors"
                title="Move Right"
              >
                后移 ▶
              </button>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {taskState && (
              <span
                className={`text-[10px] font-extrabold px-2 py-1 rounded shadow-sm ${
                  taskState.status === "running"
                    ? "bg-yellow-400 text-yellow-900 animate-pulse"
                    : taskState.status === "completed"
                    ? "bg-green-500 text-white"
                    : "bg-red-500 text-white"
                }`}
              >
                {taskState.status.toUpperCase()}
              </span>
            )}
            
            {/* 三点菜单 */}
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="p-1 rounded-md text-gray-500 hover:bg-gray-100 hover:text-gray-800 transition-colors focus:outline-none"
                disabled={isRunning}
              >
                ⋮
              </button>
              
              {menuOpen && !isRunning && (
                <div className="absolute right-0 mt-1 z-10 w-28 bg-white border border-gray-200 rounded-md shadow-lg overflow-hidden font-sans">
                  <button
                    onClick={() => {
                      setMenuOpen(false);
                      onRemove();
                    }}
                    className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors font-bold"
                  >
                    ✕ Remove
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        <textarea
          rows={1}
          value={task.id}
          onChange={(e) => {
            onTaskChange(idx, "id", e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = e.target.scrollHeight + "px";
          }}
          placeholder="Enter Task ID or Title here..."
          className="bg-transparent w-full text-base font-bold text-gray-800 placeholder-gray-400 focus:outline-none resize-none overflow-hidden break-all leading-snug"
          disabled={isRunning}
          style={{ minHeight: "28px" }}
        />
      </div>

      {/* 配置面板 */}
      <details className="group">
        <summary className="text-xs font-bold text-gray-500 cursor-pointer select-none hover:text-gray-700">
          Task Configuration
        </summary>
        <div className="flex flex-col gap-3 mt-3 ml-2 border-l-2 border-gray-200 pl-3">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-gray-600 block">
              Prompt Template
            </label>
            <PromptEditor
              value={task.prompt_template?.text || ""}
              onChange={(val: string) => onTaskChange(idx, "prompt", val)}
              availableTags={availableTags}
              disabled={isRunning}
            />
          </div>

          <div className="flex flex-col gap-1 bg-white p-2 rounded-md border border-gray-200">
            <label className="text-xs font-semibold text-gray-600">
              Msg Sources:
            </label>
            <div className="flex flex-wrap gap-1.5">
              {task.input_msg_sources?.map((tag, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs font-bold border border-blue-100"
                >
                  <span className="opacity-50">#</span>
                  {tag}
                  <button
                    type="button"
                    disabled={isRunning}
                    onClick={() => {
                      const newArr =
                        task.input_msg_sources?.filter((t) => t !== tag) || [];
                      onTaskChange(idx, "input_msg_sources", newArr);
                    }}
                    className="hover:text-blue-900 focus:outline-none ml-1 opacity-70 hover:opacity-100"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
            <div className="flex flex-col gap-2 mt-1 border-t border-gray-50 pt-2">
              <select
                disabled={isRunning || availableTags.filter((t) => !task.input_msg_sources?.includes(t)).length === 0}
                onChange={(e) => {
                  if (e.target.value) {
                    const newArr = [...(task.input_msg_sources || []), e.target.value];
                    onTaskChange(idx, "input_msg_sources", newArr);
                    e.target.value = ""; // Reset dropdown after selection
                  }
                }}
                className="text-xs w-full bg-white border border-gray-300 rounded px-2 py-1.5 focus:outline-none focus:border-blue-400 disabled:opacity-50"
                defaultValue=""
              >
                <option value="" disabled>
                  {availableTags.filter((t) => !task.input_msg_sources?.includes(t)).length === 0 
                    ? "No available sources" 
                    : "-- Add a message source --"}
                </option>
                {availableTags
                  .filter((t) => !task.input_msg_sources?.includes(t))
                  .map((tag) => (
                    <option key={tag} value={tag}>
                        {tag === "question_task" ? `Original Dataset Question (#${tag})` : `Task Output (#${tag})`}
                    </option>
                  ))}
              </select>
            </div>
          </div>
        </div>
      </details>

    </div>
  );
}
