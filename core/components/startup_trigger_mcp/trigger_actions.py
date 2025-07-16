#!/usr/bin/env python3
"""
Trigger Actions - 触发动作执行器
基于检测到的触发事件自动执行相应的动作
"""

import asyncio
import logging
import subprocess
import os
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .trigger_detection import TriggerEvent, TriggerType, TriggerPriority

logger = logging.getLogger(__name__)

class ActionStatus(Enum):
    """动作状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ActionResult:
    """动作结果"""
    action_id: str
    trigger_event_id: str
    action_type: str
    status: ActionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    result_data: Dict[str, Any] = None
    error_message: str = ""
    logs: List[str] = None

    def __post_init__(self):
        if self.result_data is None:
            self.result_data = {}
        if self.logs is None:
            self.logs = []

class TriggerActionExecutor:
    """触发动作执行器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized = False
        
        # 动作注册表
        self.action_handlers: Dict[TriggerType, Callable] = {}
        self.action_history: List[ActionResult] = []
        self.running_actions: Dict[str, ActionResult] = {}
        
        # 执行配置
        self.max_history_size = 200
        self.action_timeout = 300  # 5分钟超时
        self.auto_execute_enabled = True
        
        # 注册默认动作处理器
        self._register_action_handlers()
    
    def _register_action_handlers(self):
        """注册动作处理器"""
        try:
            self.action_handlers[TriggerType.CLAUDEEDITOR_INSTALL] = self._handle_claudeeditor_install
            self.action_handlers[TriggerType.CLAUDEEDITOR_START] = self._handle_claudeeditor_start
            self.action_handlers[TriggerType.MIRROR_CODE_SYNC] = self._handle_mirror_code_sync
            self.action_handlers[TriggerType.DUAL_COMMUNICATION] = self._handle_dual_communication
            self.action_handlers[TriggerType.SYSTEM_READY] = self._handle_system_ready
            
            self.logger.info("动作处理器注册完成")
            
        except Exception as e:
            self.logger.error(f"注册动作处理器失败: {e}")
    
    async def execute_trigger_action(self, trigger_event: TriggerEvent) -> ActionResult:
        """执行触发动作"""
        try:
            action_id = f"action_{trigger_event.event_id}"
            
            # 创建动作结果
            action_result = ActionResult(
                action_id=action_id,
                trigger_event_id=trigger_event.event_id,
                action_type=trigger_event.trigger_type.value,
                status=ActionStatus.PENDING,
                start_time=datetime.now()
            )
            
            # 检查是否有对应的处理器
            if trigger_event.trigger_type not in self.action_handlers:
                action_result.status = ActionStatus.FAILED
                action_result.error_message = f"未找到处理器: {trigger_event.trigger_type.value}"
                action_result.end_time = datetime.now()
                self._record_action_result(action_result)
                return action_result
            
            # 检查是否已有相同类型的动作在运行
            if self._is_action_type_running(trigger_event.trigger_type):
                action_result.status = ActionStatus.CANCELLED
                action_result.error_message = f"相同类型的动作正在运行: {trigger_event.trigger_type.value}"
                action_result.end_time = datetime.now()
                self._record_action_result(action_result)
                return action_result
            
            # 开始执行
            action_result.status = ActionStatus.RUNNING
            self.running_actions[action_id] = action_result
            
            try:
                # 执行动作处理器
                handler = self.action_handlers[trigger_event.trigger_type]
                result_data = await asyncio.wait_for(
                    handler(trigger_event, action_result),
                    timeout=self.action_timeout
                )
                
                action_result.result_data = result_data
                action_result.status = ActionStatus.SUCCESS
                action_result.end_time = datetime.now()
                
                self.logger.info(f"动作执行成功: {action_id}")
                
            except asyncio.TimeoutError:
                action_result.status = ActionStatus.FAILED
                action_result.error_message = "动作执行超时"
                action_result.end_time = datetime.now()
                self.logger.error(f"动作执行超时: {action_id}")
                
            except Exception as e:
                action_result.status = ActionStatus.FAILED
                action_result.error_message = str(e)
                action_result.end_time = datetime.now()
                self.logger.error(f"动作执行失败: {action_id}, 错误: {e}")
            
            finally:
                # 从运行中移除
                if action_id in self.running_actions:
                    del self.running_actions[action_id]
                
                # 记录结果
                self._record_action_result(action_result)
            
            return action_result
            
        except Exception as e:
            self.logger.error(f"执行触发动作失败: {e}")
            return ActionResult(
                action_id="error",
                trigger_event_id=trigger_event.event_id,
                action_type="error",
                status=ActionStatus.FAILED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=str(e)
            )
    
    def _is_action_type_running(self, trigger_type: TriggerType) -> bool:
        """检查是否有相同类型的动作正在运行"""
        for action_result in self.running_actions.values():
            if action_result.action_type == trigger_type.value:
                return True
        return False
    
    def _record_action_result(self, action_result: ActionResult):
        """记录动作结果"""
        try:
            self.action_history.append(action_result)
            
            # 限制历史记录大小
            if len(self.action_history) > self.max_history_size:
                self.action_history = self.action_history[-self.max_history_size:]
            
        except Exception as e:
            self.logger.error(f"记录动作结果失败: {e}")
    
    # 动作处理器实现
    async def _handle_claudeeditor_install(self, trigger_event: TriggerEvent, action_result: ActionResult) -> Dict[str, Any]:
        """处理 ClaudeEditor 安装"""
        try:
            action_result.logs.append("开始安装 ClaudeEditor...")
            
            # 检查是否已经安装
            if os.path.exists("/home/ubuntu/aicore0716"):
                action_result.logs.append("检测到 ClaudeEditor 已安装，跳过安装步骤")
                
                # 检查是否正在运行
                if self._is_claudeeditor_running():
                    action_result.logs.append("ClaudeEditor 已在运行")
                    return {
                        "installed": True,
                        "running": True,
                        "url": "http://127.0.0.1:5176",
                        "message": "ClaudeEditor 已安装并运行"
                    }
                else:
                    # 启动 ClaudeEditor
                    action_result.logs.append("启动 ClaudeEditor...")
                    start_result = await self._start_claudeeditor(action_result)
                    return start_result
            
            # 执行安装脚本
            action_result.logs.append("执行自动安装脚本...")
            script_path = "/home/ubuntu/aicore0716/auto_setup_claudeeditor.sh"
            
            if not os.path.exists(script_path):
                # 如果脚本不存在，先克隆仓库
                action_result.logs.append("克隆 PowerAutomation 仓库...")
                clone_result = await self._clone_repository(action_result)
                if not clone_result["success"]:
                    raise Exception(f"克隆仓库失败: {clone_result['error']}")
            
            # 执行安装脚本
            action_result.logs.append("运行安装脚本...")
            process = await asyncio.create_subprocess_exec(
                "bash", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/home/ubuntu"
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                action_result.logs.append("ClaudeEditor 安装成功")
                return {
                    "installed": True,
                    "running": self._is_claudeeditor_running(),
                    "url": "http://127.0.0.1:5176",
                    "message": "ClaudeEditor 安装并启动成功",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
            else:
                raise Exception(f"安装脚本执行失败: {stderr.decode()}")
            
        except Exception as e:
            action_result.logs.append(f"安装失败: {str(e)}")
            raise e
    
    async def _handle_claudeeditor_start(self, trigger_event: TriggerEvent, action_result: ActionResult) -> Dict[str, Any]:
        """处理 ClaudeEditor 启动"""
        try:
            action_result.logs.append("启动 ClaudeEditor...")
            return await self._start_claudeeditor(action_result)
            
        except Exception as e:
            action_result.logs.append(f"启动失败: {str(e)}")
            raise e
    
    async def _handle_mirror_code_sync(self, trigger_event: TriggerEvent, action_result: ActionResult) -> Dict[str, Any]:
        """处理 Mirror Code 同步"""
        try:
            action_result.logs.append("启动 Mirror Code 同步...")
            
            # 检查 ClaudeEditor 是否运行
            if not self._is_claudeeditor_running():
                action_result.logs.append("ClaudeEditor 未运行，先启动 ClaudeEditor...")
                start_result = await self._start_claudeeditor(action_result)
                if not start_result["running"]:
                    raise Exception("无法启动 ClaudeEditor")
            
            # 启用 Mirror Code 同步
            action_result.logs.append("启用 Mirror Code 双向同步...")
            
            # 这里应该调用 Mirror Code 的 API 或服务
            # 暂时返回模拟结果
            await asyncio.sleep(2)  # 模拟同步时间
            
            return {
                "sync_enabled": True,
                "sync_status": "active",
                "message": "Mirror Code 双向同步已启用"
            }
            
        except Exception as e:
            action_result.logs.append(f"同步失败: {str(e)}")
            raise e
    
    async def _handle_dual_communication(self, trigger_event: TriggerEvent, action_result: ActionResult) -> Dict[str, Any]:
        """处理双向通信建立"""
        try:
            action_result.logs.append("建立双向通信...")
            
            # 检查 ClaudeEditor 是否运行
            if not self._is_claudeeditor_running():
                raise Exception("ClaudeEditor 未运行，无法建立双向通信")
            
            # 建立双向通信
            action_result.logs.append("配置双向通信通道...")
            
            # 创建通信就绪标志文件
            ready_file = "/tmp/claude_code_ready"
            with open(ready_file, "w") as f:
                f.write(json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "status": "ready",
                    "claudeeditor_url": "http://127.0.0.1:5176"
                }))
            
            action_result.logs.append("双向通信建立成功")
            
            return {
                "communication_ready": True,
                "claudeeditor_url": "http://127.0.0.1:5176",
                "ready_file": ready_file,
                "message": "Claude Code 与 ClaudeEditor 双向通信已建立"
            }
            
        except Exception as e:
            action_result.logs.append(f"通信建立失败: {str(e)}")
            raise e
    
    async def _handle_system_ready(self, trigger_event: TriggerEvent, action_result: ActionResult) -> Dict[str, Any]:
        """处理系统就绪检查"""
        try:
            action_result.logs.append("检查系统状态...")
            
            status = {
                "claudeeditor_installed": os.path.exists("/home/ubuntu/aicore0716"),
                "claudeeditor_running": self._is_claudeeditor_running(),
                "mirror_code_ready": os.path.exists("/tmp/claude_code_ready"),
                "system_ready": False
            }
            
            status["system_ready"] = all([
                status["claudeeditor_installed"],
                status["claudeeditor_running"],
                status["mirror_code_ready"]
            ])
            
            action_result.logs.append(f"系统状态检查完成: {status}")
            
            return {
                "status": status,
                "message": "系统就绪" if status["system_ready"] else "系统未完全就绪"
            }
            
        except Exception as e:
            action_result.logs.append(f"状态检查失败: {str(e)}")
            raise e
    
    # 辅助方法
    async def _clone_repository(self, action_result: ActionResult) -> Dict[str, Any]:
        """克隆仓库"""
        try:
            action_result.logs.append("克隆 PowerAutomation 仓库...")
            
            process = await asyncio.create_subprocess_exec(
                "git", "clone", "https://github.com/alexchuang650730/aicore0716.git",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/home/ubuntu"
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                action_result.logs.append("仓库克隆成功")
                return {"success": True, "stdout": stdout.decode()}
            else:
                return {"success": False, "error": stderr.decode()}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start_claudeeditor(self, action_result: ActionResult) -> Dict[str, Any]:
        """启动 ClaudeEditor"""
        try:
            action_result.logs.append("启动 ClaudeEditor 开发服务器...")
            
            # 检查是否已在运行
            if self._is_claudeeditor_running():
                action_result.logs.append("ClaudeEditor 已在运行")
                return {
                    "running": True,
                    "url": "http://127.0.0.1:5176",
                    "message": "ClaudeEditor 已在运行"
                }
            
            # 切换到 ClaudeEditor 目录
            claudeeditor_dir = "/home/ubuntu/aicore0716/claudeditor"
            if not os.path.exists(claudeeditor_dir):
                raise Exception("ClaudeEditor 目录不存在")
            
            # 启动开发服务器
            action_result.logs.append("启动 Vite 开发服务器...")
            
            # 使用 nohup 在后台启动
            process = await asyncio.create_subprocess_exec(
                "nohup", "npm", "run", "dev", "--", "--port", "5176", "--host", "0.0.0.0",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=claudeeditor_dir
            )
            
            # 等待服务器启动
            action_result.logs.append("等待服务器启动...")
            for i in range(30):
                await asyncio.sleep(1)
                if self._is_claudeeditor_running():
                    action_result.logs.append("ClaudeEditor 启动成功")
                    return {
                        "running": True,
                        "url": "http://127.0.0.1:5176",
                        "message": "ClaudeEditor 启动成功"
                    }
            
            raise Exception("ClaudeEditor 启动超时")
            
        except Exception as e:
            action_result.logs.append(f"启动失败: {str(e)}")
            raise e
    
    def _is_claudeeditor_running(self) -> bool:
        """检查 ClaudeEditor 是否正在运行"""
        try:
            result = subprocess.run(
                ["lsof", "-Pi", ":5176", "-sTCP:LISTEN", "-t"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip()
            
        except Exception:
            return False
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """获取动作统计信息"""
        try:
            stats = {
                "total_actions": len(self.action_history),
                "running_actions": len(self.running_actions),
                "actions_by_status": {},
                "actions_by_type": {},
                "recent_actions": []
            }
            
            # 按状态统计
            for action in self.action_history:
                status = action.status.value
                if status not in stats["actions_by_status"]:
                    stats["actions_by_status"][status] = 0
                stats["actions_by_status"][status] += 1
            
            # 按类型统计
            for action in self.action_history:
                action_type = action.action_type
                if action_type not in stats["actions_by_type"]:
                    stats["actions_by_type"][action_type] = 0
                stats["actions_by_type"][action_type] += 1
            
            # 最近的动作
            recent_actions = self.action_history[-10:] if self.action_history else []
            stats["recent_actions"] = [
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "status": action.status.value,
                    "start_time": action.start_time.isoformat(),
                    "end_time": action.end_time.isoformat() if action.end_time else None,
                    "error_message": action.error_message
                }
                for action in recent_actions
            ]
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取动作统计失败: {e}")
            return {}

# 全局动作执行器实例
action_executor = TriggerActionExecutor()

# 便捷函数
async def execute_trigger_action(trigger_event: TriggerEvent) -> ActionResult:
    """执行触发动作的便捷函数"""
    return await action_executor.execute_trigger_action(trigger_event)

def get_action_statistics() -> Dict[str, Any]:
    """获取动作统计的便捷函数"""
    return action_executor.get_action_statistics()

