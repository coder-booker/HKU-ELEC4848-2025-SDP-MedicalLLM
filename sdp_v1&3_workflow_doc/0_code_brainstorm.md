# 11号之前
## Plan
1. 打通api
2. 构建事物



## graph‑based workflow / DAG orchestration
- 对象
    - dataclass
        - PoeAPIMeta：Meta data for using PoeAPI, eg api key, base url
        - PoeChatbotMeta: meta data of different chatbot, now only 'gpt5.1'
        - Workflow: identify the workflow, currently only one
        - TaskMeta: meta data of a task
        - Context: overall context of one workflow or one conversation
        - Message: the history message, encapsulate the 'fp.ProtocalMessage' for context manager
        - Prompt: the prompt of a task
    - workclass
        - Frontend: ignore first
        - Task: the task
            - TaskMeta
            - Prompt
            - PoeChatbotMeta
            - Message
            - Context
        - Engine: to run tasks. Currently supporting only single agent & self-refine
            - Context (overall): cumulated history conversation
        - Context Manager
            - to mangage context in a workflow. Currently supporting only concat history message. 
        - PoeAPI
            - PoeChatbotMeta
            - PoeChatbot: encapsulate the access of different chatbots

## workflow engine
- 角色是什么？
    - 编制 Task （把他们的input output 按照 type 连起来
    - 运行 Task
    - 与 UI 交互渲染内容

## Task
- Task 的角色是什么？
    - 执行原子化的访问
    - 上下文要管理吗？不需要，只要接收然后组织好 input，chat 并 组织 output 即可
1. internal 配置
    - 模型配置
    - 行为
    - prompt
2. inter-tasks 的协作
    - todo
3. 具体成员属性
    - task_id
    - act_type
    - act_attr
        - target_ids （为了多agent）
        - 身份
    - prompt
    - context
    - messages: list[ProtocolMessage],
    - bot_name: str,
    - api_key: str,
    - *,
    - tools: Optional[list[ToolDefinition]] = None,
    - tool_executables: Optional[list[Callable]] = None,
    - temperature: Optional[float] = None,
    - skip_system_prompt: Optional[bool] = None,
    - adopt_current_bot_name: Optional[bool] = None,
    - logit_bias: Optional[dict[str, float]] = None,
    - stop_sequences: Optional[list[str]] = None,
    <!-- - base_url: str = "https://api.poe.com/bot/", -->
    - session: Optional[httpx.AsyncClient] = None,
4. 具体成员方法
    - .init 解析所需资源
    - .fire 运行（包含了结果的实时记录
- Messgae
    - core: ProtocolMessage
        - role
        - content
    - simplified: boolean （for context simplier）
- Engine
    - 方法
        - .start 开始解析、运行、记录 task
        

## 上下文管理
- 触发策略：
    - 对话长度
- 触发后行为：
    - 全部保留
    - 直接切断
    - 人为精简
    - AI 精简


## Poe 接口
- 模型
    - gpt5.1先
    - todo
- 方法
    - get_response 非常够用
    - todo
- 参数
    - todo


- 当前进度：
    - 由于需要修改 task 的整个架构（引入 artifact ，适配 context，适配 prompt，引入 workflow），正在慢慢修改
    - 还把各种东西解耦了：
        - engine 就真的只负责运行 task，task是怎么样还得 task 和 workflow 来决定
        - task 和 上下文的管理解耦了，由 workflow 管理上下文
        - prompt 单独拎出来，同时引入 i18n


- messages 和 我自己拼接 有区别吗？
    - 有吧，后者我可以自己编好历史记录的意义，甚至进一步后处理一下，而前者会让 llm 多了一层‘判断此前在干嘛’的步骤，且不利于后处理（因为 message 本身和后处理的信息意义并不一样，不能替换）






