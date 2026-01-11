# Medical-Centered Clinical Reasoning Workflow LLM Evaluation Platform

## Midterm Report for Graduation Thesis

---

## Abstract

Large language models demonstrate excellent performance on medical knowledge tasks (84-90% accuracy) but show significant decline on real clinical workflows (45-69% success rate) [1]. This "knowledge-practice gap" stems not only from model limitations but critically from the lack of evaluation infrastructure. Current evaluation approaches either require extensive programming knowledge or remain technology-centric, creating barriers for medical researchers.

This project proposes a **medical-centered lightweight LLM workflow platform** enabling medical researchers to design, configure, and execute LLM evaluations through medical language rather than code. The platform employs a three-layer architecture that progressively conceals technical complexity. The three layers are the medical concept layer (user interface), the evaluation framework layer (methodological transformation), and the data execution layer (infrastructure) respectively.

Core contributions include **(1) transforming clinical reasoning structures into configurable workflow components**, enabling medical researchers to describe evaluation tasks using clinical terminology rather than technical jargon; **(2) extracting and unifying multiple methodological paradigms from recent literature**, supporting flexible framework selection; **(3) reducing evaluation configuration complexity from 12 discrete steps in raw programming to 2 main steps**, significantly lowering cognitive load; and **(4) maintaining declarative, human-readable, and reproducible configuration properties**, supporting result verification and reuse.

The verification strategy encompasses three dimensions. These include technical correctness (reproducing published results), usability (whether target users can successfully use the platform), and scientific value (whether it supports new research). This report documents problem analysis, design principles, architectural details, and initial implementation progress, laying the foundation for subsequent development.

**Keywords**: large language models, clinical reasoning evaluation, medical workflow programming, evaluation platform, knowledge-practice gap

---

## 1. Background and Problem

### 1.1 Empirical Analysis of the Knowledge-Practice Gap

To understand the fundamental challenges facing medical LLM evaluation, this section first extracts data from recent systematic research to quantify the specific degree and manifestations of this "knowledge-practice gap."

Large language models demonstrate obvious bimodal performance in medical capability evaluation [1].

**Knowledge-type task performance** (medical licensing exam style) [1][2]
- USMLE-style questions achieve 84-90% accuracy 
- Factual knowledge retrieval achieves 85-93% accuracy

**Practice-type task performance** (simulating real clinical workflows) [1][3]
- Clinical reasoning achieves 50-60% accuracy
- Diagnostic decision-making achieves 45-55% accuracy 
- Clinical safety assessment achieves 40-50% accuracy

This gap has been verified across multiple large-scale benchmarks. MedAgentBench [4] evaluates AI performance on real tasks interacting with electronic health record systems, finding query tasks (information retrieval) achieve 85.33% success rate, while operation tasks (actual system intervention) only achieve 54.00%. Even more extreme is DiagnosisArena [5], a professional-level diagnostic reasoning benchmark containing complex, multi-system patient cases, where even the most advanced reasoning models achieve only 45.82% accuracy, far below standard LLM performance on multiple-choice questions.

### 1.2 Analysis of Problem Sources

To effectively address this gap, we must understand its root causes. Through analyzing existing medical AI research, we can identify three core dimensions of difference.

**First dimension of fundamental differences in cognitive complexity**

Exam evaluation tests "knowledge application" where the correct answer is selected within a given choice framework. Clinical practice requires "knowledge generation", which means synthesizing possible diagnostic hypotheses from open-ended patient information, prioritizing them, and designing complete diagnostic workflows. These two cognitive tasks differ completely in difficulty and required skills.

**Second dimension of differences in information management complexity**

Exam cases provide complete, carefully designed information. Real clinical data arrive asynchronously, contain inconsistencies, and are frequently incomplete, requiring physicians to dynamically collect information and adjust problems. MedChain [6] clearly verifies this through designing a dataset containing 12,163 real clinical cases. Its dataset emphasizes three characteristics (personalization, interactivity, sequentiality), with model performance improving approximately 25% compared to baseline.

**Third dimension of differences in medical safety and uncertainty requirements**

Medical practice requires defensive reasoning. Even when preliminary diagnosis seems obvious, one must consider "cannot miss" dangerous diagnoses such as myocardial infarction and stroke. LLMs exhibit systematic failures in this regard. LLM prematurely terminates diagnostic processes, missing critical dangerous diagnoses, and providing overconfident recommendations.

### 1.3 Limitations of Current Evaluation Infrastructure

To understand this project's design motivation, we must examine the three primary approaches medical researchers currently use to evaluate LLMs and their respective limitations.

