

## Introduction & Motivation

- 📚 Background: LLM workflows as a topic have accumulated substantial academic work and open-source contributions over recent years, and so has medical reasoning
- 🔍 Observation: However, despite the richness of existing code and open-source tools, published work still predominantly follows a "custom code for a specific paper" pattern, even though many tasks (such as LLM API calls, workflow orchestration, prompt design) are highly repetitive

Why Not Use Existing Solutions?
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

How to Solve?
- Lightweight Medical Workflow Authoring & Evaluation Framework — reduce the barrier to reproducing and iterating medical reasoning workflows through medical semantic design and deliberate functional focus
    - Integrate abundant existing medical academic work and related engineering work into a unified, specialized platform
        - Three core objectives:
            1. Support rapid workflow switching and authoring
            - Built-in workflow templates validated by existing papers (CoT, Multi-Agent, Self-Refine)
            - Provide medical semantic nodes (Clue Representation, Hypothesis Generation, Hypothesis Evaluation, etc.)
            - Users can rapidly compose different workflows without needing deep understanding of underlying technical details

            1. Support rapid application of various medical benchmarks
            - Integrate common medical benchmarks (MedQA, PubMedQA, MedRBench, etc.)
            - Users only select a dataset; the system automatically handles data adaptation
            - One-click evaluation with automatic comparison visualization

            1. Simplify and abstract, reduce configuration complexity
            - Remove non-essential technical concepts (data storage protocols, publishing forms, etc.)
            - Use intuitive language instead of technical jargon

*

## Methods

1) Three-layer function system (Prompt / Component / Recipe)
   - Prompt Layer: One-click application of prompt engineering techniques
       - Self-Refine: Embedded in nodes, can be toggled on/off for iterative self-checking
       - Chain-of-Thought: Provide prompt templates for rapid step-by-step reasoning setup
       - Self-Consistency: Pre-wired node templates with multiple sub-LLMs + aggregation LLM
   
   - Component Layer: Medical semantic node library (extracted from existing papers)
       - Based on analysis of existing papers, medical clinical reasoning divides into three core steps:
           1. Clue Representation
               - Goal: Convert free-text or semi-structured medical information (symptoms, signs, test results) into structured clinical clue representation
               - Role: Establish clear, traceable information foundation for subsequent reasoning
               - Implementation: Clue Representation node structures benchmark inputs (question stem, options) into traceable clinical clue representation
           
           2. Hypothesis Generation / Differential Diagnosis (DDx)
               - Goal: Based on structured clues, generate possible diagnostic candidates with supporting and opposing evidence
               - Role: Systematically explore diagnostic space, avoid premature convergence
               - Implementation: Hypothesis Generation node generates possible diagnoses and candidate lists based on Clue Representation node output
           
           3. Hypothesis Evaluation
               - Goal: Comprehensively evaluate, rank candidate diagnoses, and select the most likely one
               - Role: Form final diagnostic decisions with supporting rationale
               - Implementation: Hypothesis Evaluation node evaluates and ranks diagnostic candidates from Hypothesis Generation, selecting the most likely diagnosis
   
   - Recipe Layer: Pre-configured workflow templates (one-click replication)
       1. Basic reasoning architecture: CoT or single-step diagnostic reasoning
       2. Multi-Agent architecture: Three independent agents executing "Clue Representation → Hypothesis Generation → Hypothesis Evaluation"
       3. Process-aware reasoning architecture: Multi-dimensional evaluation of reasoning process (assess both results and reasoning steps)

2) One-click benchmark evaluation
   - Functionality:
       - User selects dataset (MedQA / PubMedQA / MedRBench, etc.)
       - System automatically handles data loading, format conversion, workflow interface adaptation
       - Automatically generates visualization charts after evaluation
   
   - Benchmark ecosystem status
       - Dataset Layer: Current medical LLM benchmarks are well-established
           - MedQA: Medical licensing exam-style multiple-choice questions
           - MedRBench: Medical reasoning benchmark covering multiple reasoning task types
       - Metrics Layer: Evaluation dimensions systematically categorized
           - Result-Based: Accuracy, Appropriateness, Comprehensiveness, Sensitivity
           - Process-Based: Completeness, Factuality, Efficiency
       - Extra:
           - MedHELM: Comprehensive evaluation benchmark platform with datasets and various metrics
       - Current state: While datasets and metrics are well-researched, a unified platform integrating them for quick workflow comparison is lacking
   
   - Example: MedQA
       - User selects MedQA and chooses metrics to evaluate (e.g., accuracy)
       - System automatically loads relevant data interface protocols, extracts and parses questions
       - Parsed questions are automatically integrated as part of prompts into initial workflow inputs
       - Workflow normalizes final output format to MedQA multiple-choice question format
       - Based on normalized outputs, the system extracts LLM answers and invokes visualization module to compute accuracy
       - Generate visualization