# 11/01/2026
- 在调整方向后，重新出发
- 依然是工作流相关，但要为医学研究者提供遍历，例如
    - 能够一键复现论文内容（提供模板）
    - 能够方便地自制工作流（抽象一些医学工作的节点）
    - 更容易看明白在干啥（语义更加简单，而不是现在的只有技术人员才看的懂）
- 需要注意的新东西
    1. 模板类/paper 类
    2. 节点抽象类（医学推理的各个步骤）
    3. benchmark 类
- 难点
    1. 原子化工作流的难点之一就是 prompt 很难拼接
        - 例如我希望把上一次的回答嵌入下一次 llm 的输入 prompt 中，应该怎么设计？
            - 参数化的模板似乎可以解决这个问题
    2. benchmark 其实会反过来影响前面的 llm 的 prompt
        - 例如：MedQA 只包含选择题和选项，PubMedQA则是短答题和简短解释，而两者要求 LLM 的输出和评估方法不太一样。前者只需要输出 ABCD 并直接字符串对比答案，后者则需要输出短答并 LLM-as-judge。对于同一种工作流，如何适配这两种 benchmark 需要仔细设计
        - 


- brainstorm on 哪些东西会有冲突，需要仔细进行代码设计以解决
    - 临床任务
        - 分科
        - 病例撰写
        - 临床推理
        - 治疗方案
    - 临床推理阶段
        - 病例框架化与情境设定
        - 线索获取
        - 问题表述
        - 假设生成
            - 不保留原病例（prompt chaining 的话），只基于问题表述生成假设
        - 假设评估与收缩
            - 获得最终诊断，用自然语言渲染
            - 可以选择终止循环还是继续循环。这一点需要与交互式配合，所以未必需要现在做
    - 工作流相关
        - Self-refine
            - 单 self-refine 和 多 self-refine（真的有必要做多 self-refine 吗？你仔细想想，到了多 self-refine 时，我们其实还是在叫具体节点重新生成其内容，并不会带上其他节点的 review 上下文。而如果带上了其他节点的 review 上下文，这就让这个 chain 破裂了：下游依赖于上游的 refined 结果来生成新结果，这导致必须要节点一个接一个 refine，上下文只剩下上个节点的 refine 记录，而这个记录对于不同的 task 其实没什么用，因此不需要多 refine）
            - Self-refine 对于任何阶段都可以使用，理应作为一种高层功能嵌入到每个节点中
        - CoT
            - 和 prompt chaining 可以同时出现，并不冲突
        - Self-consistency
            - 作为一个独立的节点吧，获取链接的节点输出，保留它们的上下文作为一个合适的 prompt
    - benchmark 相关
        - 输出过程
        - 输出 QA 结果
        - 输出短答结果


    - 光是临床推理阶段本身已经有很多奇怪的问题了
        - brainstorm
            - 这些阶段完全可以在一个 CoT 中完成，但同时也可以拆开完成以供细粒度的工作流调整
                - 例如可以把 DDx 阶段单独用 Self-consistency 完成，其他仍然是一轮
                - 可以分为单次和分次的‘临床推理’
                - 这属于 CoT 和 prompt chaining 的区别了
            - 似乎临床推理的阶段都最好把所有上下文都保留？
                - 线索获取在交互式的阶段在可能有变数，不然线索就是题干本身
                - 问题表述的上下文只有 prompt 和原病例
                - 假设生成阶段似乎可以选择保留或不保留原病例，但保留的话与 self-refine 的职能有些重复了？
                    - 感觉得看看 paper 中对工作流的上下文是怎么设计的，现在似乎最好是把所有上下文都保留，但这和 CoT 就没有区别了
                - 假设评估需要获得足够的上下文吗？得知思考过程或许有助评估的决策
                    - 首先，假设评估无法独立，必须要在假设生成之后出现
                    - 哪些上下文是值得给假设评估的？问题表述与假设生成吗？
                        - 如果线索获取没有什么花活儿（比如交互式获取线索），那么原病例、问题表述、假设生成之中，只有原病例不需要保留，其余都保留
                    - 假设拥有重启临床推理的能力，因此需要所有的上下文，以此判断从哪一步重启。
            - 假设评估开启新一轮循环时，需要对新一轮的上下文进行什么安排吗？
                - 需要的吧，不然怎么反馈并制作差异化的新内容？
                - 是不是需要限制循环的范围？
                    - 不需要，一开始的问题表述就有可能有缺漏，因此把所有上下文都丢给它就行
                - 要让这个节点能够自己挑选从哪个阶段开始重做吗？
                    - 要
                - 还需要限制循环轮次
            - 假设评估需要交互式诊断的配合才能完成，不然没有新的信息进入，再怎么评估结果也没有区别
            - 假设评估有两种职能，这或许需要区分
        - 结论
            - 得看看 paper 中的工作流是怎么设计的，现在似乎最好是把所有上下文都保留
            - 假设评估需要获得所有上下文，需要限制循环轮次，但需要交互式诊断的辅助以提供新资讯，同时需要以某种方式把此次循环的结果告诉下次的循环（不只是新资讯）
            - 假设评估还有一种职能：从当前假设得出最终诊断，可能需要进一步拆分，与交互式循环的职能做出区分

    - CoT 和 Prompt-Chaining 其实天生就有冲突
        - brainstorm
            - Prompt-Chaining 会有细粒度高，能客制化上下文、交互任务、输入输出格式的优势
            - CoT 则有 token 更少、延迟更低的优势
            - 可以做两套，一套基于 CoT ，一套基于 prompt chaining
        - 结论
            - 两者完全可以共存。它们各有优劣，取决于用户想要用哪套就行
            - 把 CoT 单独做成一个节点，用来彰显其作为一个关键工作流的重要性
    
    - 特殊工作流节点的上下文需要被全部传递吗？
        - brainstorm
            - self-refine 与 self-consistency 结合时，refine consistency 本身这点没错
            - 假设评估与 self-refine 结合时，不会直接爆炸吗

    - benchmark
        - brainstorm：
            - benchmark 的冲突没有想象中那么大
                - 对于 QA 和 短答结果，只有一个‘是否输出解释’的步骤差异而已
                - 对于 过程 的评估，实际上 CoT/prompt chaining 本来就在做类似的事，只要提取这一点并对比答案就行了。
                - 但对于 QA vs 过程这一点，如果工作流中没有任何 reasoning 的引导，其实无法进行评估。因此对于过程的评估，可能需要纠错机制：LLM 智能提取过程，在发现上下文中并没有保留能够进行评估的点就报错（function call）。同时把 benchmark 中的过程推理显性告诉使用者（类似 mc 蓝图的‘虚影’），供使用者参考匹配。
                - 智能提取必须要和 benchmark 配套出现，分开两者会导致智能提取需要手动获取下游的benchmark类型来决定提取什么，这不太符合我们的工作流设计
                - 智能提取和虚影模板还可以用来对 QA 与 短答结果 的差异进行磨合。
            - 数据可视化
                - 把 benchmark 的结果自动画图，这一点蛮麻烦的。不过还是和benchmark结合在一起
        - 结论
            - benchmark 的类型确实会限制上游节点的类型
                - 但智能提取器可以削减这一点限制
                - 再加上我们把这种限制通过虚影模板下放给用户来搭建，进一步削减这点显示
                - 结合报错机制，benchmark 的可行性能够保证
                - 值得注意的是
                    - 智能提取必须要和 benchmark 配套出现
                    - 忽略报错可能也可以提供
            - 自动画图
                - 和 benchmark 结合在一起，例如作为一个可选项在节点中提供


