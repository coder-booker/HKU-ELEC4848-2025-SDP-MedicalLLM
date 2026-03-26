1.	很多文件/数据应该放在附录
2.	项目的成本效益评估和可行性评估


工作流：
- 为什么做
    1. 原意是想探索不同方法的效果和cost，然后衡量 cost 和 performance 给出一些工程化方案
    2. 调查之后发现，虽然这方面已经有不少工作了，但评估标准碎片化，并没有所有方法处于同一标准下的分析
    3. 似乎缺乏多模态的工作
- 常规工作流
    - ReAct
    - agent
        - 重复生成
        - 多角色
    - prompt
        - CoT
        - template
    - 上下文管理
        - 无上下文
        - 模型自己问的上下文
        - 我们提供的上下文
        - 多模态（stage 2）
- 评估维度：
    - TODO






# benchmark 、竞品、 prompt 设计和数据集的 source


- 综述，最多就是帮我进行了分类和列出很多 LLM 工作流
    - 基本信息：
        - 标题：Medical Reasoning in the Era of Large Language Models: A Systematic Review
        - 发表：2025 年 8 月
        - 范围：分析 60 篇 2022–2025 年的医学推理 LLM 论文
        - https://arxiv.org/html/2508.00669v1
    - 工作流相关
        | 方法层面 | 具体方法                                              | 论文中的应用                |
        | ---- | ------------------------------------------------- | --------------------- |
        | 训练时  | Supervised Fine-Tuning (SFT)                      | 在医学推理数据集上微调，学习领域特定逻辑  |
        |      | Reinforcement Learning from Human Feedback (RLHF) | 用人类反馈优化推理，提高与临床标准的一致性 |
        |      | Mixture of Experts (MoE) 及多模型集成                   | 多个推理路径生成与评估           |
        | 推理时  | Chain-of-Thought (CoT)                            | 逐步推理，改进复杂医学问题求解       |
        |      | Self-Consistency（多路径生成）                           | 生成多个推理路径，投票或集成得出最终答案  |
        |      | Tree-of-Thought (ToT)                             | 结构化搜索，克服线性 CoT 的局限    |
        |      | Few-shot 示例                                       | 在输入中提供示例，帮助模型快速适应     |
        |      | Zero-shot 推理                                      | 直接推理，不依赖示例（作为基线）      |
    - 评估方法：（因为是综述，所以没有详细的评估方法）
        - 简单基准（USMLE/MedQA）：多选准确率。
        - 复杂基准（MedXpertQA、MedAgentsBench）：强调多步推理、困难问题、专家审核。
        - 推理质量：ChestX-Reasoner 等框架对推理过程的细粒度评估。
        - 人类验证：临床医生进行定性审查和压力测试（如罕见病 edge case）。
    - 评估维度
        - 没啥维度，得等 ai 回答，反正我是没看见

- 量化了 CoT 这一具体提示工程方法对医学推理的改进 + 利用 "NOTA 修改版本"（No-Original-Text-Available 修改），即改写或删除关键信息，以测试模型的真实推理能力（不只是记忆）。
    - 基础信息：
        - 论文 4：Fidelity of Medical Reasoning in Large Language Models（医学推理的保真度）
        - 发表：2025 年 7 月 31 日
        - https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2837372
    - 工作流相关
        - Zero-shot	不提供任何推理指导，模型直接回答（基线）
        - Chain-of-Thought (CoT)	显式指导模型逐步推理，输出思考过程，然后给出答案
        - NOTA
    - Prompt：
        - 除了基础的指示，没有给模板
    - 评估方法：
        - 和医院合作人肉评估
    - 提供的资源：
        - 代码和QA data

<!-- - 对比推理模型和非推理模型
    - 基础信息：
        - 年份：2025
        - 标题：Evaluating the Reasoning Capabilities of Large Language Models in Clinical Tasks Using the MIMIC-IV Dataset
        - 期刊：Journal of Medical Internet Research (JMIR)
        - 发表：2025 年 7 月 29 日
        - URL：https://www.jmir.org/2025/1/e74142
    - 数据集：
        - MIMIC-IV 真实医院出院总结（300 份）
    - 评估方向：
        - 初级诊断生成
        - 医学编码（ICD-9 代码预测）
        - 住院再入院风险分层
    - 工作流相关：
        | 模型类型  | 具体方法                        | 描述                                            |
        | ----- | --------------------------- | --------------------------------------------- |
        | 非推理模型 | Zero-shot（无指导）              | 直接输入，模型直接输出答案                                 |
        |       | Zero-shot + Rationale（要求解释） | 输入中加入"请提供推理"的指导                               |
        | 推理模型  | Zero-shot 内生推理              | 模型自有的内部推理机制（如 O3、DeepSeek-R1 的 thinking part） |
        |       | Zero-shot + Rationale 提示    | 同时要求模型生成推理和答案                                 |
    - 评估指标：
        - 诊断：F1 分数、正确率（Correctness %）
        - ICD-9 编码：准确率（Correctness %）
        - 再入院风险：F1 分数、准确率 -->

