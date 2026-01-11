# 设计一套可复用的 LLM 评估工作流与接口

## 核心目标

在前文"临床推理分析"章节中，我们明确了诊断推理的六个步骤与两种评估维度（过程导向 vs 结果导向）。本章节的目标是设计一套**原子化的、可在任意推理步骤复用的 LLM 评估工作流**，使得教师或平台开发者可以在不同教学任务中快速部署相同的评估框架，而无需每次都重新编写 prompt 与评分逻辑。

### 核心原则

1. **输入标准化**：每个评估任务都映射到统一的输入格式（task metadata + case context + student response + reference answer）。
2. **输出结构化**：LLM 的评分结果遵循统一的 JSON 架构，包含多维度分数、理由、置信度等字段。
3. **可靠性机制**：通过多模型合议、一致性检验与置信度阈值，判断评分的可信程度，自动决定是否需要人工复核。

---

## 一、原子化的 LLM-as-Judge 评估方法

在医学教育中，LLM-as-Judge 的核心工作流可以抽象为四个关键操作：

### 1.1 **信息提取与标准化（Information Extraction & Normalization）**

LLM 首先需要从学生的原始回答中，提取出可评估的"陈述"（statements），然后将其标准化为结构化形式。

**具体操作：**
- 输入：学生对某一步骤的回答（可能是自由文本、表格或混合格式）
- 操作：LLM 使用"extraction prompt"识别回答中的关键要素，并将其转换为机器可读的格式
- 输出：`{extracted_statements: [...], normalization_confidence: float}`

**例子**：在"假设生成（DDx 阶段）"中，学生可能写：
```
患者主要症状是胸痛和呼吸困难。我认为可能是心肌梗死、肺栓塞或气胸。
心肌梗死风险最高因为患者有高血压和吸烟史。
```

LLM 的提取操作应输出：
```json
{
  "extracted_ddx": [
    {"diagnosis": "心肌梗死", "rank": 1, "reasoning": "高血压和吸烟史"},
    {"diagnosis": "肺栓塞", "rank": 2, "reasoning": "呼吸困难"},
    {"diagnosis": "气胸", "rank": 3, "reasoning": "急性胸痛"}
  ],
  "extraction_confidence": 0.95
}
```

此操作的目的是**将模糊的自然语言转化为清晰的"可被评价的陈述"**，为后续的评分奠定基础。

---

### 1.2 **基准对比（Benchmark Comparison）**

一旦提取了学生的陈述，LLM 需要将其与"金标准答案"或"数据库中的合理答案"进行对比，判断相似性、覆盖度、准确性。

**具体操作：**
- 输入：提取后的学生陈述 + 金标准答案（reference answer）
- 操作：LLM 逐项对比，计算"匹配度"与"新颖性"
  - **匹配度（Match Score）**：学生的答案在金标准中是否出现或等价出现
  - **新颖性（Novelty）**：学生提出的诊断是否为金标准以外但仍合理的诊断
  - **排序合理性（Ranking Coherence）**：学生给出的优先级排序是否与临床合理性一致
- 输出：`{match_scores: [...], novelty_flags: [...], ranking_alignment: float}`

**例子**：继续 DDx 阶段，假设金标准答案是：
```json
{
  "correct_ddx": [
    {"diagnosis": "心肌梗死", "rank": 1},
    {"diagnosis": "肺栓塞", "rank": 2},
    {"diagnosis": "食管痉挛", "rank": 3}
  ],
  "dangerous_exclusions": ["急性主动脉夹层"]
}
```

LLM 的对比操作输出：
```json
{
  "matches": [
    {"student_diagnosis": "心肌梗死", "in_reference": true, "rank_alignment": "exact"},
    {"student_diagnosis": "肺栓塞", "in_reference": true, "rank_alignment": "exact"},
    {"student_diagnosis": "气胸", "in_reference": false, "rank_alignment": "N/A"}
  ],
  "missing_dangerous_diagnoses": ["急性主动脉夹层"],
  "overall_coverage": 0.67,
  "dangerous_omission_risk": "HIGH"
}
```

这一步回答了**"学生的答案在多大程度上与专家共识相符"**。

---

### 1.3 **多维度打分（Multi-Dimensional Scoring）**

