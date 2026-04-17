export type ChatbotConfig = {
  chatbot_type: string;
  model: string;
  temperature: number;
  max_tokens: number;
};

export type PromptTemplate = {
  text: string;
};

export type TaskConfig = {
  id: string;
  type: string;
  chatbot_config: ChatbotConfig;
  prompt_template?: PromptTemplate;
  input_msg_sources?: string[];
  max_retries?: number;
  timeout?: number;
  connect_to?: string[];
  evaluator_type_list?: string[];
};

export type TaskState = {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  content?: string;
};

export type QuestionStatus = {
  index: number;
  datasetType: string;
  status: "pending" | "running" | "completed" | "failed";
  error?: string;
};
//   connect_to?: string[];
//   evaluator_type_list?: string[];
// };

export type Option = { label: string; value: string };

export type DatasetOption = Option & { supportedEvaluators: string[] };
export type RecipeOption = Option & { tasks: TaskConfig[] };
export type EvaluatorOption = Option & { requiresLLM?: boolean };

export type OptionsState = {
  datasets: DatasetOption[];
  evaluators: EvaluatorOption[];
  chatbotTypes: Option[];
  models: Option[];
  recipes: RecipeOption[];
};

// export type TaskState = {
//   id: string;
//   status: "pending" | "running" | "completed" | "failed";
//   content?: string;
// };

export type WorkflowPhase = "idle" | "dataset" | "execution" | "evaluation" | "completed";

export type WorkflowState = {
  phase: WorkflowPhase;
  message: string;
  currentQuestion: number;
  totalQuestions: number;
  tasks: Record<string, TaskState>;
};

// ============================================================================
// Evaluation Types (Frontend-Backend Shared Protocol)
// ============================================================================

export type EvaluationRecord = {
  score: number,
  prediction: Record<string, any>,
  ground_truth: Record<string, any>,
  detail?: Record<string, any>,
};

export type AccuracySummary = {
  total_samples: number,
  hit_count: number,
  miss_count: number,
  accuracy: number,
};

export type PrecisionSummary = {
  total_samples: number,
  macro_precision: number,
  precision_per_class: Record<string, number>,
};

export type EvaluatorSummary = AccuracySummary | PrecisionSummary | Record<string, any>;

export type EvluationBatchResult<T extends EvaluatorSummary = Record<string, any>> = {
  evaluator_name: string,
  display_type: string,
  metric_name: string,
  total_samples: number,
  average_score: number,
  min_score: number,
  max_score: number,
  records: EvaluationRecord[],
  summary: T,
};

export type EvaluationRunOutput<T extends EvaluatorSummary = Record<string, any>> = {
  dataset_type: string,
  evaluator_name: string,
  result: EvluationBatchResult<T>,
  chart_data: Record<string, any>,
  report_text: string,
};

