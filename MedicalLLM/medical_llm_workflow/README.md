# overall structure (17/01/2026)
- Controller
    - 与前端的交互/运行入口
- Service
    - 上层业务代码，或者说是非核心业务的业务（例如鉴权，调度等等）
- Domain
    - 核心业务代码
- Infrastructure
    - 基建，例如 api, client 等


# current tasks
- 将最新的架构疏通好先
    - 各类 schemas 配置好
- 继续开发最小 mvp
    - MedQA benchmark
    - 几种简单的 workflow
    - 复现一两篇 paper 的工作流
- 之后可以考虑用热门的库来实现类似效果，看看够不够好用