#!/usr/bin/env python3
"""
Hook Trigger Integration - 钩子触发集成模块
将触发检测和动作执行与钩子系统深度集成，实现智能自动安装
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# 导入钩子系统
try:
    from ..enhanced_command_mcp.hook_integration import CommandHookManager, HookType, HookEvent
except ImportError:
    logging.warning("无法导入钩子系统，使用模拟模式")
    HookType = None
    HookEvent = None

# 导入触发检测和动作执行
from .trigger_detection import (
    ClaudeCodeTriggerDetector, TriggerEvent, TriggerType, 
    detect_claude_code_triggers, update_trigger_system_status
)
from .trigger_actions import (
    TriggerActionExecutor, ActionResult, ActionStatus,
    execute_trigger_action, get_action_statistics
)

logger = logging.getLogger(__name__)

@dataclass
class HookTriggerEvent:
    """钩子触发事件"""
    hook_event_id: str
    trigger_events: List[TriggerEvent]
    action_results: List[ActionResult]
    timestamp: datetime
    context: Dict[str, Any]

class HookTriggerIntegrator:
    """钩子触发集成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized = False
        
        # 组件实例
        self.hook_manager = None
        self.trigger_detector = ClaudeCodeTriggerDetector()
        self.action_executor = TriggerActionExecutor()
        
        # 集成配置
        self.auto_trigger_enabled = True
        self.hook_trigger_history: List[HookTriggerEvent] = []
        self.max_history_size = 100
        
        # 钩子处理器ID
        self.hook_handler_ids: List[str] = []
        
        # 初始化集成
        self._initialize_integration()
    
    def _initialize_integration(self):
        """初始化钩子集成"""
        try:
            # 尝试获取钩子管理器
            if HookType and HookEvent:
                from ..enhanced_command_mcp.hook_integration import CommandHookManager
                self.hook_manager = CommandHookManager()
                
                # 注册钩子处理器
                self._register_hook_handlers()
                
                self.logger.info("钩子触发集成初始化成功")
            else:
                self.logger.warning("钩子系统不可用，使用独立模式")
            
            self.initialized = True
            
        except Exception as e:
            self.logger.error(f"钩子触发集成初始化失败: {e}")
    
    def _register_hook_handlers(self):
        """注册钩子处理器"""
        try:
            if not self.hook_manager:
                return
            
            # 注册用户输入钩子处理器
            handler_id = self.hook_manager.register_hook(
                HookType.USER_INPUT,
                self._handle_user_input_hook,
                priority=90,
                description="检测用户输入中的 ClaudeEditor 触发词"
            )
            self.hook_handler_ids.append(handler_id)
            
            # 注册命令执行前钩子处理器
            handler_id = self.hook_manager.register_hook(
                HookType.BEFORE_EXECUTE,
                self._handle_before_execute_hook,
                priority=80,
                description="在命令执行前检测 ClaudeEditor 需求"
            )
            self.hook_handler_ids.append(handler_id)
            
            # 注册工作流开始钩子处理器
            handler_id = self.hook_manager.register_hook(
                HookType.WORKFLOW_START,
                self._handle_workflow_start_hook,
                priority=70,
                description="在工作流开始时检测环境需求"
            )
            self.hook_handler_ids.append(handler_id)
            
            # 注册系统状态变更钩子处理器
            handler_id = self.hook_manager.register_hook(
                HookType.SYSTEM_STATUS_CHANGE,
                self._handle_system_status_change_hook,
                priority=60,
                description="监控系统状态变更并响应"
            )
            self.hook_handler_ids.append(handler_id)
            
            self.logger.info(f"注册了 {len(self.hook_handler_ids)} 个钩子处理器")
            
        except Exception as e:
            self.logger.error(f"注册钩子处理器失败: {e}")
    
    async def _handle_user_input_hook(self, hook_event: HookEvent) -> Dict[str, Any]:
        """处理用户输入钩子"""
        try:
            user_input = hook_event.data.get("input", "")
            if not user_input:
                return {"processed": False, "reason": "无用户输入"}
            
            # 检测触发事件
            context = {
                "from_claude_code": hook_event.context.get("source") == "claude_code",
                "user_intent": "edit_or_develop",
                "hook_event_id": hook_event.id
            }
            
            trigger_events = await self.trigger_detector.detect_triggers(user_input, context)
            
            if not trigger_events:
                return {"processed": False, "reason": "未检测到触发事件"}
            
            # 执行触发动作
            action_results = []
            if self.auto_trigger_enabled:
                for trigger_event in trigger_events:
                    action_result = await self.action_executor.execute_trigger_action(trigger_event)
                    action_results.append(action_result)
            
            # 记录钩子触发事件
            hook_trigger_event = HookTriggerEvent(
                hook_event_id=hook_event.id,
                trigger_events=trigger_events,
                action_results=action_results,
                timestamp=datetime.now(),
                context=context
            )
            self._record_hook_trigger_event(hook_trigger_event)
            
            return {
                "processed": True,
                "trigger_events_count": len(trigger_events),
                "action_results_count": len(action_results),
                "successful_actions": sum(1 for r in action_results if r.status == ActionStatus.SUCCESS),
                "recommendations": self._generate_recommendations(trigger_events, action_results)
            }
            
        except Exception as e:
            self.logger.error(f"处理用户输入钩子失败: {e}")
            return {"processed": False, "error": str(e)}
    
    async def _handle_before_execute_hook(self, hook_event: HookEvent) -> Dict[str, Any]:
        """处理命令执行前钩子"""
        try:
            command = hook_event.data.get("command", "")
            if not command:
                return {"processed": False, "reason": "无命令内容"}
            
            # 检测是否需要 ClaudeEditor
            context = {
                "command_context": True,
                "hook_event_id": hook_event.id
            }
            
            # 检查命令是否涉及编辑或开发
            edit_keywords = ["edit", "编辑", "modify", "修改", "develop", "开发", "code", "代码"]
            needs_editor = any(keyword in command.lower() for keyword in edit_keywords)
            
            if needs_editor:
                # 检测触发事件
                trigger_events = await self.trigger_detector.detect_triggers(
                    f"需要编辑环境执行命令: {command}", context
                )
                
                if trigger_events:
                    # 执行触发动作
                    action_results = []
                    if self.auto_trigger_enabled:
                        for trigger_event in trigger_events:
                            action_result = await self.action_executor.execute_trigger_action(trigger_event)
                            action_results.append(action_result)
                    
                    return {
                        "processed": True,
                        "editor_prepared": any(r.status == ActionStatus.SUCCESS for r in action_results),
                        "recommendations": ["建议在 ClaudeEditor 中执行此命令以获得更好的体验"]
                    }
            
            return {"processed": False, "reason": "命令不需要编辑环境"}
            
        except Exception as e:
            self.logger.error(f"处理命令执行前钩子失败: {e}")
            return {"processed": False, "error": str(e)}
    
    async def _handle_workflow_start_hook(self, hook_event: HookEvent) -> Dict[str, Any]:
        """处理工作流开始钩子"""
        try:
            workflow_type = hook_event.data.get("workflow_type", "")
            workflow_data = hook_event.data.get("workflow_data", {})
            
            # 检查工作流是否需要编辑环境
            editor_workflows = ["code_development", "file_editing", "project_management"]
            
            if workflow_type in editor_workflows:
                context = {
                    "workflow_context": True,
                    "workflow_type": workflow_type,
                    "hook_event_id": hook_event.id
                }
                
                # 检测触发事件
                trigger_text = f"启动 {workflow_type} 工作流，需要编辑环境"
                trigger_events = await self.trigger_detector.detect_triggers(trigger_text, context)
                
                if trigger_events:
                    # 执行触发动作
                    action_results = []
                    if self.auto_trigger_enabled:
                        for trigger_event in trigger_events:
                            action_result = await self.action_executor.execute_trigger_action(trigger_event)
                            action_results.append(action_result)
                    
                    return {
                        "processed": True,
                        "environment_prepared": any(r.status == ActionStatus.SUCCESS for r in action_results),
                        "workflow_enhanced": True
                    }
            
            return {"processed": False, "reason": "工作流不需要编辑环境"}
            
        except Exception as e:
            self.logger.error(f"处理工作流开始钩子失败: {e}")
            return {"processed": False, "error": str(e)}
    
    async def _handle_system_status_change_hook(self, hook_event: HookEvent) -> Dict[str, Any]:
        """处理系统状态变更钩子"""
        try:
            status_change = hook_event.data.get("status_change", {})
            component = status_change.get("component", "")
            new_status = status_change.get("new_status", "")
            
            # 更新触发系统状态
            if component == "claudeeditor":
                if new_status == "installed":
                    update_trigger_system_status(claudeeditor_installed=True)
                elif new_status == "running":
                    update_trigger_system_status(claudeeditor_installed=True)
                elif new_status == "stopped":
                    update_trigger_system_status(claudeeditor_installed=True)
            
            return {
                "processed": True,
                "status_updated": True,
                "component": component,
                "new_status": new_status
            }
            
        except Exception as e:
            self.logger.error(f"处理系统状态变更钩子失败: {e}")
            return {"processed": False, "error": str(e)}
    
    def _generate_recommendations(self, trigger_events: List[TriggerEvent], 
                                action_results: List[ActionResult]) -> List[str]:
        """生成推荐建议"""
        recommendations = []
        
        try:
            # 基于触发事件生成建议
            for trigger_event in trigger_events:
                if trigger_event.trigger_type == TriggerType.CLAUDEEDITOR_INSTALL:
                    recommendations.append("建议使用 ClaudeEditor 进行代码编辑和项目管理")
                elif trigger_event.trigger_type == TriggerType.MIRROR_CODE_SYNC:
                    recommendations.append("启用 Mirror Code 同步以实现实时代码镜像")
                elif trigger_event.trigger_type == TriggerType.DUAL_COMMUNICATION:
                    recommendations.append("建立双向通信以增强 Claude Code 与 ClaudeEditor 的协作")
            
            # 基于动作结果生成建议
            successful_actions = [r for r in action_results if r.status == ActionStatus.SUCCESS]
            failed_actions = [r for r in action_results if r.status == ActionStatus.FAILED]
            
            if successful_actions:
                recommendations.append(f"已成功执行 {len(successful_actions)} 个自动化动作")
            
            if failed_actions:
                recommendations.append(f"有 {len(failed_actions)} 个动作执行失败，请检查系统状态")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"生成推荐建议失败: {e}")
            return ["建议检查系统状态并重试"]
    
    def _record_hook_trigger_event(self, hook_trigger_event: HookTriggerEvent):
        """记录钩子触发事件"""
        try:
            self.hook_trigger_history.append(hook_trigger_event)
            
            # 限制历史记录大小
            if len(self.hook_trigger_history) > self.max_history_size:
                self.hook_trigger_history = self.hook_trigger_history[-self.max_history_size:]
            
            self.logger.info(f"记录钩子触发事件: {hook_trigger_event.hook_event_id}")
            
        except Exception as e:
            self.logger.error(f"记录钩子触发事件失败: {e}")
    
    async def manual_trigger_detection(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """手动触发检测（用于测试或直接调用）"""
        try:
            if context is None:
                context = {"manual_trigger": True}
            
            # 检测触发事件
            trigger_events = await self.trigger_detector.detect_triggers(text, context)
            
            if not trigger_events:
                return {
                    "success": False,
                    "message": "未检测到触发事件",
                    "text": text
                }
            
            # 执行触发动作
            action_results = []
            if self.auto_trigger_enabled:
                for trigger_event in trigger_events:
                    action_result = await self.action_executor.execute_trigger_action(trigger_event)
                    action_results.append(action_result)
            
            return {
                "success": True,
                "trigger_events_count": len(trigger_events),
                "action_results_count": len(action_results),
                "successful_actions": sum(1 for r in action_results if r.status == ActionStatus.SUCCESS),
                "failed_actions": sum(1 for r in action_results if r.status == ActionStatus.FAILED),
                "trigger_events": [
                    {
                        "type": te.trigger_type.value,
                        "matched_text": te.matched_text,
                        "priority": te.priority.value
                    }
                    for te in trigger_events
                ],
                "action_results": [
                    {
                        "action_id": ar.action_id,
                        "status": ar.status.value,
                        "message": ar.result_data.get("message", ""),
                        "error": ar.error_message
                    }
                    for ar in action_results
                ]
            }
            
        except Exception as e:
            self.logger.error(f"手动触发检测失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": text
            }
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """获取集成统计信息"""
        try:
            return {
                "initialized": self.initialized,
                "hook_manager_available": self.hook_manager is not None,
                "registered_hook_handlers": len(self.hook_handler_ids),
                "auto_trigger_enabled": self.auto_trigger_enabled,
                "hook_trigger_events": len(self.hook_trigger_history),
                "trigger_detector_stats": self.trigger_detector.get_trigger_statistics(),
                "action_executor_stats": self.action_executor.get_action_statistics(),
                "system_status": self.trigger_detector.get_system_status()
            }
            
        except Exception as e:
            self.logger.error(f"获取集成统计失败: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """清理资源"""
        try:
            # 注销钩子处理器
            if self.hook_manager:
                for handler_id in self.hook_handler_ids:
                    self.hook_manager.unregister_hook(handler_id)
                self.hook_handler_ids.clear()
            
            self.logger.info("钩子触发集成清理完成")
            
        except Exception as e:
            self.logger.error(f"清理钩子触发集成失败: {e}")

# 全局钩子触发集成器实例
hook_trigger_integrator = HookTriggerIntegrator()

# 便捷函数
async def manual_trigger_detection(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """手动触发检测的便捷函数"""
    return await hook_trigger_integrator.manual_trigger_detection(text, context)

def get_integration_statistics() -> Dict[str, Any]:
    """获取集成统计的便捷函数"""
    return hook_trigger_integrator.get_integration_statistics()

def cleanup_integration():
    """清理集成的便捷函数"""
    hook_trigger_integrator.cleanup()