基于提取和对比的结果，LLM 对学生的表现在多个维度上给出分数。这些维度来自前文定义的评估框架。

**具体操作：**
- 对于**过程导向**维度，打分内容包括：
  - **完整性（Completeness）**：学生有没有列出足够的诊断？是否涵盖了不同类别的疾病？
  - **逻辑性（Logical Coherence）**：学生为每个诊断给出的理由是否合理？推理链条是否清晰？
  - **事实准确性（Factuality）**：学生提到的临床特征、风险因素等是否正确？
  - **表达简洁性（Conciseness）**：冗长啰嗦还是言简意赅？

- 对于**结果导向**维度，打分内容包括：
  - **准确性（Accuracy）**：排在第一位的诊断是否正确？前三个中有没有正确答案？
  - **全面性（Comprehensiveness）**：有没有遗漏高风险、高流行率的诊断？特别是"dangerous diagnoses"有没有遗漏？
  - **安全性（Safety）**：有没有给出明显危险或不合理的诊断？
  - **专业性（Clinical Professionalism）**：语言是否符合临床规范？

**例子**：继续 DDx 阶段的打分：

```json
{
  "process_oriented_scores": {
    "completeness": 3.5,
    "logical_coherence": 4.0,
    "factuality": 4.5,
    "conciseness": 3.0,
    "process_average": 3.75
  },
  "result_oriented_scores": {
    "accuracy_top1": 1.0,
    "accuracy_top3": 1.0,
    "comprehensiveness": 3.5,
    "dangerous_diagnosis_coverage": 0.0,
    "safety": 3.0,
    "clinical_professionalism": 4.0,
    "result_average": 2.08
  },
  "overall_score": 2.92,
  "dimension_breakdown": {
    "DDx_breadth": 3.5,
    "DDx_appropriateness": 4.0,
    "initial_ranking_quality": 4.0,
    "awareness_of_critical_diagnoses": 1.0
  }
}
```

上述例子中，学生在"排序"与"单诊断理由"上表现较好（过程好），但在"全局安全性"（遗漏主动脉夹层）与"准确性"（诊断可能不对）上不够理想（结果有风险）。

---

### 1.4 **理由与可解释性生成（Rationale Generation & Explainability）**

仅有分数是不够的。教师与学生都需要理解"为什么给这个分数"。LLM 需要为每个维度生成一份简明的"评分理由"。

**具体操作：**
- 输入：上述打分结果 + 学生陈述 + 评分维度定义
- 操作：LLM 生成自然语言的评价，指出："这个维度表现好/不好的具体原因是什么"
- 输出：`{dimension_rationales: {}, overall_feedback: str, improvement_suggestions: [str]}`

**例子**：

```json
{
  "dimension_rationales": {
    "completeness": "学生列出了3个诊断，覆盖了胸痛的主要鉴别诊断。但未列出食管痉挛、心包炎等常见非急症诊断，完整性良好但有改进空间。",
    "dangerous_diagnosis_coverage": "⚠️ 学生未提及'急性主动脉夹层'，这是高死亡率且症状与心肌梗死相似的诊断。这是该回答中最严重的遗漏。",
    "accuracy_top1": "学生排在首位的是心肌梗死，但根据病例全景（患者年轻、无冠心病风险因素），实际首诊应为肺栓塞。",
    "ranking_quality": "学生的排序部分基于症状相似性而非病例流行病学。虽然逻辑可理解，但与临床优先级有偏离。"
  },
  "overall_feedback": "你的诊断思路清晰，论证逻辑较好，但在诊断优先级与高危诊断的识别上有改进空间。建议重点学习'胸痛的鉴别诊断'中 Rule-Out 的优先级。",
  "improvement_suggestions": [
    "补充急性主动脉夹层作为候选诊断，并学习其快速识别特征",
    "基于病例信息（年龄、风险因素）重新调整诊断优先级",
    "考虑列出5-7个诊断而不是仅3个，尤其是在初始阶段"
  ]
}
```

这一步确保评分的**透明性与可操作性**。学生不只看到分数，还能理解改进方向。

---

## 二、在临床推理步骤中的具体应用：两个案例

### 案例1：假设生成阶段（DDx 阶段）的完整工作流