**Approach One involving raw programming pipeline** (requiring 12 discrete steps, involving 15 technical concepts)

Medical researchers must write their own Python code to perform the evaluation. It involves data loading, preprocessing, prompt engineering, LLM API calls, result parsing, evaluation metric calculation, result analysis, and other steps. This requires understanding API authentication, data structures, evaluation metrics, error handling, and other technical concepts. This creates significant barriers for researchers with medical backgrounds but limited programming experience.

**Approach Two involving visual platforms** (such as Dify, requiring approximately 5 steps, involving 8 mixed concepts)

These platforms provide node-based workflow construction, reducing programming barriers. However, they remain technology-centric. Users are required to configure "template nodes" and "LLM nodes" rather than "diagnostic reasoning" and "diagnostic criteria verification" which are medical concepts. Medical knowledge and constraints are implicit in prompt text. The platform cannot perform medical semantic-level verification or assistance.

**Approach Three involving fixed public benchmarks** (standardized but inflexible)

Platforms such as HealthBench and MedQA [7] provide standardized datasets and evaluation protocols, facilitating cross-model comparison. However, the fixed nature of these benchmarks limits flexibility. Researchers find it difficult to adjust evaluation standards, apply local guidelines, or test custom diagnostic workflows.

### 1.4 Core Problem Statement

Synthesizing the above analysis, this project identifies the core problem as:

**There is no platform enabling medical researchers to conduct rigorous, flexible, and reproducible LLM evaluations through medical semantics (rather than programming skills or fixed templates).**

The consequences of this problem include medical AI evaluation being limited to the small population possessing both medical knowledge and programming skills. Most medical researchers with critical clinical expertise become excluded. Evaluation standards are difficult to align with actual clinical needs, and the development of clinically-relevant evaluation methodology proceeds slowly.

---

## 2. Related Work and Design Philosophy

### 2.1 Major Paradigms in Medical Reasoning Evaluation Methodology

To design a platform supporting flexible evaluation, we must first understand different methodological frameworks for medical AI evaluation. Through systematic reading of recent literature, we can identify multiple dimensions and paradigms for evaluating medical AI systems. This section's paradigm framework directly guided the platform's framework selection and design.

#### **Dimension One on Process-Based Evaluation versus Outcome-Based Evaluation**

Medical AI system evaluation can be divided into two different orientations along this dimension.

**Process-Based Evaluation Orientation**

This type of method focuses on *how* the model derives diagnoses, not just the final answer. Evaluation key points include several aspects.

The first aspect examines **reasoning step completeness** and evaluates whether the model covers all necessary clinical reasoning steps. For example, MedR-Bench [8] evaluates examination recommendations, diagnostic decision-making, and treatment planning reasoning quality, annotating the correctness of each reasoning step.

The second aspect examines **reasoning step factuality** and evaluates whether medical statements in each reasoning step conform to medical knowledge and clinical guidelines. The DDxReasoning dataset provides 933 clinical cases, each containing fine-grained diagnostic reasoning step annotations verified by physicians [9].

The third aspect examines **reasoning conciseness** and evaluates whether reasoning output is concise and effective, containing no redundant or irrelevant information. Evaluation methods typically measure effective content proportion and information increment.

Typical works include three examples. DDxTutor [9] is a diagnostic reasoning tutoring system decomposing clinical reasoning into teachable components. MedR-Bench [8] conducts three-stage clinical reasoning evaluation using real clinical cases and physician-annotated reasoning steps as ground truth. Medical Reasoning Fidelity [10] identifies cases where final answers are correct but reasoning processes have defects.

**Outcome-Based Evaluation Orientation**

This type focuses on the quality and safety of final diagnoses or decisions. Evaluation metrics include several dimensions.

The first metric is **diagnostic accuracy** which measures the match between final diagnosis and gold standard. Commonly used metrics include top-1 and top-N accuracy [5].

The second metric is **differential diagnosis list reasonableness** which evaluates whether each diagnosis in the generated list is reasonably appropriate for the case, typically evaluated through physician scoring [11].

The third metric is **differential diagnosis list completeness** which assesses whether the list is sufficiently comprehensive and whether important diagnoses are missed. This is evaluated through physician judgment or coverage comparison with expert diagnosis lists [11].

The fourth metric is **clinical safety** which checks whether overconfidence, dangerous recommendations, or missed critical diagnoses occur. Evaluation methods include sensitivity analysis and adverse recommendation detection.