# 12/01/2026
- 今天因为效率出了点问题，先做一些元工作
    - 先根据11号的结果把整体框架搭好
        - 确定各模块和职能边界
            - 如果把上下文交给 Task 管理，engine的职能就不那么重要了，或许把 engine 整个剔除算了，由 workflow 同时管理配置和 task 运行
            - 基于类似 DDD 的架构，分为四层
    - 排列优先级
        - 明天再说

# 17/01/2026
- 我们的核心卖点到底在哪？为什么能更好用？
    - 语义化？现在的语义怎么不好用了，我的语义怎么好用了？
        - 只能说‘做了瘦身’吧，可以对比一下已有平台中有哪些概念是需要知道的，对比我们的平台有哪些概念是需要知道的
    - 临床阶段？但其实这和灵活度是相违背的，你很难在保留灵活度的情况下，专门为临床阶段提供节点
        - 这一点我觉得确实需要认真思考，不然没法做下去，这一点是唯一一个未知的卡点
        - 而且所谓的‘提供医学节点’，真的能更可用吗？
    - paper 模板？这一点其实还行
        - 为医学研究者提供复现的现成代码，也算是一种示例
        - 提供模板虚影，供依照 paper 的工作流设计新的工作流
    - benchmark？这个估计是唯一比较有价值的点了，包括分类和智能提取器