**病例背景**：
```
患者：56岁女性
主诉：3小时急性胸痛伴呼吸困难
既往史：高血压，吸烟20年
体检：BP 160/95, HR 110, RR 24, O2 Sat 92%
初步检查：心电图无特殊变化，肺部未闻及罗音
```

**学生回答**：
```
问题表征：56岁女性，急性胸痛伴呼吸困难，高血压吸烟史
初步诊断：
1. 心肌梗死
2. 肺栓塞  
3. 气胸
我认为最可能是心肌梗死因为患者有高血压和吸烟。
```

**LLM 评估工作流**：

**Step 1：提取**
```json
{
  "extracted_ddx": [
    {"diagnosis": "心肌梗死 (MI)", "rank": 1, "evidence": "高血压和吸烟"},
    {"diagnosis": "肺栓塞 (PE)", "rank": 2},
    {"diagnosis": "气胸", "rank": 3}
  ],
  "extraction_confidence": 0.98,
  "flags": ["reasoning_incomplete_for_rank2_and_3"]
}
```

**Step 2：对比**
```json
{
  "reference_ddx": [
    {"diagnosis": "肺栓塞", "rank": 1},
    {"diagnosis": "心肌梗死", "rank": 2},
    {"diagnosis": "主动脉夹层", "rank": 3},
    {"diagnosis": "气胸", "rank": 4},
    {"diagnosis": "急性冠脉综合征", "rank": 5}
  ],
  "comparison": {
    "MI_ranking_error": "学生列为1，参考为2，排序不当",
    "PE_ranking_error": "学生列为2，参考为1，排序相反",
    "missing_critical": ["主动脉夹层"],
    "false_high_rank": ["气胸不应在前三"]
  },
  "coverage_score": 0.60,
  "critical_error_count": 1
}
```

**Step 3：打分**
```json
{
  "process_scores": {
    "completeness": 3.0,
    "logical_coherence": 3.5,
    "factuality": 4.0,
    "conciseness": 4.5,
    "avg_process": 3.75
  },
  "result_scores": {
    "top1_accuracy": 0.0,
    "top3_coverage": 1.0,
    "comprehensiveness": 2.5,
    "dangerous_diagnosis_awareness": 0.0,
    "safety": 3.0,
    "avg_result": 1.08
  },
  "overall": 2.41,
  "confidence": 0.92
}
```

**Step 4：理由**
```json
{
  "rationale": {
    "top1_ranking_error": "学生将MI列为首选，但病例中几项关键点支持PE：(1)急性呼吸困难是PE的典型表现；(2)心电图无特异性，不支持MI；(3)年龄和性别虽支持MI，但临床场景更指向PE。这是诊断优先级认知的弱点。",
    "missing_aortic_dissection": "⚠️ 严重遗漏。患者高血压+急性胸痛+呼吸困难的三联症，主动脉夹层必须在鉴别诊断中。遗漏此诊断可能导致致命后果。",
    "process_strength": "学生能够快速生成3个主要诊断，且对风险因素有基本认识。逻辑表述清晰。",
    "recommendation": "需要加强'胸痛鉴别诊断的流程图'学习，特别是PE vs MI vs 主动脉夹层的快速区分。建议使用临床决策规则（如PERC rule）来优化排序。"
  }
}
```

**关键点**：
- 此工作流清晰地表明了学生在"思维过程"与"最终结论"上的具体不足
- 评分不仅反映分数，还指出了"为什么这样排序是错的"以及"如何改进"
- LLM 可自动识别"致命的诊断遗漏"（主动脉夹层），提升安全意识

---

### 案例2：问题表征阶段（Problem Representation）的工作流

**病例背景**：
```
患者：67岁男性，主诉"咳嗽"已2周
咳嗽特点：干咳，无痰，夜间加重，不影响睡眠
伴随症状：无发热、无胸痛、无呼吸困难
既往史：慢阻肺10年，高血压
用药：血管紧张素受体阻滞剂（ARB）
```

**学生回答**：
```
患者是老年男性，有两周咳嗽。因为他用了血管紧张素受体阻滞剂，
可能与药物有关。他有慢阻肺，所以可能是慢阻肺急性加重。
还要检查一下有没有肺炎或其他感染。
```

**LLM 评估工作流**：

