from enum import Enum

class DebugConfig(Enum):
    FAKE_POE: str = "fake_poe"
    REAL_POE: str = "real_poe"
    

class MetaSettings():
    debug: DebugConfig = DebugConfig.FAKE_POE

# 最常见：模块级单例，其他地方直接 import settings
meta_settings = MetaSettings()