- 把路径打通了先，给点自信
- 让 task 返回 context



- 任务树！！


# 18/01
- poe client 先用单例模式


# 19/01
- 过一遍整个基础流程就可以开测了
- 还得建立一个简易的 benchmark protocal

- 现在的做法是 纯文本 task，但多 task 需要分叉，需要设计协议（统一 or map）和分叉代码（if or map）


# 21/01
- 今天要面试，然后又摆烂了一整天，能用来开发的时间不多，所以今天的工作量应该不多
- 目前要做的是
    1. 跑一遍真测试
    2. 构建好那几个重要的推理流程节点
    3. 把那几个先遣的工作流写好（就写一个吧）
    4. 研究下 Dify 这类平台有多难用，对比我的有多好用
    5. PPT
    6. 发 zoom 链接和参考的 ppt
- 巨量的 TODO 的一小部分：
    - 前端和后端的 id 要分开还是同步？
        - 理想的情况是，前端创建新 entity 时会访问后端要一个 id，所以 id 以后端为主
    - input 和 output 应该怎么展示给 ai 看上下文？还是把所有东西都拼接到一个字符串中？



# 22/01
- ref
    - 研究痛点：医学推理 LLM 的 workflow 研究高度碎片化，论文通常只提供为其特定实验写的一次性代码，导致复现成本高、难以做公平对比与消融实验。
    - 项目目标：实现一个面向医学研究者的轻量级 workflow 编制与评估框架，用医学语义节点（如 DDx 生成、证据对齐、结论一致性检查）来替代通用平台的技术节点组合，从而降低配置复杂度与复现时间，**降低复现与迭代医学推理工作流的门槛**
    - 轻量化定义与验证：以“Time-to-first-run、配置项数量、复现实验成功率”为核心指标，比较本框架与通用平台/手写代码在复现指定 baseline 工作流时的成本差异，并给出可重复的测量过程。
    - 学术边界：不声称提出新的医学推理算法，而是提供可扩展的系统工具，使研究者能在统一接口下评估不同工作流/模型的质量-成本权衡；这与 MedHELM 一类评测框架的目标互补。