**Step 1：提取问题表征**
```json
{
  "extracted_problem_representation": {
    "chief_complaint_elements": ["咳嗽", "2周"],
    "semantic_qualifiers": ["干咳", "夜间加重"],
    "explicitly_mentioned_hypotheses": [
      {"hypothesis": "药物相关（ARB引起的咳嗽）", "rank": 1},
      {"hypothesis": "慢阻肺急性加重", "rank": 2},
      {"hypothesis": "感染（肺炎）", "rank": 3}
    ],
    "extraction_quality": 0.85,
    "completeness_of_semantic_qualifiers": 0.70,
    "flags": ["没有提及频率、严重程度等维度"]
  }
}
```

**Step 2：对比与验证问题表征质量**
```json
{
  "reference_problem_representation": {
    "optimal_statement": "67岁男性，干咳2周，夜间加重，在ARB治疗期间。既往慢阻肺。",
    "critical_semantic_qualifiers": [
      "干咳（重要：排除感染可能）",
      "2周（时间线）",
      "夜间加重（特异性指标）",
      "在 ARB 使用期间（因果联想）"
    ],
    "standard_ddx_for_this_representation": [
      {"diagnosis": "ACE抑制剂/ARB诱发的咳嗽", "likelihood": 0.40},
      {"diagnosis": "上呼吸道感染后咳嗽", "likelihood": 0.30},
      {"diagnosis": "慢阻肺急性加重", "likelihood": 0.20},
      {"diagnosis": "肺炎", "likelihood": 0.10}
    ]
  },
  "student_representation_analysis": {
    "semantic_precision": 0.75,
    "hypothesis_rank_alignment": "POOR",
    "missing_semantic_qualifiers": ["干咳的特殊含义被低估"],
    "reasoning_quality": "逻辑可追踪但优先级不当"
  }
}
```

**Step 3：打分**
```json
{
  "problem_representation_scores": {
    "summary_statement_clarity": 3.5,
    "semantic_qualifier_precision": 3.0,
    "information_density": 3.0,
    "hypothesis_triggering_alignment": 2.5,
    "process_avg": 3.0
  },
  "implication_scores": {
    "does_representation_lead_to_optimal_ddx": 0.0,
    "ranking_alignment_with_representation": 1.0,
    "clinical_reasoning_quality": 2.0
  },
  "overall": 2.33,
  "confidence": 0.88
}
```

**Step 4：理由与改进建议**
```json
{
  "detailed_feedback": {
    "strength": "学生识别了干咳的关键特征，也意识到 ARB 与咳嗽的关联，显示医学知识基础不错。",
    "weakness": {
      "semantic_qualifier_underutilization": "干咳是区分'药物副作用'vs'感染'的关键线索，但学生未充分强调。",
      "ranking_misalignment": "学生把'ARB诱发'列为第2-3位，但实际这应该是首选。原因：(1)患者在ARB使用期间咳嗽，(2)干咳不伴其他症状（排除感染），(3)时间线吻合（ARB起效与症状出现的相关性）。",
      "incomplete_ddx_consideration": "学生提到'感染'但未给出充分理由。实际上干咳+夜间加重+无发热这一组合，用于排除急性感染。"
    },
    "recommendation": "在每一份问题表征中，学习显式标注'语义修饰符及其临床含义'。例如：'干咳（暗示非感染性病因）'，而不是仅列举症状。这样问题表征本身就能更好地约束合理的DDx。"
  },
  "suggested_rewrite": {
    "original": "患者是老年男性，有两周咳嗽...可能与药物有关...",
    "improved": "67岁男性，在ARB治疗期间出现2周干咳，夜间加重，无全身症状。临床特征高度提示药物副作用，需考虑停药或换药。继发感染可能性低（无发热、症状干燥）。"
  }
}
```

**关键点**：
- 这个案例展示了 LLM 如何对"问题表征"这一中间步骤进行细致评估
- 评分指出了学生"想法大方向对，但在语义精度和优先级上仍有改进空间"
- 建议包括"如何改写表征"，使学生能学到"更好的临床表述方式"

---

## 三、置信度与验证机制

仅靠单个 LLM 的评分是不够的。为了确保评估的可靠性，系统需要实现一套**置信度判断与人机路由**机制。