- 评估用的框架 + 对比了小模型和大模型 + LLM 作为评判者有严重局限（自我识别和增强偏差。）
    - 基础信息：
        - 年份：2025
        - 标题：Clinical Large Language Model Evaluation by Expert Review: Development and Validation of the CLEVER Rubric
        - 期刊：JMIR AI
        - 发表：2025年12月3日
        - URL：https://ai.jmir.org/2025/1/e72153
    - 评估指标：
        - 医学医生评估：随机盲化、多维度评分量表 CLEVER（准确性、临床相关性、简洁性）。
        - 评估维度（基于临床实践最佳实践）：
            - 真实性（Factuality）：医学信息的正确性。
            - 临床相关性（Clinical Relevance）：回答是否适用于实际临床场景。
            - 简洁性（Conciseness）：是否清晰、无冗余。
        - 统计验证：医学医生评分的一致性、重测可靠性。





# 竞品的 source
- openEvidence
    - https://journals.sagepub.com/doi/10.1177/21501319251332215
    - 商用闭源模型
        - 优化手段可见的主要是：
            - RAG 架构 + 证据检索；
            - PICO 风格的简单 prompt 结构指南。
            - 微调
        - 看不到的是：
            - 多步显式临床推理工作流（problem list、DDx、evidence analysis 等）；
            - 公开的微调流程或可复用的 orchestration 框架
- Autonomous AI Agents for Clinical Decision-Making
    - https://arxiv.org/html/2404.04667v1
    - 没有代码
    - 对 LLM 的优化手段
        - Agent 工作流设计（最主要的优化）
            - 工具调用阶段：
                - LLM 读取病例 / 临床问题；
                - 自主调用影像模型、病理模型、基因分析工具等，获得多模态信息。
            - 文献检索与证据整合阶段：
                - 使用检索工具查找指南和文献；
                - LLM 整合工具输出 + 文献证据，生成诊断与治疗建议，并附上引用。
        - Prompt engineering
            - 角色指令：让 LLM 扮演“肿瘤学临床专家 + orchestrator”；
            - 工具调用规范：通过说明每个工具输入输出格式，引导 LLM 在合适时机调用；
            - 结构化输出约束：要求最终建议包括诊断、分期、治疗方案、以及引用文献。    
        - 微调 / 训练
            - 论文没有报告对底层 LLM 进行专门的医学微调或 RLHF。
- MedChain
    - https://openreview.net/forum?id=YvuufwkFJY
    - github：https://github.com/ljwztc/MedChain
    - 对 LLM 的优化手段
        - Agent 工作流
            - 设计了一套基于 LLM 的 tool‑calling agent 框架，支持 EHR 查询、医学知识库检索、指南查询等工具。
            - Workflow 被抽象为：
                - perception（读取病例/问题）→
                - decision（选择工具）→
                - act（调用工具并获取结果）→
                - reflect（更新记忆、生成回答）。
        - Prompt 结构
            - 使用典型的 “system + tool-spec + conversation history” 组合：
            - system 中指定角色和目标（medical AI assistant）；
            - 每个工具有单独的自然语言描述和调用示例。
        - 优化 / 微调
            - 论文主要讲 agent 设计和 EHR 集成，并未进行复杂的 RL 或多轮微调。
- 通用编制 agent 平台
    - LangGraph，Flowise
    - 优点：抽象能力强，节点/状态/多 agent 都支持。
    - 局限：
        - 完全 领域无关，不内置任何“临床推理步骤”概念；
        - 对医疗人来说“过重”：要先学一层 DSL / 图结构，才能开始实验工作流；
        - 不提供针对诊断任务的现成模板或实践经验。



# 临床决策结构的source
- 整体框架
    - link：https://pmc.ncbi.nlm.nih.gov/articles/PMC5611427/#sec1-2
    - 具体框架：
        - 1. 假设演绎模型
            - 线索获取
            - 线索解释
            - 假设生成
            - 假设评估
                - 如果评估后发现不匹配，重新收集线索
        - 2. 模式识别模型
            - 基于此前的记忆进行模式匹配，跳过一些分析（也就是经验论
        - 3. 1+2 混合模式
        - 4. 临床推理模型路径
            - 该模型是对假设演绎模型的扩展，它更详细地描述了评估阶段的具体过程，并通过引入饱和概念，更深入地阐释了评估如何最终得出诊断
        - 5. 临床推理的整合模型
            - 该模型强调医生基于其先验知识和情境或环境因素的感知。假设或问题表征会根据新信息的收集和评估不断迭代发展，
            - 感觉没啥区别
        - 6. 初级保健诊断推理策略模型
            - 诊断假设的提出
            - 诊断假设的完善
            - 最终诊断的确定
            - 该模型并未进一步说明在诊断推理过程中第二阶段和第三阶段的策略在何时何地使用。
- 问题列表/表示
    - link：https://pmc.ncbi.nlm.nih.gov/articles/PMC5834975/
    - 临床推理过程的早期步骤是问题表征，即创建一个简短的心理摘要，突出病例的关键点。这使得医生能够处理接收到的信息，从而做出有针对性的鉴别诊断。
    - 近期研究表明，临床诊疗过程中的重要任务包括：问题界定、诊断、治疗和反思

