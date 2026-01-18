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