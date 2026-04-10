# MedicalLLM 架构与端到端流程说明（可直接附在后续 Prompt）

## 1. 项目当前核心目标

这个子系统（`medical_llm_workflow`）做的是一条可配置的医疗推理评测流水线：

1. 从 benchmark 数据集取题（当前是 MedQA）。
2. 按 recipe 生成任务链（当前主用 3-step clinical reasoning）。
3. 逐 task 调用 LLM 完成推理。
4. 用 SmartExtractor 将最终输出结构化。
5. 用 evaluator 计算指标（当前主用 accuracy）。
6. 输出运行日志与评测报告。

---

## 2. 分层架构（代码结构视角）

- `Controller`：预留层，目前基本为空。
- `Service`：编排层，工作流执行主逻辑。
- `Domain`：核心业务语义（tasks/recipes/dataset/evaluator/workflow_context）。
- `Infrastructure`：LLM client 与底层数据结构。
- `schemas`：跨层共享消息协议。

关键文件：

- 入口脚本：`medical_llm_workflow/main.py`
- HTTP 服务：`medical_llm_workflow/server.py`
- 工作流编排：`medical_llm_workflow/Service/workflow/workflow.py`
- 任务抽象与工厂：`medical_llm_workflow/Domain/tasks/base_task.py`、`medical_llm_workflow/Domain/tasks/task_factory.py`
- Recipe：`medical_llm_workflow/Domain/recipes/recipe_factory.py`
- Dataset：`medical_llm_workflow/Domain/benchmark/Dataset/all_datasets/medqa.py`
- Evaluator：`medical_llm_workflow/Domain/benchmark/Evaluator/simpleEvaluator/accuracy.py`
- 结构化适配：`medical_llm_workflow/Domain/benchmark/EvaluatorAdaptor/evaluator_adaptor.py`
- LLM 客户端：`medical_llm_workflow/Infrastructure/LLM_client/all_clients/poe_client.py`
- 日志与 SSE 桥接：`medical_llm_workflow/utils.py`

---

## 3. 两条运行路径

## 3.1 脚本直跑路径（你目前终端跑的是这条）

入口：`python -m medical_llm_workflow.main`

调用链：

1. `main.py::main()`
2. `main.py::run_workflow(...)`
3. `Workflow(...).run()`
4. 对每道题 `fire_tasks_execution(...)`
5. `evaluate(...)`
6. `build_report(...)` 写出 `evaluation_report.md`
7. `print_result_record(...)` 打印每个 task 的 input/output

特点：

- 线性执行，按题循环。
- 每道题一个 `WorkflowContext`。
- 运行中会生成 `workflow.log` 与 `workflow.md`。

## 3.2 API + SSE 路径（给前端实时流式日志）

入口：`POST /api/run`

调用链（设计意图）：

1. `server.py` 收到 `RunConfigPayload`
2. 启动 `workflow_runner` 后台 task
3. `sse_queue_var` 绑定当前协程队列
4. 调用核心 `run_workflow(...)`
5. 运行日志通过 `print_log(...) -> queue.put_nowait(...)` 持续流出
6. 结束时读取 `evaluation_report.md` + `workflow.md`
7. 以 `[DONE] {json}` 收尾

前端收到两类 SSE 消息：

- streaming：`{"status":"STREAMING","log":"..."}`
- done：`[DONE] {"status":"DONE", ...}`

---

## 4. 端到端数据流（重点）

## 4.1 配置输入层

来源有两种：

- 脚本默认常量：dataset/evaluator/chatbot/recipe（定义在 `main.py`）
- API 传入 `RunConfigPayload`（`server.py`）

被转成：

- `DatasetConfig`
- `List[EvaluatorType]`
- `chatbot_config: BaseChatbotConfig`
- `task_config_list`（由 recipe 生成，或由 `custom_tasks` 直接注入）

## 4.2 数据集流入

`Workflow.init_dataset_inlet()`：

1. `DatasetFactory.create(dataset_config)` 构造具体数据集（当前 `MedQADataset`）。
2. 抽题并得到两种表示：
   - `text_question`：喂给 LLM 的文本题目
   - `json_question`：保留结构化答案用于评测
3. 形成 `DatasetInletItem` 列表，后续与每个 `WorkflowContext` 按索引对齐。

## 4.3 Task 执行数据流（每道题）

每道题执行链：

1. inlet：`PlainTextTask(question_task)` 把题目文本放进上下文。
2. core tasks：由 recipe 生成（当前 3 步）。
3. outlet：`SmartExtractorTask` 输出评测所需 JSON。

执行器：`fire_tasks_execution(...)`

