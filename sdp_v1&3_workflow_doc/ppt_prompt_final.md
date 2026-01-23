
## Introduction & motivation
**核心信息**（用保守、可验证的文字）：
- 📚 **背景**：LLM 工作流这个主题在过去数年已经积累了相当多学术工作和开源代码贡献，医学推理亦然
- 🔍 **观察**：然而即便在现有代码，乃至开源工具如此丰富的情况下，公开代码的现有工作仍然多采用"为特定论文而编写的定制代码"模式，即使许多任务（如 LLM API 调用、工作流编排、Prompt 设计）存在高度重复。

**为什么不用现有成果？**
- 通用平台 vs 医学研究者需求：
    - 存在很多给技术人员而非医学人员设计的功能，带来了额外的认知负担
        - 例子：加载 benchmark 的题目并运行
            - 医学研究者关心的是：
                - 题目怎么集成到工作流的一部分（例如集成到 prompt 中）
            - 但通用平台还需要关系：
                - 题目怎么储存（csv文件？blob文件？json文件？）
                - 题目怎么访问（数据协议，设定列与行与工作流的关系）
    - 缺乏 benchmark 功能
        - 没有直接的跑 benchmark 的功能
        - 间接的方法：Dify 发布工作流以拥有批量处理功能
    - 通用工作流平台（Dify/Flowise/LangGraph）为了覆盖所有应用场景，不得不在代码、概念、功能上设计得非常全面。但这对**医学推理工作流研究**这个特定领域来说，引入了不必要的复杂度。
- 学术工作 vs 医学研究者需求
    - 大部分是任务特化的 script，通用性不足，无法复用
    - 泛化的 script 价值很高，但也需要学习使用方法和部署，在小规模任务上不值得
**如何解决？**
- **轻量级医学 Workflow 编制与评估框架**——通过医学语义化设计与刻意的功能聚焦，降低复现与迭代医学推理工作流的门槛。
    - 参考现有的大量医学学术工作与相关工程工作，将他们整合为一个统一的特化平台
        - 三个核心目标：
            1. **支持快速切换与编制不同工作流**
            - 内置相关论文已验证的工作流模板（如 CoT、多 Agent、Self-Refine）
            - 提供医学语义节点（线索表达、假设生成、假设评估等）
            - 用户可快速组合不同工作流，而不需过多理解底层技术细节

            1. **支持快速应用各种医学 Benchmark**
            - 集成常见医学 Benchmark（MedQA、PubMedQA、MedRBench 等）
            - 用户只需选择数据集，系统自动处理数据适配
            - 一键运行评估，自动生成对比可视化

            1. **简化与抽象，降低配置复杂度**
            - 去除非必要的技术概念（如数据存储协议、发布形态等）
            - 用直观的语言替代技术术语

## Methods
1) 三套功能体系（Prompt / Component / Recipe）
- Prompt 层：一键应用 Prompt 工程技巧
    - **Self-Refine**：嵌入在节点中，可一键开启/关闭迭代自我检查
    - **Chain-of-Thought**：提供 Prompt 模板，用户可快速设置逐步推理
    - **Self-Consistency**：预接线的节点模板，包含多个子 LLM + 聚合 LLM
- Component 层：医学语义节点库（来自现有论文提炼）
    - 基于对现有论文的分析，医学临床推理可分为三个核心步骤：
        1. **线索表达（Clue Representation）**
        - 目标：把自由文本或半结构化的医学信息（症状、体征、检查结果）转换为结构化的临床线索表示
        - 作用：为后续推理建立清晰、可追踪的信息基础
        - implementation：线索表达节点：把 Benchmark 输入（如题干、选项）结构化为可追踪的临床线索表示

        1. **假设生成（Hypothesis Generation / DDx）**
        - 目标：基于结构化线索，生成可能的诊断候选列表，包含支持与反对的证据
        - 作用：系统地探索诊断空间，避免过早收敛
        - implementation：假设生成节点：基于线索节点的 output，生成可能的诊断（DDx）与候选列表

        1. **假设评估（Hypothesis Evaluation）**
        - 目标：对候选诊断进行综合评估，排序，最终选出最可能的诊断
        - 作用：形成最终的、有理由支撑的诊断决策
        - implementation：假设评估节点：对假设生成的候选诊断进行评估、排序，最终选出最可能的诊断
