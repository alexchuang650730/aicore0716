"""
PowerAutomation 启动触发 MCP
基于钩子系统和 Mirror Code 双向机制的智能触发系统
"""

from .startup_trigger_manager import (
    StartupTriggerManager,
    StartupTriggerConfig,
    startup_trigger_manager
)
from .trigger_detection import (
    TriggerType,
    TriggerEvent
)

__version__ = "4.6.9.6"
__author__ = "PowerAutomation Team"

__all__ = [
    "StartupTriggerManager",
    "StartupTriggerConfig",
    "startup_trigger_manager",
    "TriggerType", 
    "TriggerEvent"
]