- ppt 的架构：
    1. intro + motivation：
        1. 我们的主题是 ‘Medical Reasoning LLM’
            - 我看了数十篇 paper ，发现这个领域中已经有大量的研究: Dataset 预处理, llm 工作流设计和横向对比, 评估 llm 在医学任务表现的维度等等
            - 我发现了一个问题：在现在各种 llm 配套工具如此发达的情况下，几乎所有公开了代码的 paper ，都是自己从头写的代码，并没有借助例如 LangChain 这种开源库，甚至没有借助别的 paper 给出的代码，即便他们中的很多都是重复工作，例如访问 llm api ，设计并建立工作流和 prompt 等
            - 我想优化这个问题，降低复现与迭代医学推理工作流的门槛，不需要完全从头写代码
        2. 痛点：想要做 workflow 研究需要自己写代码，成本过高
            - **TODO** ：为什么大伙儿不用现有的东西？**搜一下消息来源**，下面是个人推测的原因：
            - 通用平台：人们认为通用平台很难用
                - **为技术人员而设**，语义性和易用度对于医学研究者都有一定门槛（将那些通用技术节点转换为医学步骤其实有些门槛）
                    - 例子：（要重点阐述为什么技术会有，但对于医学人来说没什么重要的）
                        - 获取题目并运行
                            - 重要的是：
                                - 题目怎么集成到工作流的一部分（例如 prompt 中）
                            - 不重要的是：
                                - 题目怎么储存（csv文件？blob文件？json文件？）
                                - 题目怎么访问（数据协议，设定列与行与工作流的关系）
                                - 更不重要的事儿（发布工作流）
                - **缺乏验证功能**
                    - 并没有很直接的 benchmark 集成功能
                    - 其实用一些扭曲的方法也可以，但因为 dify 这类平台本意就是相对 standalone 的，所以很难说很好用：
                        - 输出为文件，保存到本地之后跑本地代码（不利于自动化）
                        - 输出文件到自定义 http 中，但这就更加麻烦了（需要网络知识部署）
            - 现有 paper 的代码
                - 都是为了特定目的而写的一次性代码。当然可以用其公开的代码，但很多时候如果想要从其上拓展，一次性代码并不好用，还是得自己写代码
        3. 总结：**轻量级医学 workflow 编制与评估框架，降低复现与迭代医学推理工作流的门槛**：
            - 将现有的大量学术工作与工程工作组合起来，整合为一个统一的平台
                - 支持快速切换/编制不同工作流（相关 paper 实验过的工作流模板，医学语义节点（如 DDx 生成、证据对齐、结论一致性检查）等）
                - 支持快速应用各种 benchamrk
                - 抽象，简化，无需太多前置知识，降低配置复杂度
            - 保留代码可用性
                - 我们清除地知道平台永远无法满足所有要求，所以我们也会将代码设计得更灵活和易于拓展
                - 保持代码的简洁性：去除过于硬编码的技术概念，将灵活度拉满
                - 让任何人即便有需要代码解决的问题，也有一个现成的基底能够快速拓展
    2. how
        - Engineering persp: 
            1. 类似 dify/flowise/langraph 的平台，但
                1. 提供一键跑 benchmark 功能，可视化图表
                    1. 基础 benchmark 功能
                        1. dataset
                            1. MedQA
                            2. PubMedQA
                            3. MedRBench
                            4. ...
                        2. 可选的 metrices
                            1. accuracy
                            2. ...
                    2. 可视化图表
                        1. 没什么好说的
                2. 提供 function, component, recipe
                    1. funciton: 将各种 prompt engineering 的技巧都结合到平台中方便一键应用
                        - self-refine（直接嵌入节点中，可以一键开关）
                        - CoT（提供 prompt 模板供填入，手动输入一步一步）
                        - self-consistency（提供连接好的节点 set 模板，包含一组 sub llm 和一个 main llm）
                    2. component: 根据现有 paper 提炼出的医学语义节点
                        1. 线索表达节点（把 benchmark 输入的问题结构化表达）
                        2. 假设生成节点（DDx，生成可能的诊断）
                        3. 假设评估节点（对诊断进行评估，并选出最终诊断）
                    3. recipe: 根据现有 paper 提供一键复现流程
                        1. 基础推理架构
                        2. 拥有过程推理评估的架构
                        3. 证实有效的多 agent 架构
                3. 轻量化
                    1. 去除不需要的功能/代码
                        - 代码撰写/编译/运行
                        - 第三方工具集成
                        - 市场功能
                        - MCP server
                        - api
                        - sdk
            2. 留出代码上的可用性
                1. 模块内聚
        - Acedemic persp:
            - medical reasoning
                - 基础推理：3 个步骤
                    1. 线索表达（把 benchmark 输入的问题结构化表达）
                    2. 假设生成（DDx，生成可能的诊断）
                    3. 假设评估（对诊断进行评估，并选出最终诊断）
            - Benchmark
                - 现有有很多benchmark，但都只专注于 benchmark 而非整个流的整合
                1. dataset
                    1. MedQA
                    2. PubMedQA
                    3. MedRBench
                    4. etc
                2. metrices
                    1. result-based
                        1. Accuracy（准确性）：最终答案与金标准的匹配度（Top-1，Top-N） 
                        2. Appropriateness（合适性）：评估每个诊断是否合理地适合这个病例
                        3. Comprehensiveness（全面性）：评估诊断是否足够全面
                        4. Sensitivity（敏感性）：是否出现过度自信或危险建议
                    2. process-based
                        1. Conciseness/Efficiency（简洁性/效率）：所输出内容是否足够简洁有效，是否有信息增量，是否有冗余内容
                        2. Factuality（真实性）：符合医学指南/知识的有效步骤占比
                        3. Completeness（完整性）：模型输出覆盖的"金标准推理步骤"占比
                3. popular benchamrk （进一步集成一些更复杂的 benchmark）
                    1. eg：MedHELM https://crfm.stanford.edu/helm/medhelm/latest/#/
    3. 对平台本身的 evaluation
        - 验证我们的解决方案是否真的有效
            1. 对比通用平台的硬性步骤
            2. 让医学生实际操作，并给出反馈
            3. 尝试一个简易的研究课题来验证其可用性
    4. Discussion
        1. 当前进度：核心可拓展代码已经完成，已经根据系统需求留下了大量接口，接下来填补所有功能和开发前端即可完成，没有什么大规模的开发任务需要处理
        2. 学术边界：不声称提出新的医学推理算法，而是提供可扩展的系统工具，**降低复现与迭代医学推理工作流的门槛**，使研究者能在统一平台下更方便地评估不同工作流的质量-成本权衡
    5. Conclusion