Typical works include three examples. The CLEVER framework [12] uses physician blind review with three-dimension scoring (factual accuracy, clinical relevance, conciseness). DiagnosisArena [5] is a professional-level diagnostic reasoning benchmark with 1,113 complex diagnostic cases. The AMIE system [11] optimizes for differential diagnosis, evaluating quality (appropriateness and completeness).

#### **Dimension Two on Single Metric versus Multi-Dimensional Framework**

Literature demonstrates progression from single metrics to multi-dimensional frameworks.

**Traditional single metrics** include accuracy which is simple but ignores reasoning quality. F1 score is inappropriate for diagnostic reasoning.

**Emerging multi-dimensional frameworks** include three representative examples. MedAgentBoard [13] systematically evaluates multi-agent collaboration, examining not only accuracy but also task completion paths. ClinBench [14] is a standardized multi-domain framework using YAML dynamic prompting and JSON schema validation. Reproducible AI Evaluation [15] defines five dimensions (accuracy, completeness, consistency, relevance, fluency).

The above two dimensions reveal medical AI evaluation's complexity. A good evaluation platform should simultaneously support these different methodological orientations.

### 2.2 Engineering Tradeoffs in Medical AI Workflow Programming

Why not directly use existing general-purpose LLM programming frameworks instead of designing a medical-specific platform? The answer lies in understanding different solutions' design tradeoffs.

**Option A involving general LLM programming frameworks** (LangChain, LangGraph, and others)

These frameworks provide powerful abstraction capabilities, but are "too heavy" for medical researchers. They require learning complex DSLs and graph structures. They remain completely domain-agnostic, embedding no clinical reasoning step concepts. They also lack practical guidance for medical workflows.

**Option B involving fixed medical benchmarks** (MedChain, MedQA [7], and others)

These works provide medical AI workflow examples demonstrating LLM medical application feasibility, but have limitations. Each study targets specific tasks and none abstract to a general platform. Workflows are mostly "single-step RAG" or "simple multi-step pipelines". They lack systematic comparison of different workflows' cost and latency impacts.

**This project's design tradeoffs**

The platform retains several features while sacrificing others. For the lightweight characteristic, the platform supports text-only clinical reasoning but excludes multimodal capabilities and real-time deployment. For the medical-first characteristic, the platform embeds clinical reasoning steps but does not support code execution. For the ready-to-use characteristic, the platform provides prompt libraries and workflow collections but does not offer complete free configuration. For readability, the platform uses YAML format supporting version control. For flexibility, the platform allows custom workflows and metrics.

### 2.3 Design Principles

Synthesizing the above analysis, the platform's four core design principles are as follows.

**Principle P1 on Medical Workflow Abstraction**

Clinical reasoning follows identifiable structures. Platform components directly map clinical concepts ("diagnostic reasoning workflow" rather than "LLM call sequence"), with users specifying medical parameters rather than technical parameters.

**Principle P2 on Multi-Dimensional Evaluation Framework Support**

Based on Section 2.1's analysis, the platform should enable users to flexibly select process-based or outcome-based orientation, single or multi-dimensional frameworks, rather than enforcing one methodology.

**Principle P3 on Declarative Configuration and Reproducibility**

All configurations are stored in YAML format (human-readable, version-control friendly). Evaluation standards are explicitly recorded with literature references. Generated reports contain complete methodological documentation, supporting result verification and reuse.

**Principle P4 on Usability First**

Target users are medical researchers potentially lacking programming experience. Success criterion states that users need only understand 4 medical concepts (workflow, evaluation dimensions, datasets, scoring standards) to complete evaluation configuration, rather than 12 technical concepts.

---

## 3. System Design

### 3.1 Three-Layer Architecture Overview

To implement the above design principles, the platform employs a three-layer architecture that progressively conceals technical complexity behind medical semantics. This section introduces the overall architecture while subsequent sections detail each layer's design and implementation.

**Layer 1 as Medical Concept Layer (User Interface)**

The topmost layer represents the user-facing interface. This is where medical researchers directly interact with the platform. Components at this layer include clinical task templates, evaluation dimension selectors, and dataset management tools. Users are medical researchers who may have basic programming experience but lack deep expertise in LLM engineering and medical AI. The entire input language at this layer uses medical terminology and clinical concepts. Users interact with the lower layers exclusively through YAML-formatted configuration files that employ medical semantics, eliminating the need to engage with technical implementation details.

**Layer 2 as Evaluation Framework Layer (Methodological Transformation)**