- 这是一篇综述，并点出了以往工作对推理过程本身的分析的缺失和不统一的评估方法。不过更多的作用是帮我分类了
    - 基础信息：
        - https://elifesciences.org/articles/106187
        - Unveiling the Reasoning Behaviour of Medical LLMs（医学 LLM 推理行为透视）
        - 2025 年 10 月 27 日
    - 评估了哪些模型：
        - 无
    - 评估了哪些工作流：
        - 无
    - 提出了评估方法：评估推理过程本身而非结果
        - 评估方向：
            - 推理过程（Process）：模型如何分解问题、得出中间步骤。
            - 推理结果（Outcome）：最终得出的结论。
            - 推理行为（Behavior）：具体的逻辑流，即"过程驱动而非结果驱动"。
        - 特色 trick
            - 现有医学 LLM 推理的四大评估范式
                - 结论导向评估（Conclusion-Based）：只看最终答案对不对。
                - 推理迹象评估（Rationale-Based）：审查推理过程的逻辑有效性。
                - 交互式评估（Interactive）：动态调整问题，深入探索模型推理深度（如 SDBench）。
                - 机制评估（Mechanistic）：挖掘低层级推理机制（特征归因、XAI）。
        - 工作流相关：
            - 提示工程
                - Chain-of-Thought (CoT)：鼓励模型逐步分解问题，产生中间推理步骤。改进但仍可能产生错误步骤。
                - Tree-of-Thought (ToT)：扩展 CoT，允许模型探索多个推理路径，通过启发式评估和搜索算法（BFS/DFS）导航树结构。适合复杂生物医学任务（如鉴别诊断、临床规划）。
                - Few-shot 学习：通过输入提示示例，让模型从最小数据中学习并快速适应。对数据稀缺的医学领域有用。
            - Agent 方法
                - 迭代规划（Iterative Planning）：将复杂临床问题分解为子问题，逐步分析，根据新信息动态调整。
                - 记忆集成（Memory Integration）：维护短期和长期记忆，跟踪患者历史、先前操作、演变中的诊断假设。
                - 工具增强（Tool Augmentation）：与 EHR、药物数据库、医学知识图谱、医学计算器、文献搜索引擎交互。
                - 反思（Reflection）：反馈机制和反思性决策，动态修改和改进推理，减少幻觉。
                - 多智能体协作（Multi-Agent）：部署多个专门化的 LLM agent（如疗效、安全、诊断 agent），通过结构化对话或论证合作分析。
            - 模型训练
                - 监督微调（SFT）：在带标签的推理数据集上训练，学习任务特定逻辑。
                - 强化学习来自人类反馈（RLHF）：基于人类偏好训练奖励模型，通过 PPO/DPO/GRPO 等算法优化策略，产生更人类一致的推理。
                - 大规模推理模型（LRMs）：专门训练用于执行延长推理（如 OpenAI o1、Huatuo GPT-o1、MedR、MedVLM-R1）。注意：MedR1 研究发现 GRPO 训练的模型在不输出中间推理迹象时比输出时性能更好，挑战了"更多推理总是更好"的假设。
            - 推理类型：
                - 演绎推理（Deductive）：从前提出发推导一般结论。医学 LLM 中最常见。
                - 溯因推理（Abductive）：从观察出发生成假设。LLM 在多选题上表现好，但从零生成假设能力弱（临床应用有限）。
                - 归纳法（Inductive）：根据具体观察结果推断一般原则。
                - 因果推理（Causal/Counterfactual）：连接症状与潜在条件的因果关系。某些模型（如 GPT-4）能推断因果方向。
                - 神经符号推理（Neuro-Symbolic）：整合神经网络（统计学习）与符号推理（形式逻辑、规则），提高可解释性、减少幻觉。
        - 评估维度：
            - 结论导向
                - 最终答案评估：Accuracy（USMLE/MedQA 等）、F1、Precision、Recall	
                - 遗漏推理过程，无法理解模型如何出错
            - 推理迹象
                - 推理过程/链评估：手工评估（医生标注、逻辑谬误识别）；半自动（CLEVER/R-IDEA 临床验证量表）；自动化（BLEU/METEOR/BERTScore 对比标准推理；LLM 评判；有向无环图 DAG 因果验证）
                - 手工评估耗时；自动指标与实际临床质量不完美相关
            - 交互式
                - 动态推理深度：诊断精准率、测试成本效益（如 SDBench：每例诊断总成本）；医生 vs 模型对标
                - 不可重现性、标准化难度高（基于对话反馈）
            - 机制
                - 低层推理操作：特征归因分数；可解释 AI（XAI）方法
                - 需专业工具，难以应用到开放生成任务