- 要做的事
    1. 研究下 Dify 这类平台有多难用，对比我的有多好用
        - 设置步骤
        - 概念数量

    2. 跑一遍真测试
    3. 构建好那三个重要的推理流程节点
    4. 把那几个先遣的工作流写好（就写一个吧）
   
    5. 赶紧把我的 benchmark eval 和可视化 和 新节点和其 prompt 设置好
    6. PPT
    7. 发 zoom 链接和参考的 ppt



- MVP
    - 核心任务：通过三个临床推理步骤来回答 json 格式的 benchmark 提供的问题
    - 【没什么问题】三个临床推理步骤
        1. 线索表达（把 benchmark 输入的问题结构化表达）
        2. 假设生成（生成可能的诊断）
        3. 假设评估（对诊断进行评估，并选出最终诊断）
    - 具体 benchmark
        - MedQA ，一个 json 的多选医疗知识题
        - 先只对比准确度，但仍然支持可视化
    - 用于对比 dify 和我的平台的差异的工作流例子
        1. 使用 CoT 单论对话
        2. 使用三个 agent 分别完成一个步骤
        3. 有 self-refine 的基础单论回答



- Dify 要怎么实现
    - CoT
        - 结构化 prompt
    - 三个 agent
        - 结构化 prompt 和
    - benchmark
        - csv 加载数据库
        - 跑分相关
            - param extractor or json 结构化输出提取用于对比的文本答案
            - 没有一站式可视化和对比标准挑选

- 我们的优势：
    - 对于医学实验，有几乎一站式的功能
        - prompt 和工作流的预设置
        - benchmark 的预设置
    - 对于推理相关的内容，我们都有自己
