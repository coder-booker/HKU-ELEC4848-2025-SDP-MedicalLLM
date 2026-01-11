from __future__ import annotations

from typing import AsyncIterable, List
import fastapi_poe as fp

ANALYST_BOT = "gpt-5.1"   # 你在 Poe 里配置的基于 GPT‑5.1 的 bot 名
CRITIC_BOT = "My-GPT51-Critic"    # 另一个基于 GPT‑5.1 的 bot 名


class MultiAgentBot(fp.PoeBot):
    async def get_settings(
        self, setting: fp.SettingsRequest
    ) -> fp.SettingsResponse:
        # 声明依赖的其他 bot（名字要和 Poe 前端显示的一致）[web:39]
        return fp.SettingsResponse(
            server_bot_dependencies={
                ANALYST_BOT: 1,
                CRITIC_BOT: 1,
            }
        )

    async def call_bot_once(
        self,
        request: fp.QueryRequest,
        bot_name: str,
        system_prompt: str | None = None,
    ) -> str:
        """
        调用某个 Poe bot 一次，返回完整文本。
        可以在这里插 system prompt，做角色控制。
        """
        messages: List[fp.ProtocolMessage] = []

        if system_prompt:
            messages.append(
                fp.ProtocolMessage(role="system", content=system_prompt)
            )

        # 把用户的原始输入透传过去（这里只拿最后一条 user 消息）[web:31]
        last_user = next(
            (m for m in reversed(request.query) if m.role == "user"),
            None,
        )
        if last_user:
            messages.append(
                fp.ProtocolMessage(role="user", content=last_user.content)
            )

        # 调用目标 bot（这里会实际用到 GPT‑5.1 之类的闭源模型）[web:39]
        chunks: List[str] = []
        async for part in fp.stream_request(
            fp.QueryRequest(query=messages),
            bot_name,
            request.access_key,
        ):
            if part.text:
                chunks.append(part.text)

        return "".join(chunks)

    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        # 1. 调用 Analyst agent
        analyst_answer = await self.call_bot_once(
            request,
            ANALYST_BOT,
            system_prompt=(
                "你是一个负责草拟解决方案的专家助手。"
                "先用条目列出分析思路，再给出一个初步方案。"
            ),
        )

        # 2. 调用 Critic agent，让它评审 Analyst 的回答
        critic_prompt = (
            "下面是另一位助手给出的方案，请你以严格审稿人的身份"
            "指出其中不清晰、不完备或可能错误的地方，并给出改进后版本。\n\n"
            f"对方的方案如下：\n{analyst_answer}"
        )
        critic_request = request
        # 这里只简单覆写用户内容，实际可以单独构造 QueryRequest
        critic_request.query = [
            fp.ProtocolMessage(role="user", content=critic_prompt)
        ]

        critic_answer = await self.call_bot_once(
            critic_request,
            CRITIC_BOT,
        )

        # 3. 在你的 server‑bot 里做最终聚合（可以加你自己的逻辑）
        final_text = (
            "【多 Agent 工作流示例】\n\n"
            "一号 Agent (Analyst) 的草案：\n"
            f"{analyst_answer}\n\n"
            "二号 Agent (Critic) 的审稿与改进：\n"
            f"{critic_answer}\n\n"
            "（在真实应用里，你可以在这里再调用一次 GPT‑5.1，让它综合两者输出最终答案。）"
        )

        yield fp.PartialResponse(text=final_text)


if __name__ == "__main__":
    # 本地跑起来测试；部署到 Poe 时换成你习惯的方式（Modal / 自己的服务器 + ngrok）。[web:31][web:39]
    fp.run(MultiAgentBot(), allow_without_key=True)