- Recipe 层：预设工作流模板（可一键复现）
    1. **基础推理架构**：CoT 或单步诊断推理
    2. **多 Agent 架构**：三个独立 Agent 分别执行"线索表达 → 假设生成 → 假设评估"
    3. **过程推理评估架构**：包含推理过程的多维评估（不仅看结果，还看推理过程）

1) 一键 Benchmark 评估
- **功能**：
    - 用户选择 dataset（MedQA / PubMedQA / MedRBench 等）
    - 系统自动处理数据加载、格式转换、与工作流的接口适配
    - 运行评估后自动生成可视化结果图表
- **Benchmark 生态现状**
    **Dataset 层**：现有医学 LLM Benchmark 已有充分积累
        - **MedQA**：医学执照考试风格的多选题
        - **MedRBench**：医学推理基准，覆盖多类型推理任务
    - **Metrics 层**：评估维度已被系统分类
        - **Result-Based**：Accuracy、Appropriateness、Comprehensiveness、Sensitivity
        - **Process-Based**：Completeness、Factuality、Efficiency
    - extra：
        - MedHELM：全面的评估基准平台，包含了 dataset 和各种指标
**现状**：虽然 Dataset 与 Metrics 已被充分研究，但缺乏统一的平台把它们集成在一起供研究者快速对比不同工作流。
- eg：MedQA
    - 用户选择 MedQA，并选择要评估那些指标，以 accuracy 为例
    - 自动载入相关数据接口协议，提取并解析出题目
    - 把解析好的题目作为 prompt 的一部分自动导入工作流的初始输入
    - 让工作流规范其最终输出格式为 MedQA 的多选题格式
    - MedQA 根据规范的输出提取 LLM 的回答，调用可视化模块来计算 accuracy
    - 出图

1) 轻量化设计
- **去除的功能**（对医学工作流研究非必要）：
    - 第三方工具集成（市场、插件生态）
    - MCP Server、API 端点、SDK 生态
    - 多 App 类型、权限与发布形态
- **保留的核心能力**：工作流执行、数据流追踪、结果可视化、日志导出


## Current progress
- 核心可拓展代码已经完成，已经根据系统需求留下了大量接口，接下来填补所有功能和开发前端即可完成，没有什么大规模的开发任务需要处理
- MVP 展示现有代码能力
    - **任务定义**：
        - **输入**：MedQA 多选题（题干 + 4–5 个选项）
        - **输出**：最终选择（A/B/C/D/E）+ 推理过程 + 成本指标
        - 过程：三个临床推理节点 + 一个 self-refine
            - 题目 → [Agent1: 线索表达] → [Agent2: 假设生成] → [Agent3: 假设评估 + self-refine] → 最终答案
        - **核心指标**：准确度（与金标准的匹配）+ 工作流搭建/执行成本
    - **对比通用框架**（可验证、可测量）：
        | **维度** | **你的平台** | **Dify** | **差异意义** |
        |---------|-----------|---------|-----------|
        | **搭建步数（UI 交互）** | ~5–8 步 | ~15–20 步 | 医学语义节点减少了通用技术配置 |
        | **需掌握的概念数** | ~8–10 个 | ~20–25 个 | 无需理解数据存储、发布、API 等非必要概念 |

**数据来源说明**（待实测）：
- 步数与概念数：通过 UI 截图与文档逐项计数
- 时间：对同一任务重复 3 次，记录平均值与标准差
- 概念数：统计两个平台各自的官方文档中"必须理解"的核心概念