# prompt 设计的 source
- prompt 技术列表
    - zero-shot
    - few-shot
    - 知识生成
        - 列出 3–6 条你认为最重要的临床问题，包含相关的疾病 / 机制中的知识关键点
    - Meta prompting/结构化输出
    - CoT
        - 线索获取
            - **关键信息摘要**：problem representation
        - 假设生成
            - **问题列表**：Problem List"（标准医学做法），或者说是【知识生成】
            - **鉴别诊断列表**：具体诊断
        - 线索解释
            - **证据分析**：支持 vs 反对每个诊断，这是"基于证据的医学"的基础。或者说是
        - 假设评估
            - **进一步检查建议**：临床实践中必须的 next step。
            - **工作诊断 + 解释**：最终结论与理由。
    - self-refine
        - 批判反思并修改

    - Prompt Chaining（子任务分解）
        - 就是正常的多 agent 工作流，因为每个 agent 有不同的任务（prompt）且上下文是一次一次传递下去的，所以叫 prompt chaining
    - 多路径生成
        - 生成多份答案并对比/挑选/整合
        - Self-consistency / Multi-agent debate / adjudication
    - ToT
        - 高级 CoT，把 CoT 每步都分叉和打分，打出来的分用作剪枝和挑选最终方案
        - 剪枝策略要代码设置（比如如果这条支的分数低过40%就剪掉）

    - function tool
        - 搜索
        - dynamic 生成
    - ReAct
    - 交互式
        - 让 LLM 决定要不要问问题

    - 多模态
    - PAL (Program-Aided Language Models)
    - Reflection
        - 拥有记忆的 self-refine
    - Directional Stimulus Prompting (DSP)
        - 额外引入一个小模型用于生成关键字，引导大模型生成内容
    - Automatic Reasoning and Tool-use (ART)
        - 提供领域特化的 few-shot 示例和工具让 AI 选择，这些示例是 ReAct 特化的
        - 所以大概率不会用在通用模型上，因为任务可以是任意领域的，只有局限在某一个领域才能人为设计示例和工具给 AI 用
        - 假设了任务分布比较稳定
    - 可以抽象为‘直接通过 LLM 的表现动态增加日后的静态参考的技巧’，是为在工作流早期或者心跳执行的技巧
        - Automatic Prompt Engineer (APE)
            - 用多路径生成来制作 prompt
            - 假设了任务分布比较稳定
            - 让 AI 自己设计 prompt 和示例，用于后续长期使用？
        - Active Prompt
            - 和 LLM 协作，制造质量更高的 few-shot 示例集
            - LLM 负责生成大量问题的答案，然后用 judger 打分，挑选出值得人类标注的问题，标注完后加入 few-shot 示例中静态供 LLM 参考
            - 关键在于 逐步扩充“最有信息量”的示例集。

- 相关 source
    - https://arxiv.org/pdf/2407.13301
        - COT 、 self-refine 、 交互式角色扮演（含扮演病人的 agent 的 prompt） 、 LLM-as-judge 的 prompt
    - https://arxiv.org/pdf/2408.12496
        - 交互式角色扮演（含扮演病人的 agent 的 prompt 和 询问检查结果 的 prompt）, self-consistency, 多模态, 格式化输出
    - https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-64769-1/MediaObjects/41467_2025_64769_MOESM1_ESM.pdf
        - CoT, 格式化输出，交互式角色扮演（含扮演病人的 agent 的 prompt） , LLM-as-judge 的 prompt





"请严格按以下结构输出你的最终回答："
"1. 关键信息摘要【线索解释+问题表示】：用 2–4 句话总结患者的主要症状、体征和关键检查结果。"
"2. 问题信息生成【线索解释+问题表示】：列出 3–6 条你认为最相关和重要的临床问题，请包含相关的疾病 / 机制的知识关键点。"
"3. 鉴别诊断列表【假设生成】：列出 3–5 个可能诊断，按危重程度从高到低排序。"
"4. 证据分析【假设评估】：对每个可能诊断，分别列出“支持该诊断的依据”和“不支持或反对该诊断的依据”。"
"5. 进一步检查建议【假设评估】：列出 2–5 项你认为应当进行的进一步检查，并说明每一项检查希望回答的关键临床问题。"
"6. 初步工作诊断：给出你认为最可能的诊断，并用 3–5 句话解释理由。"


你是一名受过严格训练的 **临床推理助手**，为医生和研究人员提供病例分析支持。你的任务是在不访问外部网络的前提下，基于给定信息完成严谨的临床推理工作流。
必须遵守以下原则：
1. **角色与边界**  
   - 你不是患者的主诊医生，不能作出最终医疗决策或处方。
   - 你的输出仅用于辅助专业人员思考，不能替代面对面的临床评估。
   - 当信息不足或存在重大不确定性时，必须明确指出“不确定”“需要更多信息”。
2. **安全与合规**  
   - 所有回答必须基于病例提供的信息和通用医学知识，不得编造检查结果或病史。
   - 对于存在重大风险的诊断（如心梗、肺栓塞、脑卒中等），即使概率较低，也应明确列出并用 “don’t miss” 或类似标注强调。  
   - 不提供药品剂量、具体处方或个体化治疗方案。
   - 不对紧急或危及生命的情况给出“在家处理”建议，必须提醒尽快就医或联系急救系统。  
   - 避免对特定医生或机构作出评价。
3. **输出格式约定（供上层工作流消费）**  
   - 上层系统可能要求你以特定 JSON / Markdown 结构输出。
   - 当明确要求结构化输出时，严格遵守字段名和层级，不要添加多余字段。
   - 若无特殊说明，优先使用清晰的 Markdown 标题和小段落，保持可读性。

给定以下病例信息，请给出初步诊断意见。
病例信息：
{{CASE}}