- 逐个 `TaskConfig` 走 `TaskFactory.create(...)`
- 每个 task 产出 `TaskRecord = {task_config, task_context}`
- 写入 `WorkflowContext`（底层是 `LinkedHashList` 保序 + O(1) 按 task_id 索引）

`BaseTask.execute(...)` 的关键机制：

1. `get_messages_for_llm_call(...)` 收集上游 `input_msg_sources` 的 output 消息。
2. `build_prompt(...)` 把 prompt 中 `{{task_id}}` 占位符替换为对应 task 最后一条输出。
3. `ClientFactory.get_client_instance(...)` 取得 LLM client（有缓存）。
4. `call_chatbot(...)` 返回字符串响应。
5. 组装 `TaskContext{input, output}` 并 append 到 `WorkflowContext`。

## 4.4 结构化抽取与评测流

1. `SmartExtractorTask` 根据 evaluator 列表动态生成 expected schema。
2. SmartExtractor 调用 LLM 输出 JSON 字符串。
3. `evaluate(...)` 逐题读取：
   - 预测：最后一个 task 的输出（即 extractor 输出）
   - 真值：dataset 的 `json_question`
4. `EvaluatorAdaptor` 做协议适配：
   - dataset 字段 -> evaluator 字段
   - extractor 输出 -> evaluator 字段补齐
5. `EvaluatorFactory.create(...)` 创建 evaluator（当前 accuracy）。
6. 得到 batch result（average/min/max/records/summary）。
7. `build_report(...)` 融合所有 evaluator 结果，写 `evaluation_report.md`。

## 4.5 日志与可观测性数据流

统一经 `print_log(...)`：

- stdout 打印
- 追加写入 `workflow.log`
- 追加写入 `workflow.md`
- 如果当前上下文有 SSE queue，则推送给前端实时显示

---

## 5. 当前默认 Recipe（3-step）

`MedicalReasoning3StepsRecipe.build_task_configs()` 产生：

1. `Problem Representation Task`
2. `Hypothesis Generation Task`
3. `Hypothesis Evaluation Task`

它们都是 `TaskType.SINGLE_AGENT`，由 `TaskFactory` 按 `medical_type` 映射到专用 Task 类。

---

## 6. 关键数据结构速览

- `ConversationMessage`：`{role, content, status}`
- `TaskContext`：`{input: [...], output: [...]}`
- `TaskRecord`：`{task_config, task_context}`
- `WorkflowContext`：按 task 顺序存储所有 `TaskRecord`
- `EvaluationSample`：`{llm_output_dict, dataset_ground_truth_dict}`
- `EvluationBatchResult`：批量评测统计与明细

---

## 7. 你后续沟通时可直接粘贴的“系统上下文段”

```text
该项目的核心是 medical_llm_workflow 子系统，采用 Domain-Service-Infrastructure 分层。
主流程是：Dataset(当前 MedQA) 抽题 -> Recipe 生成 Task 链(默认 3-step medical reasoning)
-> 按 task_id 在 WorkflowContext 中传递上下文并逐步调用 LLM
-> SmartExtractor 抽取评测 JSON
-> Evaluator(当前 accuracy) 计算指标并产出 evaluation_report.md。

关键特性：
- Task prompt 支持 {{task_id}} 占位符，从上游任务最后输出自动注入。
- WorkflowContext 底层使用 LinkedHashList，既保序又可 O(1) 按 task_id 查找。
- print_log 同时写 stdout/workflow.log/workflow.md，并可通过 SSE 实时推给前端。

当前主要入口：
- 脚本入口：python -m medical_llm_workflow.main
- 服务入口：medical_llm_workflow/server.py 提供 /api/options 和 /api/run
```

---

## 8. 现状注意点（按代码现状）

1. `server.py` 存在与导入函数同名的 `run_workflow` 路由函数，`workflow_runner` 中的 `await run_workflow(...)` 有递归/参数不匹配风险（建议把导入函数改名如 `run_workflow_core`）。
2. `Workflow.init_extractor()` 当前把 extractor 的 `input_msg_sources` 设为 `['question_task']`，可能拿不到“最终推理答案”上下文，需确认是否应改为引用最终推理 task。
3. `BaseTask.execute()` 中模型响应消息 role 当前写成 `USER`，语义上更像 `BOT`。
4. `Workflow.__init__(id: uuid.UUID = uuid.uuid4())` 默认参数会在定义时求值，可能导致多个实例共享同一个默认 id。

如果你愿意，我下一步可以直接给出一版“最小修复补丁”，只改这 4 处且不影响现有目录结构。
