import fastapi_poe as fp
import os
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError, field_validator
import yaml

def load(path: str | Path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    try:
        return raw
    except ValidationError as e:
        # 这里可以打印更友好的错误信息
        print("配置文件格式/内容错误：")
        print(e)
        raise

config = load(Path(__file__).parent / "config.yaml")

# Use the Poe Python SDK
api_key = config['base']['api_key']
message = fp.ProtocolMessage(role="user", content="Can you see my previous messages?")
print(message)

for partial in fp.get_bot_response_sync(
    messages=[message],
    bot_name=config['model'][0],
    api_key=api_key
):
    print(partial.text, end='', flush=True)