### 3.1 多模型合议（Panel of LLM-Judges）

在关键评估点（如 DDx 诊断准确性、安全性评估），系统调用 2–3 个不同的 LLM 或相同 LLM 的多次采样，生成多份独立的评分。

**工作流**：

```
学生回答
  ↓
LLM_A 评分 → 输出 score_A, confidence_A
LLM_B 评分 → 输出 score_B, confidence_B
LLM_C 评分 → 输出 score_C, confidence_C
  ↓
计算模型间一致性 (agreement_score)
  ↓
IF agreement_score > 0.85:
  → 使用平均分，标记为"高置信度"
ELSE IF agreement_score > 0.70:
  → 使用平均分，但标记为"中置信度"，附加"人工复核推荐"
ELSE:
  → 不自动评分，直接推送给教师评估
```

**例子**：在 DDx 危险诊断覆盖度评估中，

| 维度 | LLM_A | LLM_B | LLM_C | 平均 | 一致性 | 路由决策 |
|------|-------|-------|-------|------|--------|---------|
| 危险诊断遗漏 | 0.0 | 0.0 | 0.2 | 0.07 | 0.95 | **高置信** → 自动标记为"严重问题" |
| DDx 排序质量 | 2.5 | 2.7 | 2.4 | 2.53 | 0.92 | **高置信** → 接受评分 |
| 理由完整性 | 3.2 | 3.5 | 3.0 | 3.23 | 0.88 | **高置信** → 接受评分 |

如果三个模型中任何一个的评分偏离过大（例如 LLM_C 给出 4.5 而 LLM_A 给出 2.0），系统会检测到 agreement_score 过低，自动转换为"人工复核模式"。

### 3.2 一致性检验（Consistency Validation）

对于同一份答卷，在不同评估维度之间也应该有**逻辑一致性**。例如：

- **"过程得分高但结果得分低"的不一致**：这可能是合理的（学生推理逻辑好但医学知识有误），也可能反映 LLM 评估的问题。系统应标注这种不一致并提示人工复核。
  
- **"完整性高但排序质量低"的不一致**：这可能提示 LLM 的评估维度定义有歧义。

**一致性检验逻辑**：

```json
{
  "consistency_checks": {
    "process_vs_result_alignment": {
      "process_score": 3.75,
      "result_score": 1.08,
      "discrepancy": 2.67,
      "is_anomalous": true,
      "explanation": "高过程分配合低结果分配通常提示：医学知识不足而非推理能力问题。建议人工验证。"
    },
    "completeness_vs_appropriateness_alignment": {
      "completeness": 3.0,
      "appropriateness": 4.0,
      "discrepancy": -1.0,
      "is_anomalous": false,
      "explanation": "学生列了少诊断，但质量都不错。正常的权衡模式。"
    }
  },
  "overall_consistency_score": 0.72,
  "flags": ["需要人工复核因为 process/result 比失衡"]
}
```

### 3.3 人工复核阈值与路由

系统根据"置信度"与"一致性"，自动决定是否推送给教师：

```
IF confidence > 0.90 AND consistency > 0.80:
  → "完全自动评分，不需人工复核"
  → 教师可在 dashboard 中一键接受

ELSE IF confidence > 0.80 AND consistency > 0.70:
  → "自动评分，但标记为'需要教师审查'"
  → 教师看到评分时，会看到红色标记与理由

ELSE IF confidence > 0.70 OR 存在安全性相关的维度:
  → "混合人机评估：LLM 预评，教师最终决策"
  → 教师看到 LLM 的分析与建议，决定同意或覆盖

ELSE:
  → "仅供参考，需完全人工评估"
  → LLM 评分标注为 [Draft]，不用于正式成绩
```

**例子**：

对于上文 DDx 案例（学生遗漏主动脉夹层），系统的路由决策：

```json
{
  "confidence_assessment": {
    "llm_agreement": 0.93,
    "consistency_check": 0.78,
    "safety_dimension_involved": true,
    "critical_error_detected": true
  },
  "routing_decision": "TEACHER_REVIEW_REQUIRED",
  "priority": "HIGH",
  "summary_for_teacher": "系统检测到学生诊断列表中遗漏了'主动脉夹层'。该诊断在此病例中属于'致命遗漏'。建议教师立即与学生讨论并提供纠正反馈。",
  "suggested_action": "教师决定是否同意 LLM 的'0分（dangerous diagnosis awareness）'评分，或基于教学需要调整为部分分数。"
}
```