**表格下方结论**：
> *这不是说 Dify 不好——Dify 的通用性正是它的优势。但对**医学推理工作流研究**这个特定任务，我们通过医学语义化，有效降低了进入门槛与认知负担。*

***

## **第 8 页：Architecture Diagram（系统架构）**

**标题**：*Three-Layer Medical-First Architecture*

**可视化架构图**（推荐）：

```
┌─────────────────────────────────────────────────────────┐
│      Workflow Builder UI (Medical Semantic Layer)        │
│  • 拖拽医学节点（线索表达、假设生成、假设评估）          │
│  • 选择 Recipe（CoT、Multi-Agent、Self-Refine）        │
│  • 一键选择 Benchmark（MedQA、PubMedQA）               │
│  • 自动生成对比结果（Accuracy、Tokens、Time）          │
├─────────────────────────────────────────────────────────┤
│  Function / Component / Recipe Composition Layer        │
│  • Functions：Self-Refine、CoT、Self-Consistency       │
│  • Components：医学节点库（来自论文提炼）               │
│  • Recipes：预设工作流（可一键复现）                   │
├─────────────────────────────────────────────────────────┤
│  Execution Engine & Evaluation Module                   │
│  • Workflow Execution：节点执行、状态管理、数据流        │
│  • Benchmark Integration：Dataset Adapters、Metrics    │
│  • Run History & Tracing：成本数据、可视化              │
│  • Result Export：CSV、JSON、Charts                    │
├─────────────────────────────────────────────────────────┤
```

## Evaluation

**标题**：*How We Validate the Solution*

**三层验证**：

1. **工程成本对比（客观指标）（已经简单做了一个）**
   - 方法：实测同一任务（MedQA MVP）在你的平台与 Dify 上的成本
   - 指标：步数、概念数、时间、代码改写次数
   - 输出：对比表格与截图（可直观展示区别）

2. **医学用户反馈（定性）**
   - 方法：招募 3–5 名医学生/研究者，让他们用你的平台搭建一个工作流
   - 指标：操作难度、理解速度、是否需要手写代码、满意度
   - 输出：用户反馈总结

3. **可复现性验证**
   - 方法：用你的平台复现某篇现有论文的工作流（如某个 Medical Reasoning 论文）
   - 指标：是否能成功复现、需要改写多少、与原论文结果对齐度
   - 输出：复现报告 + 成本对比


## Discussion

**标题**：*What We Are NOT Claiming*

**明确声明**：
- ❌ **不是方法创新**：我们不提出新的医学推理算法
- ❌ **不是评估创新**：我们不设计新的医学评估指标（复用现有的）
- ❌ **不是通用平台竞争**：我们不试图取代 Dify/LangGraph

**我们 ARE 做的**：
- ✅ **系统工程贡献**：医学推理工作流的医学语义化、标准化、可复用化
- ✅ **领域专业化**：降低医学研究者的工程负担，缩短工作流设计-验证周期
- ✅ **可扩展基底**：为后续研究者提供清晰、灵活的扩展平台

**定位**：
> *这是一个 **Systems/Tools 类型的贡献**，价值在于 **standardization、accessibility、reproducibility**，而非 methods 或 algorithmic innovation。*


**代码可用性的承诺**：
- 我们深知平台永远无法满足所有需求，因此刻意保持代码的简洁性与模块化
- 去除硬编码的技术概念，最大化灵活度
- 提供清晰的扩展接口，让有额外需求的用户能快速拓展

## **第 13 页：Conclusion**

**收尾陈述**：
> 医学推理 LLM 研究已有充分的学术积累。但工程化与标准化的欠缺，仍然是阻碍广泛创新与复现的瓶颈。
> 我们提出一个**医学特化的 Workflow 框架**，通过医学语义化设计与刻意的功能聚焦，把医学研究者从"重复的工程工作"解放出来，让他们专注于**医学假设与工作流设计本身**。
> 这不是一个学术突破，但它有可能成为一个**有用的科研工具**，加速医学 LLM 这个领域的集体进步。