The middle layer serves as the critical transformation and adaptation mechanism. This is where algorithm engineers and platform developers work to implement framework integration and methodological workflows. The core function of this layer is translating the medical concepts and requirements described by users at Layer 1 into executable evaluation specifications that can be processed by Layer 3. Components at this layer include framework adapters that map different evaluation methodologies, scoring standard engines that manage evaluation metrics, LLM-as-Judge orchestration systems that coordinate model-based evaluation, and validation logic that ensures medical semantic integrity throughout the transformation process. This layer maintains complete medical semantic integrity while performing technical translation, ensuring that no medical meaning is lost during the transformation from user-friendly descriptions to executable specifications.

**Layer 3 as Data Execution Layer (Infrastructure)**

The bottom layer manages all infrastructure and computational resources. Components include dataset loaders that prepare and manage data from various sources, execution engines that run evaluation workflows, and storage systems that persist results and intermediate data. Technical implementation at this layer prioritizes simplicity, readability, and maintainability. The design philosophy avoids over-engineering, keeping implementations concise and understandable to support Layer 2's requirements without introducing unnecessary complexity.

**Rationale for this three-layer design**

The core reason is achieving clear separation of concerns between user interface and technical implementation. Layer 1 completely avoids technical terminology, using exclusively language familiar to medical researchers. Layer 2 provides the critical transformation and adaptation functionality, translating medical configuration into executable technical specifications while maintaining medical semantic completeness. Layer 3 supports Layer 2's needs through concise, focused implementation without over-engineering. This separation enables three distinct user groups (medical researchers at Layer 1, platform developers at Layer 2, and infrastructure engineers at Layer 3) to work effectively within their domain of expertise.

### 3.2 Medical Workflow Abstraction

Medical workflows' core is understanding how clinical reasoning structures. Through analyzing DoctorFLAN [16] and MedChain research results, we can construct a configurable workflow component set. This section explains this component set's organization structure and how medical researchers can define their own evaluation tasks through selecting and combining these components.

#### **3.2.1 Two-Layer Task Template Structure**

**First Layer on Major Clinical Functions**

The platform provides four core clinical task templates corresponding to doctors' main work functions.

1. **Diagnostic reasoning** generates and verifies diagnostic hypotheses from patient information
2. **Patient classification** assesses patient urgency and care level
3. **Treatment planning** selects and prioritizes evidence-based interventions
4. **Clinical documentation** summarizes and records visit information

**Second Layer on Workflow Stages**

Each major task contains multiple stages. Taking diagnostic reasoning as example, this project designs four stages as shown in the following table.

| Stage | Input | Clinical Task | Output | Evaluation Dimension |
|-------|-------|--------------|--------|---------------------|
| **1. Problem Representation** | Chief complaint, vital signs | Identify clinical clues | 3-5 clinical problems | Completeness, relevance |
| **2. Diagnosis Generation** | Clinical problem list | Generate differential diagnosis | 3-5 diagnostic candidates | Completeness, appropriateness, dangerous DDx coverage |
| **3. Evidence Verification** | Preliminary diagnosis, exam data | Assess evidence | Evidence weight scores | Logic, differential completeness |
| **4. Final Diagnosis** | Evidence summary | Determine working diagnosis | Final diagnosis, confidence | Accuracy, safety |

**Rationale for this stage design**

This four-stage design directly corresponds to clinical diagnostic thinking models described in medical literature. By explicitly defining these stages, researchers can intervene in evaluation at any stage. They can evaluate LLM capability in the preliminary diagnosis generation stage, or evaluate complete multi-stage workflow performance. This flexibility is critical for understanding AI systems' specific weaknesses.

#### **3.2.2 User Configuration Example on Diabetes Diagnostic Reasoning**

Consider an endocrinologist wanting to evaluate GPT-4's performance on diabetes diagnosis, particularly in early diagnosis and disease classification. The configuration would include the following elements.

Under basic settings, the specialty would be endocrinology with patient population as adult new-onset patients.

Under workflow stage selection, all four stages would be included. Stage 1 for problem representation would identify polyuria and polydipsia-related problems. Stage 2 for diagnosis generation would consider Type 1, Type 2, LADA, and other variants. Stage 3 for evidence verification would apply HbA1c and FBG standards. Stage 4 for final diagnosis would determine diabetes type.

Under evaluation dimensions, the selection would include problem identification completeness, diagnosis list appropriateness scoring, diagnostic criteria application correctness, final diagnosis accuracy, and safety (dangerous diagnosis omission).

Under evaluation methodology, the selection would be process plus outcome (combined approach).

