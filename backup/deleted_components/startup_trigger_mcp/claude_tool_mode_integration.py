#!/usr/bin/env python3
"""
Claude Tool Mode Integration - Claude 工具模式集成
将 Claude 工具模式和 K2 服务路由集成到 startup_trigger_manager 中
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

from .claude_tool_mode_config import ClaudeToolModeManager, get_tool_mode_manager
from .k2_service_router import K2ServiceRouter, K2Request, K2Response, get_k2_router
from .hook_trigger_integration import HookTriggerIntegrator
# 暂时注释掉 mirror_code 导入，避免循环依赖
# from ..mirror_code.communication.comm_manager import CommunicationManager, Event, EventType

logger = logging.getLogger(__name__)

# 简化的事件类型定义（避免依赖 mirror_code）
class EventType:
    STATUS_UPDATE = "status_update"
    ERROR_OCCURRED = "error_occurred"
    SYNC_COMPLETED = "sync_completed"
    CLAUDE_RESPONSE = "claude_response"

@dataclass
class Event:
    id: str
    type: str
    data: Any
    timestamp: float
    source: str

class SimpleCommunicationManager:
    """简化的通信管理器"""
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        self.initialized = True
    
    async def publish_event(self, channel: str, event: Event):
        # 简化实现，只记录日志
        logger.info(f"Event published to {channel}: {event.type}")
    
    def subscribe_to_channel(self, channel: str, subscriber: str, callback=None):
        logger.info(f"Subscribed {subscriber} to {channel}")

@dataclass
class ToolModeIntegrationConfig:
    """工具模式集成配置"""
    auto_enable_on_startup: bool = True
    auto_configure_k2: bool = True
    integrate_with_mirror_code: bool = True
    enable_request_interception: bool = True
    enable_ai_routing: bool = True
    log_all_operations: bool = True

class ClaudeToolModeIntegration:
    """Claude 工具模式集成器"""
    
    def __init__(self, config: ToolModeIntegrationConfig = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or ToolModeIntegrationConfig()
        
        # 核心组件
        self.tool_mode_manager = get_tool_mode_manager()
        self.k2_router = get_k2_router()
        self.hook_integrator = HookTriggerIntegrator()
        self.comm_manager = SimpleCommunicationManager()  # 使用简化版本
        
        # 状态管理
        self.initialized = False
        self.active_interceptors = {}
        self.routing_stats = {
            "intercepted_requests": 0,
            "routed_to_k2": 0,
            "tool_requests": 0,
            "blocked_model_requests": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # 请求拦截器
        self.request_interceptors = []
        self.response_processors = []
    
    async def initialize(self) -> bool:
        """初始化集成器"""
        try:
            self.logger.info("🔧 初始化 Claude 工具模式集成器...")
            
            # 1. 初始化通信管理器
            await self.comm_manager.initialize()
            
            # 2. 配置工具模式
            if self.config.auto_enable_on_startup:
                await self._configure_tool_mode()
            
            # 3. 配置 K2 服务
            if self.config.auto_configure_k2:
                await self._configure_k2_service()
            
            # 4. 设置请求拦截
            if self.config.enable_request_interception:
                await self._setup_request_interception()
            
            # 5. 集成 Mirror Code
            if self.config.integrate_with_mirror_code:
                await self._integrate_mirror_code()
            
            # 6. 注册钩子处理器
            await self._register_hook_handlers()
            
            self.initialized = True
            self.logger.info("✅ Claude 工具模式集成器初始化完成")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 初始化集成器失败: {e}")
            return False
    
    async def _configure_tool_mode(self):
        """配置工具模式"""
        self.logger.info("🔧 配置 Claude 工具模式...")
        
        # 启用工具模式
        self.tool_mode_manager.enable_tool_mode()
        
        # 发送配置事件
        await self._send_event(
            EventType.STATUS_UPDATE,
            {
                "component": "claude_tool_mode",
                "status": "enabled",
                "message": "Claude 工具模式已启用"
            }
        )
    
    async def _configure_k2_service(self):
        """配置 K2 服务"""
        self.logger.info("🔧 配置 K2 服务...")
        
        # 检查 K2 服务健康状态
        healthy = await self.k2_router.health_check()
        
        if healthy:
            self.logger.info("✅ K2 服务连接正常")
        else:
            self.logger.warning("⚠️ K2 服务连接异常，将在后续重试")
        
        # 发送配置事件
        await self._send_event(
            EventType.STATUS_UPDATE,
            {
                "component": "k2_service",
                "status": "configured",
                "healthy": healthy,
                "message": f"K2 服务配置完成，健康状态: {healthy}"
            }
        )
    
    async def _setup_request_interception(self):
        """设置请求拦截"""
        self.logger.info("🔧 设置请求拦截...")
        
        # 注册模型请求拦截器
        self.register_request_interceptor(
            "claude_model_blocker",
            self._intercept_claude_model_requests,
            priority=100
        )
        
        # 注册工具请求处理器
        self.register_request_interceptor(
            "tool_request_handler",
            self._handle_tool_requests,
            priority=90
        )
        
        # 注册 AI 推理路由器
        self.register_request_interceptor(
            "ai_inference_router",
            self._route_ai_inference_requests,
            priority=80
        )
    
    async def _integrate_mirror_code(self):
        """集成 Mirror Code"""
        self.logger.info("🔧 集成 Mirror Code...")
        
        # 订阅 Mirror Code 事件
        self.comm_manager.subscribe_to_channel(
            "claude",
            "tool_mode_integration",
            self._handle_mirror_code_event
        )
        
        # 发送集成事件
        await self._send_event(
            EventType.STATUS_UPDATE,
            {
                "component": "mirror_code_integration",
                "status": "active",
                "message": "Mirror Code 集成已激活"
            }
        )
    
    async def _register_hook_handlers(self):
        """注册钩子处理器"""
        self.logger.info("🔧 注册钩子处理器...")
        
        # 注册用户输入钩子
        self.hook_integrator.register_hook(
            "USER_INPUT",
            self._handle_user_input_hook,
            priority=95,
            description="处理用户输入并检查是否需要 AI 推理"
        )
        
        # 注册命令执行前钩子
        self.hook_integrator.register_hook(
            "BEFORE_EXECUTE",
            self._handle_before_execute_hook,
            priority=90,
            description="在命令执行前检查是否为模型请求"
        )
    
    def register_request_interceptor(self, name: str, handler: Callable, priority: int = 50):
        """注册请求拦截器"""
        interceptor = {
            "name": name,
            "handler": handler,
            "priority": priority,
            "active": True
        }
        
        self.request_interceptors.append(interceptor)
        self.request_interceptors.sort(key=lambda x: x["priority"], reverse=True)
        
        self.logger.info(f"📝 注册请求拦截器: {name} (优先级: {priority})")
    
    async def intercept_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """拦截和处理请求"""
        self.routing_stats["intercepted_requests"] += 1
        
        try:
            # 按优先级执行拦截器
            for interceptor in self.request_interceptors:
                if not interceptor["active"]:
                    continue
                
                try:
                    result = await interceptor["handler"](request_data)
                    
                    # 如果拦截器返回结果，则停止后续处理
                    if result is not None:
                        self.logger.info(f"🔄 请求被拦截器处理: {interceptor['name']}")
                        return result
                        
                except Exception as e:
                    self.logger.error(f"❌ 拦截器 {interceptor['name']} 执行失败: {e}")
            
            # 如果没有拦截器处理，返回原始请求
            return request_data
            
        except Exception as e:
            self.logger.error(f"❌ 请求拦截失败: {e}")
            return request_data
    
    async def _intercept_claude_model_requests(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """拦截 Claude 模型请求"""
        endpoint = request_data.get("endpoint", "")
        request_type = request_data.get("type", "")
        
        # 检查是否为被阻止的模型端点
        if self.tool_mode_manager.is_endpoint_blocked(endpoint):
            self.routing_stats["blocked_model_requests"] += 1
            
            # 记录被阻止的请求
            self.tool_mode_manager.log_blocked_request(
                endpoint,
                "Claude 工具模式已启用，模型推理被阻止"
            )
            
            # 发送阻止事件
            await self._send_event(
                EventType.ERROR_OCCURRED,
                {
                    "type": "model_request_blocked",
                    "endpoint": endpoint,
                    "reason": "Claude 工具模式已启用",
                    "suggestion": "请使用工具功能或将 AI 推理任务路由到 K2 服务"
                }
            )
            
            return {
                "blocked": True,
                "reason": "Claude 工具模式已启用，模型推理被阻止",
                "alternative": "使用 K2 服务进行 AI 推理"
            }
        
        return None
    
    async def _handle_tool_requests(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理工具请求"""
        tool_name = request_data.get("tool_name", "")
        
        if tool_name:
            self.routing_stats["tool_requests"] += 1
            
            # 检查工具是否被允许
            allowed = self.tool_mode_manager.is_tool_allowed(tool_name)
            
            # 记录工具请求
            self.tool_mode_manager.log_tool_request(tool_name, allowed)
            
            if not allowed:
                return {
                    "blocked": True,
                    "reason": f"工具 {tool_name} 不在允许列表中",
                    "allowed_tools": self.tool_mode_manager.config.allowed_tools
                }
        
        return None
    
    async def _route_ai_inference_requests(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """路由 AI 推理请求"""
        request_type = request_data.get("type", "")
        
        # 检查是否应该路由到 K2
        if self.tool_mode_manager.should_route_to_k2(request_type):
            self.routing_stats["routed_to_k2"] += 1
            
            try:
                # 构建 K2 请求
                k2_request = K2Request(
                    request_id=str(uuid.uuid4()),
                    request_type=request_type,
                    content=request_data.get("content", ""),
                    context=request_data.get("context", {}),
                    temperature=request_data.get("temperature", 0.7),
                    max_tokens=request_data.get("max_tokens", 4096)
                )
                
                # 路由到 K2 服务
                k2_response = await self.k2_router.route_ai_request(k2_request)
                
                # 记录路由
                self.tool_mode_manager.log_k2_routing(
                    request_type,
                    f"成功路由到 K2 - {k2_response.response_time:.2f}s"
                )
                
                # 发送路由事件
                await self._send_event(
                    EventType.SYNC_COMPLETED,
                    {
                        "type": "k2_routing",
                        "request_id": k2_request.request_id,
                        "request_type": request_type,
                        "success": k2_response.success,
                        "response_time": k2_response.response_time,
                        "cost": k2_response.cost
                    }
                )
                
                return {
                    "routed_to_k2": True,
                    "response": asdict(k2_response)
                }
                
            except Exception as e:
                self.logger.error(f"❌ K2 路由失败: {e}")
                
                return {
                    "routed_to_k2": False,
                    "error": str(e)
                }
        
        return None
    
    async def _handle_user_input_hook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户输入钩子"""
        user_input = data.get("input", "")
        
        # 检查是否包含 AI 推理请求
        ai_keywords = ["分析", "生成", "解释", "总结", "翻译", "写代码", "帮我"]
        
        if any(keyword in user_input for keyword in ai_keywords):
            # 这是一个 AI 推理请求，路由到 K2
            request_data = {
                "type": "chat_completion",
                "content": user_input,
                "context": {"source": "user_input_hook"}
            }
            
            result = await self._route_ai_inference_requests(request_data)
            
            if result and result.get("routed_to_k2"):
                return {
                    "handled": True,
                    "response": result["response"]["content"],
                    "routed_to_k2": True
                }
        
        return {"handled": False}
    
    async def _handle_before_execute_hook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理命令执行前钩子"""
        command = data.get("command", "")
        
        # 检查是否为模型 API 调用
        model_api_patterns = [
            "curl.*api.anthropic.com",
            "curl.*api.openai.com",
            "python.*openai",
            "python.*anthropic"
        ]
        
        for pattern in model_api_patterns:
            if pattern in command:
                # 阻止模型 API 调用
                self.tool_mode_manager.log_blocked_request(
                    command,
                    "命令包含模型 API 调用"
                )
                
                return {
                    "blocked": True,
                    "reason": "命令包含模型 API 调用，已被工具模式阻止",
                    "suggestion": "使用 K2 服务进行 AI 推理"
                }
        
        return {"blocked": False}
    
    async def _handle_mirror_code_event(self, event: Event):
        """处理 Mirror Code 事件"""
        try:
            if event.type == EventType.CLAUDE_RESPONSE:
                # 检查是否为模型响应，如果是则路由到 K2
                response_data = event.data
                
                if response_data.get("type") == "model_response":
                    self.logger.info("🔄 检测到 Claude 模型响应，考虑路由到 K2")
                    
                    # 这里可以添加更复杂的路由逻辑
                    
        except Exception as e:
            self.logger.error(f"❌ 处理 Mirror Code 事件失败: {e}")
    
    async def _send_event(self, event_type: EventType, data: Any):
        """发送事件"""
        try:
            event = Event(
                id=str(uuid.uuid4()),
                type=event_type,
                data=data,
                timestamp=time.time(),
                source="claude_tool_mode_integration"
            )
            
            await self.comm_manager.publish_event("events", event)
            
        except Exception as e:
            self.logger.error(f"❌ 发送事件失败: {e}")
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """获取集成统计信息"""
        uptime = (datetime.now() - datetime.fromisoformat(self.routing_stats["start_time"])).total_seconds()
        
        return {
            **self.routing_stats,
            "uptime_seconds": uptime,
            "tool_mode_config": asdict(self.tool_mode_manager.config),
            "k2_router_stats": self.k2_router.get_stats(),
            "active_interceptors": len([i for i in self.request_interceptors if i["active"]]),
            "initialized": self.initialized
        }
    
    async def cleanup(self):
        """清理资源"""
        try:
            self.logger.info("🧹 清理 Claude 工具模式集成器...")
            
            # 清理 K2 路由器
            await self.k2_router.cleanup()
            
            # 清理拦截器
            self.request_interceptors.clear()
            self.response_processors.clear()
            
            self.initialized = False
            self.logger.info("✅ Claude 工具模式集成器清理完成")
            
        except Exception as e:
            self.logger.error(f"❌ 清理集成器失败: {e}")


# 全局集成器实例
claude_tool_mode_integration = ClaudeToolModeIntegration()


def get_tool_mode_integration() -> ClaudeToolModeIntegration:
    """获取工具模式集成器实例"""
    return claude_tool_mode_integration


# CLI 接口
if __name__ == "__main__":
    import argparse
    import sys
    
    async def main():
        parser = argparse.ArgumentParser(description="Claude 工具模式集成器")
        parser.add_argument("--action", choices=["init", "stats", "test"], 
                           default="init", help="执行的动作")
        parser.add_argument("--test-input", type=str, default="帮我分析这个代码", 
                           help="测试输入")
        
        args = parser.parse_args()
        
        integration = ClaudeToolModeIntegration()
        
        try:
            if args.action == "init":
                print("初始化 Claude 工具模式集成器...")
                success = await integration.initialize()
                print(f"初始化结果: {'✅ 成功' if success else '❌ 失败'}")
            
            elif args.action == "stats":
                await integration.initialize()
                print("集成器统计信息:")
                stats = integration.get_integration_stats()
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            elif args.action == "test":
                await integration.initialize()
                print(f"测试用户输入: {args.test_input}")
                
                result = await integration._handle_user_input_hook({
                    "input": args.test_input
                })
                
                print(f"处理结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        finally:
            await integration.cleanup()
    
    asyncio.run(main())