3) Lightweight design
   - Removed features (non-essential for medical workflow research):
       - Third-party tool integration (marketplaces, plugin ecosystems)
       - MCP Server, API endpoints, SDK ecosystems
       - Multiple app types, permission systems, publishing forms
   - Retained core capabilities: Workflow execution, data flow tracing, result visualization, log export

*

## Current Progress

- Core extensible codebase is complete, with numerous interfaces preserved based on system requirements. Remaining work is feature completion and frontend development—no major development tasks remain
- MVP demonstration of existing code capabilities
    - Task Definition:
        - Input: MedQA multiple-choice questions (question stem + 4–5 options)
        - Output: Final choice (A/B/C/D/E) + reasoning process + cost metrics
        - Process: Three clinical reasoning nodes + one self-refine
            - Question → [Agent1: Clue Representation] → [Agent2: Hypothesis Generation] → [Agent3: Hypothesis Evaluation + Self-Refine] → Final Answer
        - Core Metrics: Accuracy (match with gold standard) + workflow setup/execution cost
    - Comparison with general framework (verifiable, measurable):
        | Dimension | Your Platform | Dify | Significance |
        |---------|-----------|---------|-----------
        | Setup Steps (UI interactions) | ~5–8 steps | ~15–20 steps | Medical semantic nodes reduce generic technical configuration |
        | Concepts to Master | ~8–10 | ~20–25 | No need to understand data storage, publishing, APIs, etc. |

Data source note (to be verified):
- Steps and concept counts: counted via UI screenshots and documentation
- Time: repeated 3 times, recording mean and standard deviation
- Concept counts: statistics from official documentation of each platform on "must understand" core concepts

Table conclusion:
> *This is not to say Dify is bad—its generality is its strength. But for medical reasoning workflow research as a specific task, we effectively lower barriers and cognitive load through medical semanticization.*

*

## System Architecture Diagram

Title: *Three-Layer Medical-First Architecture*

Visualization diagram (recommended):

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

*

## Evaluation

Title: *How We Validate the Solution*

Three-layer validation:

1. Engineering cost comparison (objective metrics) [already did a simple version]
   - Method: Measure same task (MedQA MVP) cost on both platforms
   - Metrics: Steps, concept count, time, code rewrites
   - Output: Comparison table + screenshots

2. Medical user feedback (qualitative)
   - Method: Recruit 3–5 medical students/researchers to build workflows on our platform
   - Metrics: Operational difficulty, comprehension speed, need for hand-coding, satisfaction
   - Output: User feedback summary

3. Reproducibility verification
   - Method: Reproduce existing paper's workflow using our platform
   - Metrics: Success/failure, rewrite amount, result alignment with original paper
   - Output: Reproduction report + cost comparison

*

## Discussion

Title: *What We Are NOT Claiming*

Clear statements:
- ❌ Not method innovation: We don't propose new medical reasoning algorithms
- ❌ Not evaluation innovation: We don't design new medical evaluation metrics (reuse existing ones)
- ❌ Not general platform competition: We don't attempt to replace Dify/LangGraph

What we ARE doing:
- ✅ Systems engineering contribution: Medical semanticization, standardization, and reusability of medical reasoning workflows
- ✅ Domain specialization: Reduce engineering burden for medical researchers, shorten workflow design-validation cycles
- ✅ Extensible foundation: Provide clear, flexible extension platform for future researchers

Positioning:
> *This is a Systems/Tools type contribution, with value in standardization, accessibility, reproducibility rather than methods or algorithmic innovation.*

Code usability commitment:
- We understand the platform can never satisfy all needs, so we deliberately maintain code simplicity and modularity
- Remove hard-coded technical concepts, maximize flexibility
- Provide clear extension interfaces for users with additional needs to quickly extend

*

## Conclusion

Closing statement:
> Medical reasoning LLM research already has substantial academic foundation. But the lack of engineering standardization remains a bottleneck to broad innovation and reproducibility.
> 
> We propose a medical-specialized workflow framework that, through medical semantic design and deliberate functional focus, frees medical researchers from "repetitive engineering work" to focus on medical hypotheses and workflow design itself.
> 
> This is not an academic breakthrough, but it could become a useful research tool that accelerates collective progress in the medical LLM field.