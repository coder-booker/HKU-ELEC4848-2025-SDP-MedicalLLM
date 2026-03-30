"""全局运行时元配置。

该模块用于控制跨模块共享的运行模式（例如真假 Poe 调用）。
"""
from enum import Enum

# class DebugConfig(Enum):
#     """调试模式枚举。"""
#     FAKE_POE: str = "fake_poe"
#     REAL_POE: str = "real_poe"


class MetaSettings():
    """运行时元配置对象。"""
    # 默认走假响应，便于离线开发调试。
    debug: bool = True

# 最常见：模块级单例，其他地方直接 import settings
meta_settings = MetaSettings()
