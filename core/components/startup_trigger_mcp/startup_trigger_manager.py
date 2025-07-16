#!/usr/bin/env python3
"""
Startup Trigger Manager - 启动触发管理器
整合所有触发组件，提供统一的接口和管理功能
"""

import asyncio
import logging
import json
import argparse
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# 导入触发组件
from .trigger_detection import (
    ClaudeCodeTriggerDetector, TriggerEvent, TriggerType,
    detect_claude_code_triggers, update_trigger_system_status, get_trigger_system_status
)
from .trigger_actions import (
    TriggerActionExecutor, ActionResult, ActionStatus,
    execute_trigger_action, get_action_statistics
)
from .hook_trigger_integration import (
    HookTriggerIntegrator, manual_trigger_detection,
    get_integration_statistics, cleanup_integration
)
from .mirror_code_communication import (
    MirrorCodeCommunicator, CommunicationStatus,
    initialize_mirror_code_communication, get_mirror_code_status,
    send_code_sync, send_command_request, cleanup_mirror_code_communication
)
from .claude_tool_mode_integration import (
    ClaudeToolModeIntegration, get_tool_mode_integration,
    ToolModeIntegrationConfig
)

logger = logging.getLogger(__name__)

@dataclass
class StartupTriggerConfig:
    """启动触发配置"""
    auto_trigger_enabled: bool = True
    auto_install_enabled: bool = True
    mirror_code_enabled: bool = True
    hook_integration_enabled: bool = True
    claude_tool_mode_enabled: bool = True  # 新增：Claude 工具模式
    k2_service_enabled: bool = True        # 新增：K2 服务
    heartbeat_interval: int = 30
    monitoring_interval: int = 10
    log_level: str = "INFO"