### 3.4 动态校准（Adaptive Calibration）

系统持续收集"LLM 评分 vs 教师最终判断"的数据，用于动态调整 prompt、阈值与维度定义。

**校准流程**：

1. 初始阶段：LLM 评估所有学生答卷
2. 教师复核：特别是那些 confidence < 0.85 的评分
3. 比对分析：
   - 如果 LLM 和教师 80%+ 以上一致 → 置信度阈值可提高
   - 如果某个维度频繁不一致 → 调整该维度的 prompt 和定义
   - 如果某类题型（例如"安全性判断"）出现偏差 → 针对性优化
4. 反馈循环：每个学期更新 rubric 与 LLM 参数

示例日志：
```
日期: 2026-01-15
维度: dangerous_diagnosis_awareness
历史准确率: 92% (23/25 次 LLM 评分与教师一致)
调整: 无需调整，保持当前 prompt

日期: 2026-02-20
维度: reasoning_quality
历史准确率: 71% (15/21 次)
调整: 因一致性低，建议教师补充 3-5 个示例到 prompt 中
```

---

## 四、完整的系统架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    学生输入（自由文本）                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         原子化 LLM-as-Judge 工作流                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. 信息提取与标准化                                      │   │
│  │    (Extract & Normalize)                                │   │
│  │ 输出: extracted_statements, extraction_confidence        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. 基准对比                                              │   │
│  │    (Benchmark Comparison)                               │   │
│  │ 输入: reference_answer, evaluation_rubric               │   │
│  │ 输出: match_scores, coverage, novelty_flags             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. 多维度打分                                            │   │
│  │    (Multi-Dimensional Scoring)                          │   │
│  │ 输出: process_scores, result_scores, overall_score      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4. 理由与可解释性生成                                    │   │
│  │    (Rationale Generation)                               │   │
│  │ 输出: dimension_rationales, feedback, suggestions        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              置信度与验证机制                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 多模型合议 (LLM_A, LLM_B, LLM_C)                        │   │
│  │ → agreement_score, consensus_decision                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 一致性检验 (Consistency Validation)                      │   │
│  │ → process_vs_result_alignment, completeness_vs_approp   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 路由决策 (Routing Logic)                                 │   │
│  │ IF confidence > 0.90 & consistency > 0.80               │   │
│  │   → AUTO_ACCEPT                                         │   │
│  │ ELSE IF confidence > 0.80 & consistency > 0.70          │   │
│  │   → TEACHER_REVIEW                                      │   │
│  │ ELSE                                                     │   │
│  │   → HUMAN_ONLY                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              输出给教师与学生                                     │
│  - 结构化评分 + 多维度分解                                       │
│  - 清晰的理由与改进建议                                         │
│  - 置信度标记与人工复核提示                                     │
│  - 可视化 Dashboard（趋势分析、弱点识别）                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 五、总结与实施要点

### 核心优势

1. **可复用性**：同一套 LLM 工作流可在临床推理的任意步骤（线索获取、表征、假设生成、假设评估、反思）应用。
2. **透明性**：每个评分都附带可理解的理由，学生与教师都能看到"为什么这样打分"。
3. **安全性**：多模型合议与一致性检验确保高风险评估（如诊断遗漏）不会被遗漏。
4. **可迭代**：系统持续收集"LLM vs 教师"的比对数据，用于动态改进评估质量。

### 实施步骤

1. **第一阶段**：在单个推理步骤（如 DDx）上验证工作流可行性。
2. **第二阶段**：扩展到其他步骤，统一输入输出接口。
3. **第三阶段**：部署置信度与路由机制，收集人工反馈。
4. **第四阶段**：基于反馈进行动态校准，逐步降低人工依赖比例。

### 预期效果

- 教师从"手工逐个打分"解放出来，转向"基于 LLM 建议的高层审查"。
- 学生获得**即时、可解释、细致的反馈**，而非黑盒式的总分。
- 系统持续学习，变得越来越可靠。