Here's the English translation of your final script, ready to copy into your PPT:

***

## Introduction & Motivation

**Core Message** (conservative, verifiable language):
- 📚 **Background**: LLM workflows as a topic have accumulated substantial academic work and open-source contributions over recent years, and so has medical reasoning
- 🔍 **Observation**: However, despite the richness of existing code and open-source tools, published work still predominantly follows a "custom code for a specific paper" pattern, even though many tasks (such as LLM API calls, workflow orchestration, prompt design) are highly repetitive

**Why Not Use Existing Solutions?**
- General platforms vs. medical researchers' needs:
    - Many features are designed for engineers rather than medical professionals, introducing unnecessary cognitive overhead
        - Example: Loading and running benchmark questions
            - What medical researchers care about:
                - How to integrate questions into the workflow (e.g., into prompts)
            - What general platforms require:
                - How to store questions (CSV file? Blob? JSON?)
                - How to access questions (data protocols, mapping columns and rows to workflow)
    - Lack of benchmark functionality
        - No direct benchmark-running capability
        - Workaround: Dify requires publishing workflows for batch processing
    - General workflow platforms (Dify/Flowise/LangGraph) must design comprehensively to cover all scenarios, introducing unnecessary complexity for medical reasoning workflow research
- Academic work vs. medical researchers' needs
    - Most are task-specific scripts with poor generalizability and limited reusability
    - Generalized scripts are valuable but require learning and deployment—not worth it for small-scale tasks

**How to Solve?**
- **Lightweight Medical Workflow Authoring & Evaluation Framework** — reduce the barrier to reproducing and iterating medical reasoning workflows through medical semantic design and deliberate functional focus
    - Integrate abundant existing medical academic work and related engineering work into a unified, specialized platform
        - Three core objectives:
            1. **Support rapid workflow switching and authoring**
            - Built-in workflow templates validated by existing papers (CoT, Multi-Agent, Self-Refine)
            - Provide medical semantic nodes (Clue Representation, Hypothesis Generation, Hypothesis Evaluation, etc.)
            - Users can rapidly compose different workflows without needing deep understanding of underlying technical details

            2. **Support rapid application of various medical benchmarks**
            - Integrate common medical benchmarks (MedQA, PubMedQA, MedRBench, etc.)
            - Users only select a dataset; the system automatically handles data adaptation
            - One-click evaluation with automatic comparison visualization

            3. **Simplify and abstract, reduce configuration complexity**
            - Remove non-essential technical concepts (data storage protocols, publishing forms, etc.)
            - Use intuitive language instead of technical jargon

***

## Methods

1) **Three-layer function system (Prompt / Component / Recipe)**
   - Prompt Layer: One-click application of prompt engineering techniques
       - **Self-Refine**: Embedded in nodes, can be toggled on/off for iterative self-checking
       - **Chain-of-Thought**: Provide prompt templates for rapid step-by-step reasoning setup
       - **Self-Consistency**: Pre-wired node templates with multiple sub-LLMs + aggregation LLM
   
   - Component Layer: Medical semantic node library (extracted from existing papers)
       - Based on analysis of existing papers, medical clinical reasoning divides into three core steps:
           1. **Clue Representation**
               - Goal: Convert free-text or semi-structured medical information (symptoms, signs, test results) into structured clinical clue representation
               - Role: Establish clear, traceable information foundation for subsequent reasoning
               - Implementation: Clue Representation node structures benchmark inputs (question stem, options) into traceable clinical clue representation
           
           2. **Hypothesis Generation / Differential Diagnosis (DDx)**
               - Goal: Based on structured clues, generate possible diagnostic candidates with supporting and opposing evidence
               - Role: Systematically explore diagnostic space, avoid premature convergence
               - Implementation: Hypothesis Generation node generates possible diagnoses and candidate lists based on Clue Representation node output
           
           3. **Hypothesis Evaluation**
               - Goal: Comprehensively evaluate, rank candidate diagnoses, and select the most likely one
               - Role: Form final diagnostic decisions with supporting rationale
               - Implementation: Hypothesis Evaluation node evaluates and ranks diagnostic candidates from Hypothesis Generation, selecting the most likely diagnosis
   
   - Recipe Layer: Pre-configured workflow templates (one-click replication)
       1. **Basic reasoning architecture**: CoT or single-step diagnostic reasoning
       2. **Multi-Agent architecture**: Three independent agents executing "Clue Representation → Hypothesis Generation → Hypothesis Evaluation"
       3. **Process-aware reasoning architecture**: Multi-dimensional evaluation of reasoning process (assess both results and reasoning steps)

