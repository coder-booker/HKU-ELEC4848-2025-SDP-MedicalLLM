# import httpx
# import json

# # 填入你出错时使用的真实参数
# api_key = "sk-poe-5zk_gqVbGOiNq5Fykxgoof2zvQh_fn21fjeZmiUrQ9M"  
# bot_name = "Claude-3-Haiku"  # 填入你代码中的实际值

# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json"
# }

# payload = {
#     "query": [{"role": "user", "content": "hello"}],
#     "version": "1.0",
#     "type": "query",
#     "user_id": "test_user",
#     "conversation_id": "test_conv",
#     "message_id": "test_msg"
# }

# # 直接向 Poe 的网关发请求，不使用 stream
# response = httpx.post(
#     f"https://api.poe.com/bot/{bot_name}", # 注意：Poe内部路由可能会将bot_name拼在路径或参数里
#     headers=headers,
#     json=payload
# )
# print(response)
# print(f"状态码: {response.status_code}")
# print(f"Poe 服务器真实返回内容: {response.text}")






import fastapi_poe as fp
import asyncio

api_key = "sk-poe-5zk_gqVbGOiNq5Fykxgoof2zvQh_fn21fjeZmiUrQ9M"
message = fp.ProtocolMessage(role="user", content="Hello world")

async def main():
    async for partial in fp.get_bot_response(messages=[message], bot_name="GPT-5.4", api_key=api_key):
        print(partial.text)
asyncio.run(main())