"请严格按以下结构输出你的最终回答："
- 对于每个病例，请严格遵循以下顺序进行思考和回答：
    1. 关键信息摘要（Problem Representation）
        - 用 2–4 句话概括该病例的核心特征（年龄、性别、主要症状、时间进程、关键体征/实验室）。  
    2. **问题列表（Problem List）**  
        - 列出 3–6 条你认为最相关和重要的临床问题（症状、体征、异常检查、合并的重大慢病等）。
        - 附上每个临床问题的相关疾病/机制的知识关键点
    3. **鉴别诊断列表（Differential Diagnosis, DDx）**  
        - 列出 3–5 个可能诊断，并给出一个按“危险性 + 可能性”排序的诊断列表。用简短说明标注每个诊断的思路。
    4. **证据分析（Evidence For / Against）**  
        - 对列表中的每个候选诊断，分别写出：
            - 支持证据：病例中支持该诊断的要点；
            - 反对或不足证据：病例中缺失或不支持该诊断的要点。
    5. **进一步检查与管理建议（Next Steps）**  
        - 在不越界给具体处方的前提下，列出 2–5 项你认为应当进行的下一步的检查/评估方向，并说明 **“每项检查希望回答的关键临床问题”**。  
    6. **工作诊断与解释（Working Diagnosis）**  
        - 在承认不确定性的前提下，给出当前最合理的工作诊断（可以是一个或少数几个）并简要解释理由。
    - 使用**显性推理**：写出你的思考逻辑，而不是只给结论。

若输入信息极少或质量很差，你必须先说明“信息不足以进行可靠的临床推理”，然后指出还需要哪些关键补充信息。







# benchmark 的 source
- 对 DDx 的评估
    - 基础信息：
        - https://www.nature.com/articles/s41586-025-08869-4
        - Towards accurate differential diagnosis with large language models
        - 09 April 2025
    - 这篇工作评估的是 AMIE 这个专门针对 DDx 优化的 LLM，在 NEJM CPC 等复杂病例上的表现。 评估分为两块：
        - 模型单独生成 DDx 的能力（standalone）；
        - 模型作为医生助手时，对医生 DDx 质量的提升。
    - 关键有三类指标：Top‑N 准确率、质量/适当性/全面性评分、自动 vs 人工评估对照。
    - 实验在专门训练出来的模型上
- 综述，但主要用途在于把全部有代表性的评估指标全部列了出来
    - 基础信息：
        - Large language models for disease diagnosis: a scoping review（2025，NIH PMC）
        - 2025 Jun 9
        - https://pmc.ncbi.nlm.nih.gov/articles/PMC12216946/#Sec1
    - 在 Evaluation methods 小节中，总结不同诊断研究常用的指标：
        - 诊断准确率（Top‑1, Top‑k）；
        - AUC、敏感度、特异度（尤其在分类/风险预测场景）；
        - 与人类医生或 guideline 的一致性；
        - 某些工作中对解释质量 / 可信度的评估。
    - 列出来的所有评估指标
        - https://pmc.ncbi.nlm.nih.gov/articles/PMC12216946/table/Tab2/ 
- 推理过程自动化评分系统
    - 基础信息：
        - https://www.nature.com/articles/s41467-025-64769-1#Sec22
        - Quantifying the reasoning abilities of LLMs on clinical cases
        - 2025 年 11 月
    - 评估了哪些模型：
        - 主要是推理用的模型
    - 评估了哪些工作流：
        - zero-shot（无上下文）
        - one-shot（展示一个例子）
        - few-shot
        - oracle（给定所有需要的上下文。测试上限用的）
    - 提出了评估方法：MedR-Bench
        - 评估方向：
            - 检查建议（Examination Recommendation）：评估模型在信息不完整情况下推荐相关检查的能力；
            - 诊断决策（Diagnostic Decision-Making）；
            - 治疗规划（Treatment Planning）。
        - 特色 trick
            - 用 LLM 扮演患者
            - 自动化评分系统：用一个 LLM judger 和网络搜索来给 result 打分
        - 评估维度：
            - Reasoning 步骤评估: 
                - Efficiency（效率）	有效推理步骤占总步骤的比例
                - Factuality（准确性）	符合医学指南/知识的有效步骤占比
                - Completeness（完整性）	模型输出覆盖的"金标准推理步骤"占比
            - 结果评估：
                - Accuracy（准确性）    最终答案与金标准的匹配度
                - Precision/Recall（精准率/召回率） 用于检查建议列表（与医嘱对比）
        - 评估方法
            - LLM-as-judge 。小规模人工验证过 LLM-as-judge 的表现
    - 评估的数据集
        - MedR-Bench 数据集  https://github.com/MAGIC-AI4Med/MedRBench
    - 提供的资料：https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-64769-1/MediaObjects/41467_2025_64769_MOESM1_ESM.pdf
        - 有 prompt 提供
- 数据集
    - pubmed（短答题



# super source
- 基本信息：
    - https://arxiv.org/pdf/2505.12371
    - 18 May 2025
    - MedAgentBoard: Benchmarking Multi-Agent Collaboration with Conventional Methods for Diverse Medical Tasks
- 主要工作
    - 主要工作：对比了很多种 workflow ，并且也对比了 4 种




# report draft
- 终极目的：
    - 描述我的整个项目与计划
