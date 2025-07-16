#!/usr/bin/env python3
"""
Startup Trigger Detection - 启动触发检测模块
基于钩子和 Mirror Code 的智能触发机制，解决 Claude Code 自动安装 ClaudeEditor 的问题
"""

import asyncio
import logging
import re
import json
import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class TriggerType(Enum):
    """触发类型"""
    CLAUDEEDITOR_INSTALL = "claudeeditor_install"
    CLAUDEEDITOR_START = "claudeeditor_start"
    MIRROR_CODE_SYNC = "mirror_code_sync"
    DUAL_COMMUNICATION = "dual_communication"
    SYSTEM_READY = "system_ready"

class TriggerPriority(Enum):
    """触发优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class TriggerPattern:
    """触发模式"""
    pattern_id: str
    trigger_type: TriggerType
    patterns: List[str]  # 正则表达式模式
    keywords: List[str]  # 关键词
    context_requirements: Dict[str, Any]  # 上下文要求
    priority: TriggerPriority
    enabled: bool = True
    description: str = ""

@dataclass
class TriggerEvent:
    """触发事件"""
    event_id: str
    trigger_type: TriggerType
    matched_pattern: str
    matched_text: str
    context: Dict[str, Any]
    timestamp: datetime
    priority: TriggerPriority
    source: str

class ClaudeCodeTriggerDetector:
    """Claude Code 触发检测器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized = False
        
        # 触发模式注册表
        self.trigger_patterns: Dict[TriggerType, List[TriggerPattern]] = {}
        self.trigger_history: List[TriggerEvent] = []
        
        # 检测配置
        self.max_history_size = 500
        self.detection_enabled = True
        self.auto_trigger_enabled = True
        
        # Mirror Code 状态
        self.mirror_code_active = False
        self.claudeeditor_installed = False
        self.dual_communication_ready = False
        
        # 初始化触发模式
        self._register_trigger_patterns()
    
    def _register_trigger_patterns(self):
        """注册触发模式"""
        try:
            # ClaudeEditor 安装触发模式
            self._register_pattern(TriggerPattern(
                pattern_id="claudeeditor_install_1",
                trigger_type=TriggerType.CLAUDEEDITOR_INSTALL,
                patterns=[
                    r"(?i).*需要.*claudeeditor.*",
                    r"(?i).*安装.*claudeeditor.*",
                    r"(?i).*启动.*claudeeditor.*",
                    r"(?i).*运行.*claudeeditor.*",
                    r"(?i).*开始.*编辑.*",
                    r"(?i).*打开.*编辑器.*",
                    r"(?i).*需要.*编辑.*界面.*",
                    r"(?i).*启动.*编辑.*环境.*"
                ],
                keywords=[
                    "claudeeditor", "编辑器", "编辑界面", "编辑环境",
                    "需要编辑", "开始编辑", "打开编辑", "启动编辑",
                    "安装编辑器", "运行编辑器", "编辑模式"
                ],
                context_requirements={
                    "claudeeditor_not_installed": True,
                    "user_intent": "edit_or_develop"
                },
                priority=TriggerPriority.HIGH,
                description="检测用户需要 ClaudeEditor 的意图"
            ))
            
            # Mirror Code 同步触发模式
            self._register_pattern(TriggerPattern(
                pattern_id="mirror_code_sync_1",
                trigger_type=TriggerType.MIRROR_CODE_SYNC,
                patterns=[
                    r"(?i).*同步.*代码.*",
                    r"(?i).*mirror.*code.*",
                    r"(?i).*双向.*通信.*",
                    r"(?i).*代码.*镜像.*",
                    r"(?i).*实时.*同步.*",
                    r"(?i).*代码.*同步.*"
                ],
                keywords=[
                    "mirror code", "代码镜像", "双向通信", "实时同步",
                    "代码同步", "同步代码", "镜像同步", "双向同步"
                ],
                context_requirements={
                    "claudeeditor_installed": True,
                    "sync_required": True
                },
                priority=TriggerPriority.MEDIUM,
                description="检测 Mirror Code 同步需求"
            ))
            
            # 双向通信建立触发模式
            self._register_pattern(TriggerPattern(
                pattern_id="dual_communication_1",
                trigger_type=TriggerType.DUAL_COMMUNICATION,
                patterns=[
                    r"(?i).*建立.*连接.*",
                    r"(?i).*双向.*沟通.*",
                    r"(?i).*实时.*交互.*",
                    r"(?i).*连接.*编辑器.*",
                    r"(?i).*启用.*双向.*",
                    r"(?i).*开启.*通信.*"
                ],
                keywords=[
                    "双向沟通", "实时交互", "建立连接", "连接编辑器",
                    "启用双向", "开启通信", "双向连接", "实时连接"
                ],
                context_requirements={
                    "claudeeditor_running": True,
                    "communication_needed": True
                },
                priority=TriggerPriority.HIGH,
                description="检测双向通信建立需求"
            ))
            
            # 系统就绪检查触发模式
            self._register_pattern(TriggerPattern(
                pattern_id="system_ready_1",
                trigger_type=TriggerType.SYSTEM_READY,
                patterns=[
                    r"(?i).*系统.*就绪.*",
                    r"(?i).*准备.*完成.*",
                    r"(?i).*环境.*准备.*",
                    r"(?i).*检查.*状态.*",
                    r"(?i).*系统.*状态.*",
                    r"(?i).*服务.*状态.*"
                ],
                keywords=[
                    "系统就绪", "准备完成", "环境准备", "检查状态",
                    "系统状态", "服务状态", "就绪状态", "准备状态"
                ],
                context_requirements={},
                priority=TriggerPriority.LOW,
                description="检测系统状态查询需求"
            ))
            
            # 特殊的 Claude Code 专用触发模式
            self._register_pattern(TriggerPattern(
                pattern_id="claude_code_special_1",
                trigger_type=TriggerType.CLAUDEEDITOR_INSTALL,
                patterns=[
                    r"(?i).*powerautomation.*setup.*",
                    r"(?i).*claudeeditor.*ready.*",
                    r"(?i).*启动.*powerautomation.*",
                    r"(?i).*初始化.*编辑.*环境.*",
                    r"(?i).*setup.*claudeeditor.*",
                    r"(?i).*init.*editor.*"
                ],
                keywords=[
                    "powerautomation setup", "claudeeditor ready", 
                    "启动 powerautomation", "初始化编辑环境",
                    "setup claudeeditor", "init editor",
                    "准备编辑环境", "编辑器初始化"
                ],
                context_requirements={
                    "claude_code_context": True
                },
                priority=TriggerPriority.CRITICAL,
                description="Claude Code 专用的特殊触发模式"
            ))
            
            self.logger.info("触发模式注册完成")
            
        except Exception as e:
            self.logger.error(f"注册触发模式失败: {e}")
    
    def _register_pattern(self, pattern: TriggerPattern):
        """注册单个触发模式"""
        try:
            if pattern.trigger_type not in self.trigger_patterns:
                self.trigger_patterns[pattern.trigger_type] = []
            
            self.trigger_patterns[pattern.trigger_type].append(pattern)
            self.logger.debug(f"注册触发模式: {pattern.pattern_id}")
            
        except Exception as e:
            self.logger.error(f"注册触发模式失败: {e}")
    
    async def detect_triggers(self, text: str, context: Dict[str, Any] = None) -> List[TriggerEvent]:
        """检测触发事件"""
        try:
            if not self.detection_enabled:
                return []
            
            if context is None:
                context = {}
            
            detected_events = []
            
            # 遍历所有触发模式
            for trigger_type, patterns in self.trigger_patterns.items():
                for pattern in patterns:
                    if not pattern.enabled:
                        continue
                    
                    # 检查上下文要求
                    if not self._check_context_requirements(pattern.context_requirements, context):
                        continue
                    
                    # 检查正则表达式模式
                    for regex_pattern in pattern.patterns:
                        match = re.search(regex_pattern, text)
                        if match:
                            event = TriggerEvent(
                                event_id=str(uuid.uuid4()),
                                trigger_type=trigger_type,
                                matched_pattern=regex_pattern,
                                matched_text=match.group(0),
                                context=context.copy(),
                                timestamp=datetime.now(),
                                priority=pattern.priority,
                                source="ClaudeCodeTriggerDetector"
                            )
                            detected_events.append(event)
                            self._record_trigger_event(event)
                            break
                    
                    # 检查关键词
                    if not detected_events:  # 如果正则没有匹配，再检查关键词
                        for keyword in pattern.keywords:
                            if keyword.lower() in text.lower():
                                event = TriggerEvent(
                                    event_id=str(uuid.uuid4()),
                                    trigger_type=trigger_type,
                                    matched_pattern=f"keyword: {keyword}",
                                    matched_text=keyword,
                                    context=context.copy(),
                                    timestamp=datetime.now(),
                                    priority=pattern.priority,
                                    source="ClaudeCodeTriggerDetector"
                                )
                                detected_events.append(event)
                                self._record_trigger_event(event)
                                break
            
            # 按优先级排序
            detected_events.sort(key=lambda x: x.priority.value, reverse=True)
            
            return detected_events
            
        except Exception as e:
            self.logger.error(f"检测触发事件失败: {e}")
            return []
    
    def _check_context_requirements(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """检查上下文要求"""
        try:
            for key, required_value in requirements.items():
                if key == "claudeeditor_not_installed":
                    if required_value and self.claudeeditor_installed:
                        return False
                elif key == "claudeeditor_installed":
                    if required_value and not self.claudeeditor_installed:
                        return False
                elif key == "claudeeditor_running":
                    if required_value and not self._is_claudeeditor_running():
                        return False
                elif key == "claude_code_context":
                    if required_value and not context.get("from_claude_code", False):
                        return False
                elif key in context:
                    if context[key] != required_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查上下文要求失败: {e}")
            return False
    
    def _record_trigger_event(self, event: TriggerEvent):
        """记录触发事件"""
        try:
            self.trigger_history.append(event)
            
            # 限制历史记录大小
            if len(self.trigger_history) > self.max_history_size:
                self.trigger_history = self.trigger_history[-self.max_history_size:]
            
            self.logger.info(f"检测到触发事件: {event.trigger_type.value} - {event.matched_text}")
            
        except Exception as e:
            self.logger.error(f"记录触发事件失败: {e}")
    
    def _is_claudeeditor_running(self) -> bool:
        """检查 ClaudeEditor 是否正在运行"""
        try:
            # 检查端口 5176 是否被占用
            result = subprocess.run(
                ["lsof", "-Pi", ":5176", "-sTCP:LISTEN", "-t"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip()
            
        except Exception as e:
            self.logger.error(f"检查 ClaudeEditor 运行状态失败: {e}")
            return False
    
    def update_system_status(self, claudeeditor_installed: bool = None, 
                           mirror_code_active: bool = None,
                           dual_communication_ready: bool = None):
        """更新系统状态"""
        try:
            if claudeeditor_installed is not None:
                self.claudeeditor_installed = claudeeditor_installed
            
            if mirror_code_active is not None:
                self.mirror_code_active = mirror_code_active
            
            if dual_communication_ready is not None:
                self.dual_communication_ready = dual_communication_ready
            
            self.logger.debug(f"系统状态更新: ClaudeEditor={self.claudeeditor_installed}, "
                            f"MirrorCode={self.mirror_code_active}, "
                            f"DualComm={self.dual_communication_ready}")
            
        except Exception as e:
            self.logger.error(f"更新系统状态失败: {e}")
    
    def get_trigger_statistics(self) -> Dict[str, Any]:
        """获取触发统计信息"""
        try:
            stats = {
                "total_patterns": sum(len(patterns) for patterns in self.trigger_patterns.values()),
                "total_events": len(self.trigger_history),
                "events_by_type": {},
                "recent_events": []
            }
            
            # 按类型统计事件
            for event in self.trigger_history:
                event_type = event.trigger_type.value
                if event_type not in stats["events_by_type"]:
                    stats["events_by_type"][event_type] = 0
                stats["events_by_type"][event_type] += 1
            
            # 最近的事件
            recent_events = self.trigger_history[-10:] if self.trigger_history else []
            stats["recent_events"] = [
                {
                    "type": event.trigger_type.value,
                    "matched_text": event.matched_text,
                    "timestamp": event.timestamp.isoformat(),
                    "priority": event.priority.value
                }
                for event in recent_events
            ]
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取触发统计失败: {e}")
            return {}
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "claudeeditor_installed": self.claudeeditor_installed,
            "claudeeditor_running": self._is_claudeeditor_running(),
            "mirror_code_active": self.mirror_code_active,
            "dual_communication_ready": self.dual_communication_ready,
            "detection_enabled": self.detection_enabled,
            "auto_trigger_enabled": self.auto_trigger_enabled
        }

# 全局触发检测器实例
trigger_detector = ClaudeCodeTriggerDetector()

# 便捷函数
async def detect_claude_code_triggers(text: str, context: Dict[str, Any] = None) -> List[TriggerEvent]:
    """检测 Claude Code 触发事件的便捷函数"""
    return await trigger_detector.detect_triggers(text, context)

def update_trigger_system_status(**kwargs):
    """更新触发系统状态的便捷函数"""
    trigger_detector.update_system_status(**kwargs)

def get_trigger_system_status() -> Dict[str, Any]:
    """获取触发系统状态的便捷函数"""
    return trigger_detector.get_system_status()