Under dataset, the source would be MedChain with conditions filtering to endocrinology specialty and confirmed diabetes cases, yielding approximately 350 cases.

Under model configuration, the model would be GPT-4o with temperature set to 0.7.

The backend automatically generates YAML configuration without requiring direct user editing.

### 3.3 Evaluation Framework Integration

#### **3.3.1 Three Evaluation Framework Systems**

**Framework System One on Process-Based Quality Evaluation**

Typical representatives include MedR-Bench [8], DDxTutor [9], and Chain of Diagnosis [17].

When users select this framework, the platform performs three operations. First, it automatically activates fine-grained reasoning step annotation requirements. Second, it provides step-level scoring standards and LLM-judge prompts. Third, it generates detailed step accuracy reports.

**Framework System Two on Outcome-Based Quality Evaluation**

Typical representatives include CLEVER framework [12], AMIE system [11], and MedAgentBoard [13].

When users select this framework, the platform performs three operations. First, it loads final diagnosis accuracy calculation (top-1 and top-N). Second, if needed, it loads LLM-judge evaluation (appropriateness and completeness). Third, it generates accuracy and safety metrics reports.

**Framework System Three on Combined Evaluation Methods**

Many studies find that evaluating either process or outcome alone insufficiently characterizes system performance. For example, Two-Stage Prompting framework [18] shows that separating different stages for evaluation can identify specific reasoning logic weaknesses.

Users can select combined frameworks where the first two stages use process-based quality evaluation (ensuring diagnostic logic correctness) and the last two stages use outcome-based quality evaluation (ensuring final diagnostic accuracy).

**Rationale for organizing frameworks this way**

Different research questions need different evaluation perspectives. A researcher improving diagnostic reasoning cares about reasoning completeness. A researcher assessing clinical deployment readiness cares about final diagnostic accuracy. The platform, by offering multiple framework options, enables researchers to select flexibly according to their scientific questions.

#### **3.3.2 Multi-Stage LLM-as-Judge Implementation**

When evaluation dimensions require model judgment, the platform uses LLM-as-Judge methodology. A reliable LLM-judge requires careful multi-stage design [12] as follows.

| Stage | Content |
|-------|---------|
| **1. Standard Definition** | Provide judge with scoring standards, medical reference materials, example cases |
| **2. Case Analysis** | Judge analyzes model output, evaluates point-by-point against standards |
| **3. Structured Scoring** | Judge outputs scores, detailed reasoning, confidence |
| **4. Calibration Verification** | Compare with expert physician scoring on 30-50 representative cases, Kappa greater than or equal to 0.70 |

### 3.4 Configuration Complexity Simplification Analysis

To quantify the platform's progress in simplifying medical AI evaluation configuration, this section details work step comparisons across three approaches.

#### **3.4.1 Work Step Comparison**

The following table compares three approaches.

| Approach | Steps | Applicable Users |
|----------|-------|------------------|
| **Raw programming pipeline** | 12 discrete steps | Researchers with programming experience |
| **Dify visual platforms** | 5 steps | Users with basic programming experience |
| **This platform** | 2 main steps | **Medical researchers** |

**Raw programming pipeline detailed steps**

The twelve discrete steps proceed as follows. Step 1 involves environment setup. Step 2 involves data acquisition. Step 3 involves preprocessing. Step 4 involves LLM integration. Steps 5-6 involve prompt engineering. Steps 7-8 involve evaluation metric implementation. Steps 9-10 involve execution and debugging. Steps 11-12 involve documentation and reporting.

**This platform's 2 main steps**

The first main step involves configuring the evaluation task. This includes selecting template, specifying stages, selecting dimensions, selecting paradigm, and selecting dataset.

The second main step involves running evaluation. This includes specifying model, setting hyperparameters, and clicking run.

All other steps (data loading, prompt application, metric calculation, report generation) are automatically handled by the platform.

#### **3.4.2 Concept Complexity Comparison**

The following table compares concept complexity across approaches.

| Concept Type | Raw Programming (15) | Dify Platform (8) | **This Platform (4)** |
|--------------|---------------------|-------------------|----------------------|
| **Programming** | Python, data structures, API calls, error handling | Graph nodes, prompt variables | Not needed |
| **LLM** | Temperature, token limit, rate limit | Prompt design | Basically automated |
| **Evaluation** | Accuracy, F1, metric design | Single metric | Multi-dimensional frameworks, evaluation paradigms |
| **Medical** | Implicit in prompts | Implicit in prompts | Workflow, dimensions, diagnostic standards |