class StartupTriggerManager:
    """启动触发管理器"""
    
    def __init__(self, config: StartupTriggerConfig = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or StartupTriggerConfig()
        self.initialized = False
        
        # 组件实例
        self.trigger_detector = ClaudeCodeTriggerDetector()
        self.action_executor = TriggerActionExecutor()
        self.hook_integrator = HookTriggerIntegrator()
        self.mirror_communicator = MirrorCodeCommunicator()
        self.tool_mode_integration = get_tool_mode_integration()  # 新增：工具模式集成器
        
        # 管理状态
        self.running = False
        self.start_time = None
        self.statistics = {
            "total_triggers": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "communication_events": 0
        }
        
        # 配置日志
        self._configure_logging()
    
    def _configure_logging(self):
        """配置日志"""
        try:
            log_level = getattr(logging, self.config.log_level.upper())
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(sys.stdout),
                    logging.FileHandler('/tmp/startup_trigger.log')
                ]
            )
            
        except Exception as e:
            print(f"配置日志失败: {e}")
    
    async def initialize(self) -> bool:
        """初始化管理器"""
        try:
            self.logger.info("初始化启动触发管理器...")
            
            # 初始化 Claude 工具模式集成器（优先级最高）
            if self.config.claude_tool_mode_enabled:
                tool_mode_config = ToolModeIntegrationConfig(
                    auto_enable_on_startup=True,
                    auto_configure_k2=self.config.k2_service_enabled,
                    integrate_with_mirror_code=self.config.mirror_code_enabled,
                    enable_request_interception=True,
                    enable_ai_routing=True
                )
                self.tool_mode_integration.config = tool_mode_config
                await self.tool_mode_integration.initialize()
                self.logger.info("Claude 工具模式集成器初始化完成")
            
            # 初始化 Mirror Code 通信
            if self.config.mirror_code_enabled:
                await self.mirror_communicator.initialize()
                self.logger.info("Mirror Code 通信初始化完成")
            
            # 配置组件
            self.trigger_detector.auto_trigger_enabled = self.config.auto_trigger_enabled
            self.action_executor.auto_execute_enabled = self.config.auto_install_enabled
            self.hook_integrator.auto_trigger_enabled = self.config.auto_trigger_enabled
            
            # 注册回调
            self._register_callbacks()
            
            self.initialized = True
            self.start_time = datetime.now()
            
            self.logger.info("启动触发管理器初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化启动触发管理器失败: {e}")
            return False
    
    def _register_callbacks(self):
        """注册回调函数"""
        try:
            # 注册状态变更回调
            self.mirror_communicator.register_status_callback(self._on_communication_status_change)
            
        except Exception as e:
            self.logger.error(f"注册回调函数失败: {e}")
    
    async def _on_communication_status_change(self, status: CommunicationStatus):
        """通信状态变更回调"""
        try:
            self.logger.info(f"通信状态变更: {status.value}")
            
            # 更新触发系统状态
            if status == CommunicationStatus.CONNECTED:
                update_trigger_system_status(
                    claudeeditor_installed=True,
                    mirror_code_active=True,
                    dual_communication_ready=True
                )
            elif status == CommunicationStatus.DISCONNECTED:
                update_trigger_system_status(
                    mirror_code_active=False,
                    dual_communication_ready=False
                )
            
            self.statistics["communication_events"] += 1
            
        except Exception as e:
            self.logger.error(f"处理通信状态变更失败: {e}")
    
    async def process_claude_code_input(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理 Claude Code 输入"""
        try:
            if not self.initialized:
                return {"error": "管理器未初始化"}
            
            if context is None:
                context = {"from_claude_code": True}
            else:
                context["from_claude_code"] = True
            
            self.logger.info(f"处理 Claude Code 输入: {text[:100]}...")
            
            # 优先通过工具模式集成器处理请求
            if self.config.claude_tool_mode_enabled:
                request_data = {
                    "type": "chat_completion",
                    "content": text,
                    "context": context,
                    "endpoint": "/v1/messages"  # 模拟 Claude API 端点
                }
                
                # 拦截和处理请求
                intercepted_result = await self.tool_mode_integration.intercept_request(request_data)
                
                # 如果请求被拦截处理，返回结果
                if intercepted_result.get("blocked") or intercepted_result.get("routed_to_k2"):
                    response = {
                        "processed": True,
                        "tool_mode_handled": True,
                        "blocked": intercepted_result.get("blocked", False),
                        "routed_to_k2": intercepted_result.get("routed_to_k2", False),
                        "message": intercepted_result.get("reason", ""),
                        "system_status": get_trigger_system_status(),
                        "tool_mode_stats": self.tool_mode_integration.get_integration_stats()
                    }
                    
                    if intercepted_result.get("routed_to_k2") and "response" in intercepted_result:
                        k2_response = intercepted_result["response"]
                        response["k2_response"] = {
                            "content": k2_response.get("content", ""),
                            "success": k2_response.get("success", False),
                            "cost": k2_response.get("cost", 0.0),
                            "response_time": k2_response.get("response_time", 0.0)
                        }
                    
                    return response
            
            # 如果工具模式未处理，继续原有的触发检测流程
            # 检测触发事件
            trigger_events = await self.trigger_detector.detect_triggers(text, context)
            
            if not trigger_events:
                return {
                    "processed": False,
                    "message": "未检测到触发事件",
                    "suggestions": self._get_trigger_suggestions(text)
                }
            
            # 执行触发动作
            action_results = []
            for trigger_event in trigger_events:
                if self.config.auto_install_enabled:
                    action_result = await self.action_executor.execute_trigger_action(trigger_event)
                    action_results.append(action_result)
            
            # 更新统计
            self.statistics["total_triggers"] += len(trigger_events)
            self.statistics["successful_actions"] += sum(
                1 for r in action_results if r.status == ActionStatus.SUCCESS
            )
            self.statistics["failed_actions"] += sum(
                1 for r in action_results if r.status == ActionStatus.FAILED
            )
            
            # 生成响应
            response = {
                "processed": True,
                "trigger_events": len(trigger_events),
                "actions_executed": len(action_results),
                "successful_actions": sum(1 for r in action_results if r.status == ActionStatus.SUCCESS),
                "failed_actions": sum(1 for r in action_results if r.status == ActionStatus.FAILED),
                "results": []
            }
            
            # 添加详细结果
            for i, (trigger_event, action_result) in enumerate(zip(trigger_events, action_results)):
                result_detail = {
                    "trigger_type": trigger_event.trigger_type.value,
                    "matched_text": trigger_event.matched_text,
                    "action_status": action_result.status.value,
                    "message": action_result.result_data.get("message", ""),
                    "error": action_result.error_message
                }
                
                # 特殊处理 ClaudeEditor 安装结果
                if (trigger_event.trigger_type == TriggerType.CLAUDEEDITOR_INSTALL and 
                    action_result.status == ActionStatus.SUCCESS):
                    result_detail["claudeeditor_url"] = action_result.result_data.get("url", "")
                    result_detail["installation_successful"] = True
                
                response["results"].append(result_detail)
            
            # 添加系统状态
            response["system_status"] = get_trigger_system_status()
            response["communication_status"] = get_mirror_code_status()
            
            # 添加工具模式状态
            if self.config.claude_tool_mode_enabled:
                response["tool_mode_stats"] = self.tool_mode_integration.get_integration_stats()
            
            return response
            
        except Exception as e:
            self.logger.error(f"处理 Claude Code 输入失败: {e}")
            return {"error": str(e), "processed": False}
    
    def _get_trigger_suggestions(self, text: str) -> List[str]:
        """获取触发建议"""
        suggestions = []
        
        # 基于输入内容提供建议
        if any(keyword in text.lower() for keyword in ["edit", "编辑", "code", "代码"]):
            suggestions.append("尝试说：'需要 ClaudeEditor' 或 '启动编辑器'")
        
        if any(keyword in text.lower() for keyword in ["sync", "同步", "mirror", "镜像"]):
            suggestions.append("尝试说：'启用 Mirror Code 同步' 或 '双向通信'")
        
        if any(keyword in text.lower() for keyword in ["setup", "安装", "install", "初始化"]):
            suggestions.append("尝试说：'PowerAutomation setup' 或 '初始化编辑环境'")
        
        if not suggestions:
            suggestions = [
                "尝试说：'需要 ClaudeEditor'",
                "尝试说：'启动编辑器'",
                "尝试说：'PowerAutomation setup'",
                "尝试说：'初始化编辑环境'"
            ]
        
        return suggestions
    
    async def check_system_status(self) -> Dict[str, Any]:
        """检查系统状态"""
        try:
            return {
                "manager_status": {
                    "initialized": self.initialized,
                    "running": self.running,
                    "start_time": self.start_time.isoformat() if self.start_time else None,
                    "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
                },
                "trigger_system": get_trigger_system_status(),
                "action_statistics": get_action_statistics(),
                "integration_statistics": get_integration_statistics(),
                "communication_status": get_mirror_code_status(),
                "overall_statistics": self.statistics,
                "config": asdict(self.config)
            }
            
        except Exception as e:
            self.logger.error(f"检查系统状态失败: {e}")
            return {"error": str(e)}
    
    async def manual_trigger(self, trigger_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """手动触发"""
        try:
            return await manual_trigger_detection(trigger_text, context)
            
        except Exception as e:
            self.logger.error(f"手动触发失败: {e}")
            return {"error": str(e)}
    
    async def send_mirror_code_sync(self, code_data: Dict[str, Any]) -> bool:
        """发送 Mirror Code 同步"""
        try:
            return await send_code_sync(code_data)
            
        except Exception as e:
            self.logger.error(f"发送 Mirror Code 同步失败: {e}")
            return False
    
    async def send_mirror_command(self, command_data: Dict[str, Any]) -> bool:
        """发送 Mirror 命令"""
        try:
            return await send_command_request(command_data)
            
        except Exception as e:
            self.logger.error(f"发送 Mirror 命令失败: {e}")
            return False
    
    async def start_monitoring(self):
        """启动监控"""
        try:
            if self.running:
                return
            
            self.running = True
            self.logger.info("启动监控模式...")
            
            while self.running:
                try:
                    # 定期检查系统状态
                    await asyncio.sleep(self.config.monitoring_interval)
                    
                    # 这里可以添加定期检查逻辑
                    # 例如检查 ClaudeEditor 是否仍在运行
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"监控循环错误: {e}")
            
        except Exception as e:
            self.logger.error(f"启动监控失败: {e}")
    
    async def stop_monitoring(self):
        """停止监控"""
        try:
            self.running = False
            self.logger.info("停止监控模式")
            
        except Exception as e:
            self.logger.error(f"停止监控失败: {e}")
    
    async def cleanup(self):
        """清理资源"""
        try:
            self.logger.info("清理启动触发管理器...")
            
            # 停止监控
            await self.stop_monitoring()
            
            # 清理工具模式集成器
            if self.config.claude_tool_mode_enabled:
                await self.tool_mode_integration.cleanup()
            
            # 清理组件
            cleanup_integration()
            await cleanup_mirror_code_communication()
            
            self.initialized = False
            self.logger.info("启动触发管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"清理启动触发管理器失败: {e}")

# 全局管理器实例
startup_trigger_manager = StartupTriggerManager()

# CLI 接口
async def main():
    """主函数 - CLI 接口"""
    parser = argparse.ArgumentParser(description="PowerAutomation 启动触发管理器")
    parser.add_argument("--action", choices=["init", "trigger", "status", "monitor", "test"], 
                       default="init", help="执行的动作")
    parser.add_argument("--text", type=str, help="触发文本（用于 trigger 动作）")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = StartupTriggerConfig()
        if args.config and Path(args.config).exists():
            with open(args.config, 'r') as f:
                config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        
        config.log_level = args.log_level
        
        # 创建管理器
        manager = StartupTriggerManager(config)
        
        if args.action == "init":
            print("初始化启动触发管理器...")
            success = await manager.initialize()
            if success:
                print("✅ 初始化成功")
                status = await manager.check_system_status()
                print(json.dumps(status, indent=2, ensure_ascii=False))
            else:
                print("❌ 初始化失败")
                return 1
        
        elif args.action == "trigger":
            if not args.text:
                print("❌ 请提供触发文本 (--text)")
                return 1
            
            await manager.initialize()
            print(f"处理触发文本: {args.text}")
            result = await manager.process_claude_code_input(args.text)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.action == "status":
            await manager.initialize()
            print("检查系统状态...")
            status = await manager.check_system_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        elif args.action == "monitor":
            await manager.initialize()
            print("启动监控模式... (按 Ctrl+C 停止)")
            try:
                await manager.start_monitoring()
            except KeyboardInterrupt:
                print("\n停止监控...")
                await manager.stop_monitoring()
        
        elif args.action == "test":
            await manager.initialize()
            print("运行测试...")
            
            test_cases = [
                "需要 ClaudeEditor",
                "启动编辑器",
                "PowerAutomation setup",
                "初始化编辑环境",
                "启用 Mirror Code 同步",
                "建立双向通信"
            ]
            
            for test_text in test_cases:
                print(f"\n测试: {test_text}")
                result = await manager.process_claude_code_input(test_text)
                print(f"结果: {result.get('processed', False)}")
                if result.get('results'):
                    for r in result['results']:
                        print(f"  - {r['trigger_type']}: {r['action_status']}")
        
        # 清理
        await manager.cleanup()
        return 0
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