2) **One-click benchmark evaluation**
   - **Functionality**:
       - User selects dataset (MedQA / PubMedQA / MedRBench, etc.)
       - System automatically handles data loading, format conversion, workflow interface adaptation
       - Automatically generates visualization charts after evaluation
   
   - **Benchmark ecosystem status**
       - **Dataset Layer**: Current medical LLM benchmarks are well-established
           - **MedQA**: Medical licensing exam-style multiple-choice questions
           - **MedRBench**: Medical reasoning benchmark covering multiple reasoning task types
       - **Metrics Layer**: Evaluation dimensions systematically categorized
           - **Result-Based**: Accuracy, Appropriateness, Comprehensiveness, Sensitivity
           - **Process-Based**: Completeness, Factuality, Efficiency
       - **Extra**:
           - **MedHELM**: Comprehensive evaluation benchmark platform with datasets and various metrics
       - **Current state**: While datasets and metrics are well-researched, a unified platform integrating them for quick workflow comparison is lacking
   
   - **Example: MedQA**
       - User selects MedQA and chooses metrics to evaluate (e.g., accuracy)
       - System automatically loads relevant data interface protocols, extracts and parses questions
       - Parsed questions are automatically integrated as part of prompts into initial workflow inputs
       - Workflow normalizes final output format to MedQA multiple-choice question format
       - Based on normalized outputs, the system extracts LLM answers and invokes visualization module to compute accuracy
       - Generate visualization

3) **Lightweight design**
   - **Removed features** (non-essential for medical workflow research):
       - Third-party tool integration (marketplaces, plugin ecosystems)
       - MCP Server, API endpoints, SDK ecosystems
       - Multiple app types, permission systems, publishing forms
   - **Retained core capabilities**: Workflow execution, data flow tracing, result visualization, log export

***

## Current Progress

- Core extensible codebase is complete, with numerous interfaces preserved based on system requirements. Remaining work is feature completion and frontend development—no major development tasks remain
- MVP demonstration of existing code capabilities
    - **Task Definition**:
        - **Input**: MedQA multiple-choice questions (question stem + 4–5 options)
        - **Output**: Final choice (A/B/C/D/E) + reasoning process + cost metrics
        - Process: Three clinical reasoning nodes + one self-refine
            - Question → [Agent1: Clue Representation] → [Agent2: Hypothesis Generation] → [Agent3: Hypothesis Evaluation + Self-Refine] → Final Answer
        - **Core Metrics**: Accuracy (match with gold standard) + workflow setup/execution cost
    - **Comparison with general framework** (verifiable, measurable):
        | **Dimension** | **Your Platform** | **Dify** | **Significance** |
        |---------|-----------|---------|-----------
        | **Setup Steps (UI interactions)** | ~5–8 steps | ~15–20 steps | Medical semantic nodes reduce generic technical configuration |
        | **Concepts to Master** | ~8–10 | ~20–25 | No need to understand data storage, publishing, APIs, etc. |