**Key difference**

Both raw programming and Dify require users to understand LLM technical details, which are irrelevant distraction for medical researchers. This platform shifts these technical details to the framework layer, letting users focus only on medical concepts.

### 3.5 Implementation Status and Progress

**Completed portions (approximately 40%)**

The completed work includes architecture design, technology stack selection, and documentation writing. Dataset loaders support MedChain and MedQA formats. The basic prompt template system covers diagnostic reasoning and classification tasks. The evaluation metrics library includes accuracy, precision, recall, and other metrics. JSON result storage and Markdown report generation are functional. FastAPI backend framework and basic API endpoints are implemented.

**In progress portions (approximately 40%)**

The ongoing work includes medical concept layer UI using React component library. Process-based quality metrics implement completeness and factuality calculation. LLM-as-Judge orchestration and multi-stage calibration are being developed. Workflow template library expansion covers 4 core clinical tasks. YAML configuration generation and validation system are under development.

**Planned portions (approximately 20%)**

The planned work includes outcome-based quality metrics implementing accuracy and safety scoring. Multi-framework integration testing and UI feedback will proceed. User research and usability testing will be conducted. Complete documentation, tutorials, and API reference will be written.

## 4. Verification and Scientific Value

Sections 1 to 3 explain the motivation, related work, and system design. Building on that foundation, this section explains how the project will verify that the platform is correct, usable, and scientifically meaningful before it is treated as a reliable evaluation tool.

### 4.1 Why Multi-Dimensional Verification?

Before formal platform launch, systematic verification is needed to ensure that the platform is both reliable and valuable in practice. Verification in this context is not merely about "finding bugs" but about demonstrating that the implementation truly matches the design goals and supports credible scientific use.

To cover these different aspects, the project adopts three complementary verification levels, each focusing on a distinct question. The first level examines **technical correctness** and asks whether the platform's implementation of evaluation workflows and metrics is accurate. The second level focuses on **usability** and asks whether target users can independently complete evaluations using only medical concepts. The third level targets **scientific value** and asks whether the platform can realistically support new empirical studies in medical AI.

The first verification level addresses technical correctness by checking whether the platform reproduces published benchmark results using its own pipelines. The second verification level examines usability through structured user studies with 7–10 participants from the target medical audience. The third verification level assesses scientific value by running a complete comparative study that uses the platform as the main research tool.

With these verification goals established at a high level, the next subsection specifies concrete tasks, participants, and success criteria for each level.

### 4.2 Detailed Three-Level Verification Strategy

#### **Verification Level One on Technical Correctness Verification**

The first level focuses on whether the platform faithfully implements evaluation frameworks and metric calculations without introducing systematic errors. This is essential because any upstream mistakes in data handling or scoring would invalidate subsequent usability findings and research conclusions.

To test this, the project reproduces published benchmark studies using the platform's own configuration and execution pipeline. The first task is MedChain reproduction, which aims to recover key stage-wise performance metrics with a success criterion of an error less than or equal to 5% relative to the reported results. The second task is DiagnosisArena subset reproduction, which evaluates whether the platform preserves model ranking patterns with a success criterion of Spearman correlation greater than or equal to 0.90 [5].

Together, these two tasks provide a quantitative check that the platform's data processing and metric computations are aligned with existing, peer-reviewed benchmarks.

#### **Verification Level Two on Usability Verification**

Once technical correctness has been established, the focus shifts from implementation details to the experience of intended users. This second level evaluates whether medical-background researchers, who may have limited programming experience, can configure and run evaluations while thinking in clinical rather than engineering terms.

The core objective is to show that such users can successfully complete typical evaluation tasks using only the platform's medical concepts and interface. To test this, the project will conduct small-scale user studies. Participants (n = 7–10) will be drawn from medical informatics students, clinical medicine master's students, and practicing medical professionals.

Each participant will be asked to complete two tasks within a 1-hour session. The first is a simple configuration task: setting up an evaluation of GPT-4 on a MedQA subset, with outcome measures including completion rate, time to completion, and configuration errors. The second is a medium-complexity configuration task: building a diagnostic workflow and comparing two models, with outcome measures including completion rate, understanding of key decision points, and reported difficulties during configuration.

Success criteria are defined along three thresholds. The completion rate should be at least 60%, which is reasonable for a prototype targeting non-programmers. The System Usability Scale score should reach at least 65, indicating acceptable usability. Finally, medical semantic clarity, as rated by participants, should be at least 5 out of 7, indicating that the platform's concepts are understandable in clinical terms.

