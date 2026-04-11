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
  medical_type: string;
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

export type RecipeOption = Option & { tasks: TaskConfig[] };

export type OptionsState = {
  datasets: Option[];
  evaluators: Option[];
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