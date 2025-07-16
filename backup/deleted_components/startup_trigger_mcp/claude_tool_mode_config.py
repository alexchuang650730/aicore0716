#!/usr/bin/env python3
"""
Claude Tool Mode Configuration - Claude 工具模式配置
实现完全不使用 Claude 模型服务，只使用工具和指令的配置
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ClaudeToolModeConfig:
    """Claude 工具模式配置"""
    # 工具模式设置
    tool_mode_enabled: bool = True
    disable_model_inference: bool = True
    allow_tools_only: bool = True
    
    # K2 服务路由设置
    k2_service_enabled: bool = True
    k2_service_url: str = "https://cloud.infini-ai.com/maas/v1"
    k2_api_key: str = ""
    k2_model_id: str = "kimi-k2-instruct"
    
    # 工具白名单
    allowed_tools: List[str] = None
    blocked_model_endpoints: List[str] = None
    
    # 路由规则
    route_ai_requests_to_k2: bool = True
    preserve_tool_functionality: bool = True
    
    # 监控设置
    log_blocked_requests: bool = True
    log_k2_routing: bool = True
    
    def __post_init__(self):
        """初始化后处理"""
        if self.allowed_tools is None:
            self.allowed_tools = [
                "file_read",
                "file_write_text", 
                "file_append_text",
                "file_replace_text",
                "shell_exec",
                "shell_view",
                "shell_wait",
                "shell_input",
                "shell_kill",
                "browser_navigate",
                "browser_view",
                "browser_click",
                "browser_input",
                "browser_scroll_down",
                "browser_scroll_up",
                "browser_save_image",
                "media_generate_image",
                "media_generate_video",
                "media_generate_speech",
                "info_search_web",
                "info_search_image",
                "info_search_api",
                "service_expose_port",
                "service_deploy_frontend",
                "service_deploy_backend",
                "slide_initialize",
                "slide_present"
            ]
        
        if self.blocked_model_endpoints is None:
            self.blocked_model_endpoints = [
                "/v1/messages",
                "/v1/chat/completions",
                "/v1/completions",
                "api.anthropic.com",
                "api.openai.com"
            ]
        
        if not self.k2_api_key:
            self.k2_api_key = os.environ.get("INFINI_AI_API_KEY", "sk-kqbgz7fvqdutvns7")


class ClaudeToolModeManager:
    """Claude 工具模式管理器"""
    
    def __init__(self, config: ClaudeToolModeConfig = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or ClaudeToolModeConfig()
        self.config_file = Path.home() / ".powerautomation" / "claude_tool_mode.json"
        self.stats = {
            "blocked_model_requests": 0,
            "routed_to_k2": 0,
            "tool_requests_allowed": 0,
            "start_time": datetime.now().isoformat()
        }
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                # 更新配置
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                self.logger.info(f"已加载 Claude 工具模式配置: {self.config_file}")
            else:
                # 保存默认配置
                self._save_config()
                self.logger.info("已创建默认 Claude 工具模式配置")
                
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
    
    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"已保存 Claude 工具模式配置: {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
    
    def is_tool_mode_enabled(self) -> bool:
        """检查工具模式是否启用"""
        return self.config.tool_mode_enabled
    
    def is_model_inference_disabled(self) -> bool:
        """检查模型推理是否被禁用"""
        return self.config.disable_model_inference
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """检查工具是否被允许"""
        if not self.config.allow_tools_only:
            return True
        
        return tool_name in self.config.allowed_tools
    
    def is_endpoint_blocked(self, endpoint: str) -> bool:
        """检查端点是否被阻止"""
        if not self.config.disable_model_inference:
            return False
        
        for blocked_endpoint in self.config.blocked_model_endpoints:
            if blocked_endpoint in endpoint:
                return True
        
        return False
    
    def should_route_to_k2(self, request_type: str) -> bool:
        """检查是否应该路由到 K2 服务"""
        if not self.config.k2_service_enabled:
            return False
        
        if not self.config.route_ai_requests_to_k2:
            return False
        
        # AI 推理请求应该路由到 K2
        ai_request_types = [
            "chat_completion",
            "text_generation", 
            "code_generation",
            "analysis",
            "reasoning"
        ]
        
        return request_type in ai_request_types
    
    def get_k2_service_config(self) -> Dict[str, Any]:
        """获取 K2 服务配置"""
        return {
            "url": self.config.k2_service_url,
            "api_key": self.config.k2_api_key,
            "model_id": self.config.k2_model_id,
            "enabled": self.config.k2_service_enabled
        }
    
    def log_blocked_request(self, endpoint: str, reason: str):
        """记录被阻止的请求"""
        if self.config.log_blocked_requests:
            self.logger.warning(f"🚫 阻止模型请求: {endpoint} - {reason}")
            self.stats["blocked_model_requests"] += 1
    
    def log_k2_routing(self, request_type: str, details: str = ""):
        """记录 K2 路由"""
        if self.config.log_k2_routing:
            self.logger.info(f"🔄 路由到 K2: {request_type} - {details}")
            self.stats["routed_to_k2"] += 1
    
    def log_tool_request(self, tool_name: str, allowed: bool):
        """记录工具请求"""
        status = "✅ 允许" if allowed else "❌ 拒绝"
        self.logger.info(f"{status} 工具请求: {tool_name}")
        
        if allowed:
            self.stats["tool_requests_allowed"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "config": asdict(self.config),
            "uptime": (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds()
        }
    
    def update_config(self, **kwargs):
        """更新配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    self.logger.info(f"更新配置: {key} = {value}")
            
            # 保存配置
            self._save_config()
            
        except Exception as e:
            self.logger.error(f"更新配置失败: {e}")
    
    def enable_tool_mode(self):
        """启用工具模式"""
        self.update_config(
            tool_mode_enabled=True,
            disable_model_inference=True,
            allow_tools_only=True,
            route_ai_requests_to_k2=True
        )
        self.logger.info("🔧 已启用 Claude 工具模式")
    
    def disable_tool_mode(self):
        """禁用工具模式"""
        self.update_config(
            tool_mode_enabled=False,
            disable_model_inference=False,
            allow_tools_only=False,
            route_ai_requests_to_k2=False
        )
        self.logger.info("🔧 已禁用 Claude 工具模式")
    
    def configure_k2_service(self, url: str = None, api_key: str = None, model_id: str = None):
        """配置 K2 服务"""
        updates = {}
        
        if url:
            updates["k2_service_url"] = url
        if api_key:
            updates["k2_api_key"] = api_key
        if model_id:
            updates["k2_model_id"] = model_id
        
        if updates:
            self.update_config(**updates)
            self.logger.info("🔧 已更新 K2 服务配置")


# 全局工具模式管理器实例
claude_tool_mode_manager = ClaudeToolModeManager()


def get_tool_mode_manager() -> ClaudeToolModeManager:
    """获取工具模式管理器实例"""
    return claude_tool_mode_manager


# CLI 接口
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Claude 工具模式配置管理")
    parser.add_argument("--action", choices=["enable", "disable", "status", "config"], 
                       default="status", help="执行的动作")
    parser.add_argument("--k2-url", type=str, help="K2 服务 URL")
    parser.add_argument("--k2-key", type=str, help="K2 API Key")
    parser.add_argument("--k2-model", type=str, help="K2 模型 ID")
    
    args = parser.parse_args()
    
    manager = ClaudeToolModeManager()
    
    if args.action == "enable":
        manager.enable_tool_mode()
        print("✅ Claude 工具模式已启用")
    
    elif args.action == "disable":
        manager.disable_tool_mode()
        print("✅ Claude 工具模式已禁用")
    
    elif args.action == "config":
        manager.configure_k2_service(
            url=args.k2_url,
            api_key=args.k2_key,
            model_id=args.k2_model
        )
        print("✅ K2 服务配置已更新")
    
    elif args.action == "status":
        stats = manager.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