#### **Verification Level Three on Scientific Value Verification**

Even if a platform is technically correct and usable, it must still demonstrate that it enables meaningful research that would otherwise be difficult, slow, or error-prone. The third level therefore evaluates scientific value through an end-to-end study that uses the platform as the primary research instrument.

The example study investigates how diagnostic workflow complexity affects accuracy in medical LLM evaluation. The underlying question is whether multi-stage workflows consistently outperform simpler, single-stage approaches. This question has direct engineering implications for deployment complexity and also contributes to a deeper understanding of how LLMs reason in clinical contexts.

The study design includes three experimental conditions. Condition A uses a single-stage workflow that directly generates the final diagnosis. Condition B uses a two-stage workflow that first generates a differential diagnosis list and then applies diagnostic standards. Condition C uses a four-stage workflow including problem representation, differential diagnosis generation, evidence verification, and final diagnosis determination.

Evaluation metrics are defined at two levels. The primary metric is diagnostic accuracy across conditions. Secondary metrics include configuration time required by researchers and a structured score for reasoning process quality, allowing the study to capture both performance and practical cost.

The expected findings include quantitative evidence on how accuracy changes with workflow complexity and whether there are diminishing returns beyond a certain number of stages. In addition, qualitative analysis will identify which case types benefit most from multi-stage reasoning. Together, these results both validate the platform's ability to support real medical AI research and provide practical guidance for designing LLM-based diagnostic workflows.

### 4.3 Platform's Expected Scientific Contributions

The multi-level verification plan naturally leads to a discussion of what the platform is expected to contribute once it is stable enough to be shared and reused. These contributions can be viewed along two main dimensions: methodological impact and practical impact.

On the methodological side, the platform aims to show that a medical-centered design can substantially lower the technical barrier for rigorous AI evaluation. By re-framing configuration around workflows, evaluation dimensions, and clinical standards, it enables a broader group of medical professionals to participate directly in designing and interpreting evaluations, rather than deferring entirely to technical specialists.

On the practical side, the project plans to release the platform under an Apache 2.0 license, accompanied by documentation, tutorials, and example workflows. This is intended to provide the community with a reusable tool that can be adapted to different clinical domains while maintaining transparent configuration and reproducible evaluation pipelines.

### 4.4 Project's Main Limitations

Clarifying limitations is essential for interpreting the scope of the results and for identifying directions for future work. This subsection therefore outlines the main constraints of the current project stage.

First, the **functional scope** of the platform is intentionally restricted. The current design focuses on text-based clinical reasoning tasks and does not attempt to cover multimodal data such as medical imaging, real-time deployment scenarios, or code execution. These capabilities are left for future extensions once the core workflow and evaluation framework are mature.

Second, the project faces **resource constraints**. Development is carried out by a single person, which makes it necessary to prioritize core functionality such as workflow abstraction and multi-dimensional evaluation frameworks. More advanced features, including distributed evaluation and automatic prompt optimization, are deferred to later phases or potential follow-up projects.

Third, there are inherent challenges regarding **LLM-as-Judge reliability**. Model-based judgment may introduce biases or inconsistencies into the evaluation process. To mitigate this, the platform incorporates calibration protocols, supports multi-judge consensus mechanisms, documents judgment methodology transparently, and recommends human review for high-stakes medical decisions. These measures do not completely eliminate risk but are intended to keep LLM-based evaluation within a controlled and auditable framework.

---

## 5. Project Timeline and Summary

After defining what must be verified, the project can be planned so that development milestones and validation activities reinforce each other. This section provides the timeline and explains why the project matters in a broader medical AI evaluation context.

### 5.1 Development and Verification Timeline

The development proceeds through three phases as shown in the following table.

| Phase | Timeline | Work Content | Expected Outcome |
|-------|----------|--------------|------------------|
| **Core Function Development** | Jan-mid Feb (8 weeks) | UI framework, LLM-as-Judge, template library expansion | 40% completion |
| **Verification and Optimization** | Late Feb-mid Mar (3-4 weeks) | MedChain reproduction, user testing | Technical validation plus feedback improvements |
| **Documentation and Summary** | Late Mar-early Apr (2-3 weeks) | User docs, tutorials, API reference | Complete docs, midterm report |

The delivery time is mid-April 2026.

### 5.2 Project's Core Significance

The knowledge-practice gap in medical AI evaluation is not merely a technical problem but a power structure issue. Current evaluation tools, designed by technical experts for technical personnel, cause most medical professionals to passively accept evaluation results.

