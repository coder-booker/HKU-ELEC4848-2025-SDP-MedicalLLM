"""SmartExtractor 领域模型。"""

from enum import Enum
from typing import Any, Dict, Optional, TypedDict

from pydantic import BaseModel, Field


class SmartExtractionResult(TypedDict):
    """
    - raw_response: str - LLM 的原始输出文本
    - extracted: Dict[str, Any] - 从原始输出中解析出的结构化数据，键值由 expected_schema 定义
    """

    raw_response: str = ""
    extracted: Dict[str, Any]