**Data source note** (to be verified):
- Steps and concept counts: counted via UI screenshots and documentation
- Time: repeated 3 times, recording mean and standard deviation
- Concept counts: statistics from official documentation of each platform on "must understand" core concepts

**Table conclusion**:
> *This is not to say Dify is bad—its generality is its strength. But for medical reasoning workflow research as a specific task, we effectively lower barriers and cognitive load through medical semanticization.*

***

## System Architecture Diagram

**Title**: *Three-Layer Medical-First Architecture*

**Visualization diagram** (recommended):

```
┌─────────────────────────────────────────────────────────┐
│      Workflow Builder UI (Medical Semantic Layer)        │
│  • Drag-and-drop medical nodes                           │
│  • Select Recipe (CoT, Multi-Agent, Self-Refine)        │
│  • One-click Benchmark selection (MedQA, PubMedQA)      │
│  • Auto-generate comparison results (Accuracy, Tokens)  │
├─────────────────────────────────────────────────────────┤
│  Function / Component / Recipe Composition Layer        │
│  • Functions: Self-Refine, CoT, Self-Consistency       │
│  • Components: Medical node library (paper-derived)     │
│  • Recipes: Pre-configured workflows (one-click replay) │
├─────────────────────────────────────────────────────────┤
│  Execution Engine & Evaluation Module                   │
│  • Workflow Execution: node execution, state mgmt       │
│  • Benchmark Integration: Dataset Adapters, Metrics    │
│  • Run History & Tracing: cost data, visualization      │
│  • Result Export: CSV, JSON, Charts                    │
└─────────────────────────────────────────────────────────┘
```

***

## Evaluation

**Title**: *How We Validate the Solution*

**Three-layer validation**:

1. **Engineering cost comparison** (objective metrics) [already did a simple version]
   - Method: Measure same task (MedQA MVP) cost on both platforms
   - Metrics: Steps, concept count, time, code rewrites
   - Output: Comparison table + screenshots

2. **Medical user feedback** (qualitative)
   - Method: Recruit 3–5 medical students/researchers to build workflows on our platform
   - Metrics: Operational difficulty, comprehension speed, need for hand-coding, satisfaction
   - Output: User feedback summary

3. **Reproducibility verification**
   - Method: Reproduce existing paper's workflow using our platform
   - Metrics: Success/failure, rewrite amount, result alignment with original paper
   - Output: Reproduction report + cost comparison

***

## Discussion

**Title**: *What We Are NOT Claiming*

**Clear statements**:
- ❌ **Not method innovation**: We don't propose new medical reasoning algorithms
- ❌ **Not evaluation innovation**: We don't design new medical evaluation metrics (reuse existing ones)
- ❌ **Not general platform competition**: We don't attempt to replace Dify/LangGraph

**What we ARE doing**:
- ✅ **Systems engineering contribution**: Medical semanticization, standardization, and reusability of medical reasoning workflows
- ✅ **Domain specialization**: Reduce engineering burden for medical researchers, shorten workflow design-validation cycles
- ✅ **Extensible foundation**: Provide clear, flexible extension platform for future researchers

**Positioning**:
> *This is a **Systems/Tools type contribution**, with value in **standardization, accessibility, reproducibility** rather than methods or algorithmic innovation.*

**Code usability commitment**:
- We understand the platform can never satisfy all needs, so we deliberately maintain code simplicity and modularity
- Remove hard-coded technical concepts, maximize flexibility
- Provide clear extension interfaces for users with additional needs to quickly extend

***

## Conclusion

**Closing statement**:
> Medical reasoning LLM research already has substantial academic foundation. But the lack of engineering standardization remains a bottleneck to broad innovation and reproducibility.
> 
> We propose a **medical-specialized workflow framework** that, through medical semantic design and deliberate functional focus, frees medical researchers from "repetitive engineering work" to focus on **medical hypotheses and workflow design itself**.
> 
> This is not an academic breakthrough, but it could become a **useful research tool** that accelerates collective progress in the medical LLM field.