This project, through medical-centered platform design, aims to change this structure through four goals.

These goals also guide what evidence will be collected during verification and what features are prioritized during implementation.

The first goal is empowering medical professional knowledge. This enables medical researchers to directly participate in AI evaluation and improvement rather than passively accepting others' evaluation conclusions.

The second goal is promoting clinically-relevant research. This enables medical researchers to pose fundamental clinical questions about how AI performs in their patient population and whether it follows their clinical guidelines.

The third goal is accelerating evaluation methodology development. This lowers evaluation costs and complexity, enabling broader teams to attempt and compare different evaluation methods, driving clinical evaluation standard development.

The fourth goal is supporting responsible AI development. When medical researchers participate in evaluation, they take responsibility for results, promoting more cautious and responsible medical AI development.

Ultimately, this platform does not replace medical judgment with automation but empowers medical professional knowledge participation by eliminating technical barriers.

---

## References

[1] Koh H.Y., et al., Knowledge-Practice Performance Gap in Clinical Large Language Models: Systematic Review of 39 Benchmarks, JMIR, Vol. 27, 2025.

[2] Singhal K., et al., Toward Expert-Level Medical Question Answering with Large Language Models, Nature Medicine, Vol. 31, No. 1, 2025.

[3] Koh H.Y., et al., Clinical reasoning and decision-making evaluation across major medical LLM benchmarks, JMIR, Vol. 27, 2025.

[4] Gao Y., et al., MedAgentBench: A Realistic Virtual EHR Environment to Benchmark Medical AI Agents, NEJM AI, Vol. 2, No. 1, 2025.

[5] Zhu Y., Huang Z., Mu L., Huang Y., Nie W., Liu J., Zhang S., Liu P., Zhang X., DiagnosisArena: Benchmarking Diagnostic Reasoning for Large Language Models, arXiv preprint arXiv:2505.14107, 2025.

[6] Liu J., Wang W., Ma Z., Huang G., Su Y., Chang K.J., Chen W., Li H., Shen L., Lyu M.R., MedChain: Bridging the Gap Between LLM Agents and Clinical Practice with Interactive Sequence, Proceedings of NeurIPS 2025, 2025.

[7] Jin D., Pan E., Oufattole N., Weng W.H., Fang Y., Szolovits P., What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams, arXiv preprint arXiv:2009.13081, 2021.

[8] Quantifying the Reasoning Abilities of LLMs on Clinical Cases (MedR-Bench), Nature Communications, Vol. 16, Article no. 452, 2025.

[9] Wu Q., Gao Z., Gou L., Dou Q., DDxTutor: Clinical Reasoning Tutoring System with Differential Diagnosis-Based Structured Reasoning, Proceedings of ACL 2025, July 27-August 1, 2025, pp. 30934–30957.

[10] Favelukes G., et al., Fidelity of Medical Reasoning in Large Language Models, JAMA Network Open, Vol. 8, No. 1, Article e2437372, 2025.

[11] Tu T., McDuff D., et al., Towards Conversational Diagnostic Artificial Intelligence (AMIE), Nature, Vol. 630, 2025, pp. 621-629.

[12] Kocaman V., Kaya M.A., Feier A.M., Talby D., Clinical Large Language Model Evaluation by Expert Review (CLEVER): Framework Development and Validation, JMIR AI, Vol. 4, Article e72153, 2025.

[13] Zhu Y., et al., MedAgentBoard: Benchmarking Multi-Agent Collaboration with Conventional Methods for Diverse Medical Tasks, Proceedings of NeurIPS 2025, Datasets and Benchmarks Track, 2025.

[14] Villanueva-Miranda I., et al., ClinBench: A Standardized Multi-Domain Framework for Reproducible LLM Benchmarking in Clinical NLP, Proceedings of NeurIPS 2025, Datasets and Benchmarks Track, 2025.

[15] Johnson A., et al., Reproducible Generative AI Evaluation for Health Care: A Clinician-in-the-Loop Approach, PMC, Article PMC12169418, 2025.

[16] FreedomIntelligence, DoctorFLAN: Doctor-Focused Language Model, Hugging Face Datasets, https://huggingface.co/datasets/FreedomIntelligence/DoctorFLAN, 2024.

[17] Zhang P., et al., CoD: Towards an Interpretable Medical Agent using Chain of Diagnosis, arXiv preprint arXiv:2407.13301, 2024.

[18] Zhang L., et al., Two-stage Prompting Framework with Predefined Clinical Reasoning, Nature Digital Medicine, Vol. 8, Article no. 12, 2025.