- 格式要求
    - 尽量学术风
    - 20页以内
    - 遵循以下结构：
        - introduction
        - background/motivation
        - implementation details
        - discussion
        - conclusion

- Introduction
- Background:
    - Engineering Perspective:
        - what I plan to do
            - 一个完整的可拓展的工作流编制框架
                1. 分层与原子化
                2. 轻量，medical-first
            - 完整的产品
                1. UI 页面方便使用
                2. 即用的 default config set （包括 prompt，工作流，成本，表现）
        - why do this
            1. Light-weight orchestration platform for high-flexibility
                - 通用 LLM orchestration 框架（LangGraph / Flowise / Orion 等）
                    - 优点：抽象能力强，节点/状态/多 agent 都支持。
                    - 局限：
                        - 对医疗人来说“过重”：要先学一层 DSL / 图结构，才能开始实验工作流；
                        - 完全 领域无关，不内置任何“临床推理步骤”概念；
                        - 不提供 “开放式临床诊断/推理”临床概念驱动的、轻量可配置的 workflow 模板或实践经验；
            2. 为 medical 场景提供实际的工程实践，包括分析 cost, performance, task 的平衡，提供好用的，针对不同 task 的 prompt 和工作流实践
                - 医疗 LLM 工作流论文（clinical decision workflow / patient‑friendly report / MedChain） 
                    - 优点：说明了 LLM 工作流在医疗中的可行性。
                    - 局限：
                        - 每篇都针对 特定任务（分诊/转诊、报告生成、工具调用），没有抽象成通用的 orchestration 平台；
                        - 工作流多为“单步 RAG”或“简单多步 pipeline”，很少对比更多的 workflow 优化方法
                        - 几乎没有系统比较“不同 workflow 对 cost / latency 的影响” 并量化 cost / 性能 / 质量权衡，通常只给出一条最佳 quality pipeline。
                - 现有的 medical reasoning 产品
                    - 像 OpenEvidence 是闭源+黑盒微调，只对外暴露“证据检索 +汇总”这一层优化；（https://journals.sagepub.com/doi/10.1177/21501319251332215）
                    - 像 Autonomous AI Agent 和 MedChain，重点在 多工具集成，而非工作流（https://arxiv.org/html/2404.04667v1）（https://openreview.net/forum?id=YvuufwkFJY）
            - 你的工作提供：
                - 基于现有通用 orchestration 思想，但做成 更轻、更 opinionated 的 medical‑first 层；
                - 内置可复用、可组合的诊断推理工作流模板，直接对齐临床推理文献（problem representation、problem list、DDx 等）；
                - 同时保持实现层简单（不需要学习复杂 DSL / 图 API 就能上手配置和实验）。
                - 你的贡献是在同一个统一框架里，把“临床推理步骤 + LLM 工程优化 + 成本分析”打通，并且让别人能直接拿来改和复现。
        - How do I do
            - 分层设计：
                - 应用层（UI）
                    - 提供工作面板来低代码建立想要的工作流
                    - 提供一些成体系的配置方案
                - 逻辑层
                    - task
                        - 原子化的，内聚的工作流任务，能够随意组合
                        - 工作
                            - 储存 meta data ，包括任务种类、任务设置、chatbot 设置等
                            - 与 context_manager 交互获得应有的上下文，同时把自己的输出储存到其中
                            - 与 prompt_manager 交互获得应有的 prompt
                            - 调用 api 封装方法来进行问答
                        - CoT + self-refine 的 eg
                            ```
                            TODO，请给这里留空
                            ```
                    - workflow
                        - 储存 task 和整份工作流的容器
                        - 负责储存 meta data 和启动整个 task graph
                    - prompt_manager
                        - 管理不同 task 的 prompt 的管理器，因为 task 种类很多所以需要这么一个管理器辅助
                    - context_manager
                        - 管理不同 task 的 prompt 的管理器，因为 task 种类很多所以需要这么一个管理器辅助
                - API 层（访问外部模型 API）
                    - 封装好各种访问协议和格式，供简易访问
            - LLM 挑选
                - 关注通用 LLM
                - 先对 闭源商用通用模型 进行评估，在对 闭源商用推理模型 进行评估
                - 最后看看要不要搞一搞开源模型
                - 我们会使用 Poe 这个 chatbot 统合平台的 API 进行统一的访问，后续再拓展到直接对接对于服务上
	- Academic Perspective
        - what I plan to do
            - 分析临床步骤来设计 prompt 和 工作流
            - 实践、评估不同的工作流优化方法
            - 分析现有 paper 来设计 benchmark 供横向评估工作流优化方法
		- Why do this（可能有些偏离方向，不用提及太多）
            - 现有研究 no complete analysis on different workflow under same benchmark
        - How do I do:
            - 有三种临床工作（https://elifesciences.org/articles/106187）
                1. 诊断决策（Diagnostic Decision-Making）；
                    - 这个就是核心工作
                2. 检查建议（Examination Recommendation）：评估模型在信息不完整情况下推荐相关检查的能力；
                    - 这个可以做，当作其中一个 section 的工作，下一个 stage 再做
                3. 治疗规划（Treatment Planning）。
                    - 这个很危险，paper 也说效果不佳，下一个 stage 再做
                - 还有一个医疗方向的工作：医疗工作自然语言化
                    - 不搞，因为不会搞，需要非常专业的医疗知识
                        - MedAgentGym (https://arxiv.org/abs/2506.04405)
                            - EHR 表格查询（MIMIC-III、eICU、TREQS 等）；
                            - 医学计算（MedCalcBench）；
                            - EHR 驱动的临床预测；
                            - 生物信息学 code（BioCoder）；
                            - 生物医学数据分析和 biostat；
                            - 机器学习建模（EHRSHOT, MIMIC-Extract 等）
            - 分析临床步骤
                - 大体框架（https://pmc.ncbi.nlm.nih.gov/articles/PMC5611427/#sec1-2）
                    - 线索获取
                    - 线索解释/问题表示（https://pmc.ncbi.nlm.nih.gov/articles/PMC5834975/）
                    - 假设生成
                        - DDx
                    - 假设评估
            - prompt 和 工作流 设计（https://elifesciences.org/articles/106187）（https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-64769-1/MediaObjects/41467_2025_64769_MOESM1_ESM.pdf）（https://arxiv.org/pdf/2408.12496）（https://arxiv.org/pdf/2407.13301）
                - stage 1，现在已经搞好了的：
                    - zero-shot （system prompt）
                        - prompt:
                            ```markdown
                            你是一名受过严格训练的 **临床推理助手**，为医生和研究人员提供病例分析支持。你的任务是在不访问外部网络的前提下，基于给定信息完成严谨的临床推理工作流。
                            必须遵守以下原则：
                            1. **角色与边界**  
                            - 你不是患者的主诊医生，不能作出最终医疗决策或处方。
                            - 你的输出仅用于辅助专业人员思考，不能替代面对面的临床评估。
                            - 当信息不足或存在重大不确定性时，必须明确指出“不确定”“需要更多信息”。
                            1. **安全与合规**  
                            - 所有回答必须基于病例提供的信息和通用医学知识，不得编造检查结果或病史。
                            - 对于存在重大风险的诊断（如心梗、肺栓塞、脑卒中等），即使概率较低，也应明确列出并用 “don’t miss” 或类似标注强调。  
                            - 不提供药品剂量、具体处方或个体化治疗方案。
                            - 不对紧急或危及生命的情况给出“在家处理”建议，必须提醒尽快就医或联系急救系统。  
                            - 避免对特定医生或机构作出评价。
                            1. **输出格式约定（供上层工作流消费）**  
                            - 上层系统可能要求你以特定 JSON / Markdown 结构输出。
                            - 当明确要求结构化输出时，严格遵守字段名和层级，不要添加多余字段。
                            - 若无特殊说明，优先使用清晰的 Markdown 标题和小段落，保持可读性。
                            ```
                    - few-shot
                        - 由于没有医生帮忙按照我们的 benchmark 回答问题，这个暂且忽略，后续可能可以用基于 self-consistency 的 LLM-as-judge 来生成 few-shot example
                    - Meta prompting + CoT + 知识生成
                        - prompt:
                            ```markdown
                            请严格按以下结构输出你的最终回答：
                            - 对于每个病例，请严格遵循以下顺序进行思考和回答：
                                1. 关键信息摘要
                                    - 用 2–4 句话概括该病例的核心特征（年龄、性别、主要症状、时间进程、关键体征/实验室）。  
                                2. 问题列表
                                    - 列出 3–6 条你认为最相关和重要的临床问题（症状、体征、异常检查、合并的重大慢病等）。
                                    - 附上每个临床问题的相关疾病/机制的知识关键点
                                3. 鉴别诊断列表
                                    - 列出 3–5 个可能诊断，并给出一个按“危险性 + 可能性”排序的诊断列表。用简短说明标注每个诊断的思路。
                                4. 证据分析
                                    - 对列表中的每个候选诊断，分别写出：
                                        - 支持证据：病例中支持该诊断的要点；
                                        - 反对或不足证据：病例中缺失或不支持该诊断的要点。
                                5. 进一步检查与管理建议
                                    - 在不越界给具体处方的前提下，列出 2–5 项你认为应当进行的下一步的检查/评估方向，并说明 **“每项检查希望回答的关键临床问题”**。  
                                6. 工作诊断与解释
                                    - 在承认不确定性的前提下，给出当前最合理的工作诊断（可以是一个或少数几个）并简要解释理由。
                                - 使用**显性推理**：写出你的思考逻辑，而不是只给结论。

                            若输入信息极少或质量很差，你必须先说明“信息不足以进行可靠的临床推理”，然后指出还需要哪些关键补充信息。
                            ```
                    - self-refine
                        - prompt:
                            ```
                            "你现在的角色是一名经验丰富的上级医生，你的任务是严格审查一名住院医生写的病例诊断思路与结论。"
                            "请特别关注：是否遗漏危重诊断、是否有与病史/体征矛盾的推理、是否出现过度自信或危险建议。"
                            "请审查并批评以下对病例信息的回答"
                            "病例信息："
                            "{{CASE}}"
                            "住院医生的诊断："
                            "{{INITIAL_ANSWER}}"
                            ```
                - stage 2，搞更复杂的工作流
                    - Prompt Chaining，多路径，ToT
                    - function tool，ReAct（搜索引擎事实验证，有一篇 paper 就这么干的），交互式
                - stage 3 探索更高级的技巧（yes 代表可能会去探索，no 代表不会去探索）
                    - 多模态
                        - 【yes】
                    - Automatic Reasoning and Tool-use (ART)
                        - 提供领域特化的 few-shot 示例和工具让 AI 选择，这些示例是 ReAct 特化的
                        - 假设了任务分布比较稳定，所以大概率不会用在通用模型上，只有局限在某一个领域才能人为设计示例和工具给 AI 用
                        - 【yes】
                    - 上下文管理
                        - Reflection：拥有记忆的 self-refine
                        - 【yes】
                    - PAL (Program-Aided Language Models)
                        - 【no，医学里设计代码的东西学习成本太高了】
                    - 额外的模型
                        - Directional Stimulus Prompting (DSP)：额外引入一个小模型用于生成关键字，引导大模型生成内容
                        - 【no，我们的目标是不涉及模型训练来提升质量】
                    - 可以抽象为‘直接通过 LLM 的表现动态增加日后的静态参考的技巧’，是可以在工作流早期或者心跳执行的技巧
                        - Automatic Prompt Engineer (APE)
                            - 用多路径生成来制作 prompt
                            - 假设了任务分布比较稳定
                            - 让 AI 自己设计 prompt 和示例，用于后续长期使用？
                            - 【yes，但优先级较低】
                        - Active Prompt
                            - 和 LLM 协作，制造质量更高的 few-shot 示例集
                            - LLM 负责生成大量问题的答案，然后用 judger 打分，挑选出值得人类标注的问题，标注完后加入 few-shot 示例中静态供 LLM 参考
                            - 关键在于 逐步扩充“最有信息量”的示例集。
                            - 【yes，但优先级较低】

            - benchmark 设计供横向评估工程实践（https://www.nature.com/articles/s41586-025-08869-4）（https://pmc.ncbi.nlm.nih.gov/articles/PMC12216946/）（https://www.nature.com/articles/s41467-025-64769-1）（https://pmc.ncbi.nlm.nih.gov/articles/PMC11590327/#Sec3）
                - 推理迹象评估（Rationale-Based）：审查推理过程的逻辑有效性。
                    - Conciseness/Efficiency（相关性/准确性/效率）：所输出内容是否足够简洁有效（最后用于输出的有效内容的比例），是否有信息增量，还是说有很多冗余内容
                    - Factuality（真实性）：符合医学指南/知识的有效步骤占比
                    - Completeness（完整性）：模型输出覆盖的"金标准推理步骤"占比
                - 结论导向评估（Conclusion-Based）：只看最终答案对不对。
                    - Accuracy（准确性）：最终答案与金标准的匹配度
                        - DDx 的 Top-1 和 Top-N
                        - Appropriateness：评估 DDx 中每个诊断是否**“合理地适合这个病例”**：
                        - Comprehensiveness：评估 DDx 是否**“足够全面”**：
                    - Precision/Recall（精准率/召回率）：用于检查建议列表（与医嘱对比）
                    - sensitivity：是否出现过度自信或危险建议
            - 评估方法
                - 选择/填空题/字符串匹配 自动化评估，得出初步结果供工作流早期对比‘剪枝’，防止工作流排列组合成本爆炸
                - LLM-as-judge 进行更抽象的评估
                    - 使用 基于数据集的 多路径生成 结果来当成上限，使用 zero-shot 当成下限
                - paper 中出现过的 trick
                    - NOTA
            - benchmark 数据集
                - MedQA 有医学知识的 QA 问答，用于得出初步结果供工作流早期对比‘剪枝’，防止工作流排列组合成本爆炸（https://github.com/jind11/MedQA）
                - PubMed 有医学知识的短答题，得出初步结果供工作流早期对比‘剪枝’，防止工作流排列组合成本爆炸（https://github.com/pubmedqa/pubmedqa）
                - MedRBench 有完整 诊断 和 设计治疗方案 的问题，供全面的评估（https://github.com/MAGIC-AI4Med/MedRBench）
                - 由于数据集较大，我们仅会抽取其中一部分进行评估


- Supervisor:
    - Prof. Cheng Chen
- second examiner:
    - Prof. Edith Ngai
    - chngai@eee.hku.hk
- Moderator: 
    - Prof. Kevin Tsia
    - tsia@eee.hku.hk





- 核心内容：
    - 临床概念建模 （problem representation, DDx 等）；
    - 医疗任务模板和 workflow 配方；
    - 质量–成本评估和经验总结；
    - 给未来真正的医院产品团队提供“可拷贝的工程 best practices”。


- 搜索、复现、统合、提供科研功能
    1. 找几个有代表性的工作进行建模
    2. 提炼出多个节点，结合工作流进行开发

    - 有代表性的医学工作
        - Medical Reasoning
            - 摘要
            - problem list
            - DDx
            - evidence
            - refine check
            - 讨论组
        - 医疗文书报告（stage 2：实际用途）
            - 
    - 提供 benchmark 框架和可视化面板
        - Medical Reasoning
            - 指标的节点
        - Meta
            - LLM-as-judge 的节点
        - 可视化
            - 可视化节点

    - 全程的 intermediate step 的记录与评估？