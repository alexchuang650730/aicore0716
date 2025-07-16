#!/usr/bin/env python3
"""
Mirror Code Communication - Mirror Code 双向通信检测模块
监控和管理 Claude Code 与 ClaudeEditor 之间的双向通信
"""

import asyncio
import logging
import json
import os
import time
import aiohttp
import websockets
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class CommunicationStatus(Enum):
    """通信状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SYNCING = "syncing"
    ERROR = "error"
    TIMEOUT = "timeout"

class MessageType(Enum):
    """消息类型"""
    HEARTBEAT = "heartbeat"
    CODE_SYNC = "code_sync"
    STATUS_UPDATE = "status_update"
    COMMAND_REQUEST = "command_request"
    COMMAND_RESPONSE = "command_response"
    FILE_CHANGE = "file_change"
    SYSTEM_EVENT = "system_event"

@dataclass
class CommunicationMessage:
    """通信消息"""
    message_id: str
    message_type: MessageType
    source: str
    target: str
    timestamp: datetime
    data: Dict[str, Any]
    priority: int = 0

@dataclass
class CommunicationChannel:
    """通信通道"""
    channel_id: str
    channel_type: str  # websocket, http, file
    endpoint: str
    status: CommunicationStatus
    last_activity: datetime
    message_count: int = 0
    error_count: int = 0

class MirrorCodeCommunicator:
    """Mirror Code 通信器"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized = False
        
        # 通信配置
        self.claudeeditor_url = "http://127.0.0.1:5176"
        self.websocket_url = "ws://127.0.0.1:5176/ws"
        self.api_endpoint = "http://127.0.0.1:5176/api"
        
        # 通信状态
        self.communication_status = CommunicationStatus.DISCONNECTED
        self.channels: Dict[str, CommunicationChannel] = {}
        self.message_history: List[CommunicationMessage] = []
        
        # 配置参数
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self.connection_timeout = 10  # 连接超时（秒）
        self.max_retry_attempts = 5
        self.max_message_history = 500
        
        # 监控任务
        self.monitoring_task = None
        self.heartbeat_task = None
        
        # 回调函数
        self.message_callbacks: Dict[MessageType, List[Callable]] = {}
        self.status_callbacks: List[Callable] = []
        
        # 同步状态
        self.sync_enabled = False
        self.last_sync_time = None
        self.sync_statistics = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "last_sync_duration": 0
        }
    
    async def initialize(self) -> bool:
        """初始化通信器"""
        try:
            self.logger.info("初始化 Mirror Code 通信器...")
            
            # 检查 ClaudeEditor 是否运行
            if not await self._check_claudeeditor_availability():
                self.logger.warning("ClaudeEditor 不可用，通信器将在检测到可用时自动连接")
                self.communication_status = CommunicationStatus.DISCONNECTED
            else:
                # 建立通信通道
                await self._establish_communication_channels()
            
            # 启动监控任务
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            self.initialized = True
            self.logger.info("Mirror Code 通信器初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化 Mirror Code 通信器失败: {e}")
            return False
    
    async def _check_claudeeditor_availability(self) -> bool:
        """检查 ClaudeEditor 可用性"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(self.claudeeditor_url) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def _establish_communication_channels(self):
        """建立通信通道"""
        try:
            self.communication_status = CommunicationStatus.CONNECTING
            
            # 建立 HTTP 通道
            http_channel = CommunicationChannel(
                channel_id="http_api",
                channel_type="http",
                endpoint=self.api_endpoint,
                status=CommunicationStatus.DISCONNECTED,
                last_activity=datetime.now()
            )
            
            if await self._test_http_channel(http_channel):
                http_channel.status = CommunicationStatus.CONNECTED
                self.channels["http_api"] = http_channel
                self.logger.info("HTTP 通道建立成功")
            
            # 建立 WebSocket 通道
            websocket_channel = CommunicationChannel(
                channel_id="websocket",
                channel_type="websocket",
                endpoint=self.websocket_url,
                status=CommunicationStatus.DISCONNECTED,
                last_activity=datetime.now()
            )
            
            if await self._test_websocket_channel(websocket_channel):
                websocket_channel.status = CommunicationStatus.CONNECTED
                self.channels["websocket"] = websocket_channel
                self.logger.info("WebSocket 通道建立成功")
            
            # 建立文件通道
            file_channel = CommunicationChannel(
                channel_id="file_sync",
                channel_type="file",
                endpoint="/tmp/claude_code_sync",
                status=CommunicationStatus.CONNECTED,
                last_activity=datetime.now()
            )
            self.channels["file_sync"] = file_channel
            self._ensure_sync_directory()
            self.logger.info("文件同步通道建立成功")
            
            # 更新通信状态
            if any(channel.status == CommunicationStatus.CONNECTED for channel in self.channels.values()):
                self.communication_status = CommunicationStatus.CONNECTED
                
                # 启动心跳
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                # 通知状态变更
                await self._notify_status_change()
            
        except Exception as e:
            self.logger.error(f"建立通信通道失败: {e}")
            self.communication_status = CommunicationStatus.ERROR
    
    async def _test_http_channel(self, channel: CommunicationChannel) -> bool:
        """测试 HTTP 通道"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.connection_timeout)) as session:
                test_url = f"{channel.endpoint}/health"
                async with session.get(test_url) as response:
                    if response.status == 200:
                        channel.last_activity = datetime.now()
                        return True
                    return False
        except Exception as e:
            self.logger.debug(f"HTTP 通道测试失败: {e}")
            return False
    
    async def _test_websocket_channel(self, channel: CommunicationChannel) -> bool:
        """测试 WebSocket 通道"""
        try:
            async with websockets.connect(
                channel.endpoint,
                timeout=self.connection_timeout
            ) as websocket:
                # 发送测试消息
                test_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(test_message))
                
                # 等待响应
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                if response_data.get("type") == "pong":
                    channel.last_activity = datetime.now()
                    return True
                return False
                
        except Exception as e:
            self.logger.debug(f"WebSocket 通道测试失败: {e}")
            return False
    
    def _ensure_sync_directory(self):
        """确保同步目录存在"""
        try:
            sync_dir = "/tmp/claude_code_sync"
            os.makedirs(sync_dir, exist_ok=True)
            
            # 创建状态文件
            status_file = os.path.join(sync_dir, "communication_status.json")
            status_data = {
                "status": self.communication_status.value,
                "timestamp": datetime.now().isoformat(),
                "channels": len(self.channels)
            }
            
            with open(status_file, "w") as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"创建同步目录失败: {e}")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while True:
            try:
                await asyncio.sleep(10)  # 每10秒检查一次
                
                # 检查通道状态
                await self._check_channel_health()
                
                # 检查 ClaudeEditor 可用性
                if self.communication_status == CommunicationStatus.DISCONNECTED:
                    if await self._check_claudeeditor_availability():
                        self.logger.info("检测到 ClaudeEditor 可用，尝试重新连接...")
                        await self._establish_communication_channels()
                
                # 清理过期消息
                self._cleanup_message_history()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.communication_status == CommunicationStatus.CONNECTED:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                # 发送心跳消息
                heartbeat_message = CommunicationMessage(
                    message_id=str(uuid.uuid4()),
                    message_type=MessageType.HEARTBEAT,
                    source="claude_code",
                    target="claudeeditor",
                    timestamp=datetime.now(),
                    data={
                        "status": self.communication_status.value,
                        "sync_enabled": self.sync_enabled,
                        "channels": len(self.channels)
                    }
                )
                
                await self._send_message(heartbeat_message)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"心跳循环错误: {e}")
    
    async def _check_channel_health(self):
        """检查通道健康状态"""
        try:
            current_time = datetime.now()
            unhealthy_channels = []
            
            for channel_id, channel in self.channels.items():
                # 检查通道是否超时
                time_since_activity = current_time - channel.last_activity
                if time_since_activity > timedelta(minutes=5):
                    channel.status = CommunicationStatus.TIMEOUT
                    unhealthy_channels.append(channel_id)
                
                # 尝试恢复不健康的通道
                if channel.status in [CommunicationStatus.ERROR, CommunicationStatus.TIMEOUT]:
                    await self._recover_channel(channel)
            
            # 更新整体通信状态
            if unhealthy_channels:
                self.logger.warning(f"检测到不健康的通道: {unhealthy_channels}")
                
                # 如果所有通道都不健康，更新状态
                healthy_channels = [c for c in self.channels.values() 
                                  if c.status == CommunicationStatus.CONNECTED]
                if not healthy_channels:
                    self.communication_status = CommunicationStatus.ERROR
                    await self._notify_status_change()
            
        except Exception as e:
            self.logger.error(f"检查通道健康状态失败: {e}")
    
    async def _recover_channel(self, channel: CommunicationChannel):
        """恢复通道"""
        try:
            self.logger.info(f"尝试恢复通道: {channel.channel_id}")
            
            if channel.channel_type == "http":
                if await self._test_http_channel(channel):
                    channel.status = CommunicationStatus.CONNECTED
                    self.logger.info(f"HTTP 通道恢复成功: {channel.channel_id}")
            
            elif channel.channel_type == "websocket":
                if await self._test_websocket_channel(channel):
                    channel.status = CommunicationStatus.CONNECTED
                    self.logger.info(f"WebSocket 通道恢复成功: {channel.channel_id}")
            
            elif channel.channel_type == "file":
                # 文件通道通常不会失败，只需更新状态
                channel.status = CommunicationStatus.CONNECTED
                channel.last_activity = datetime.now()
                self._ensure_sync_directory()
            
        except Exception as e:
            self.logger.error(f"恢复通道失败: {channel.channel_id}, 错误: {e}")
            channel.error_count += 1
    
    async def _send_message(self, message: CommunicationMessage) -> bool:
        """发送消息"""
        try:
            # 选择最佳通道
            channel = self._select_best_channel(message.message_type)
            if not channel:
                self.logger.warning("没有可用的通信通道")
                return False
            
            success = False
            
            if channel.channel_type == "http":
                success = await self._send_http_message(channel, message)
            elif channel.channel_type == "websocket":
                success = await self._send_websocket_message(channel, message)
            elif channel.channel_type == "file":
                success = await self._send_file_message(channel, message)
            
            if success:
                channel.message_count += 1
                channel.last_activity = datetime.now()
                self._record_message(message)
            else:
                channel.error_count += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            return False
    
    def _select_best_channel(self, message_type: MessageType) -> Optional[CommunicationChannel]:
        """选择最佳通道"""
        # 根据消息类型选择最适合的通道
        if message_type == MessageType.HEARTBEAT:
            # 心跳优先使用 HTTP
            return self.channels.get("http_api")
        elif message_type == MessageType.CODE_SYNC:
            # 代码同步优先使用 WebSocket
            return self.channels.get("websocket") or self.channels.get("file_sync")
        elif message_type == MessageType.FILE_CHANGE:
            # 文件变更使用文件通道
            return self.channels.get("file_sync")
        else:
            # 其他消息使用可用的任何通道
            for channel in self.channels.values():
                if channel.status == CommunicationStatus.CONNECTED:
                    return channel
        
        return None
    
    async def _send_http_message(self, channel: CommunicationChannel, message: CommunicationMessage) -> bool:
        """通过 HTTP 发送消息"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = f"{channel.endpoint}/message"
                data = asdict(message)
                data["timestamp"] = message.timestamp.isoformat()
                
                async with session.post(url, json=data) as response:
                    return response.status == 200
                    
        except Exception as e:
            self.logger.debug(f"HTTP 消息发送失败: {e}")
            return False
    
    async def _send_websocket_message(self, channel: CommunicationChannel, message: CommunicationMessage) -> bool:
        """通过 WebSocket 发送消息"""
        try:
            async with websockets.connect(channel.endpoint, timeout=10) as websocket:
                data = asdict(message)
                data["timestamp"] = message.timestamp.isoformat()
                
                await websocket.send(json.dumps(data))
                return True
                
        except Exception as e:
            self.logger.debug(f"WebSocket 消息发送失败: {e}")
            return False
    
    async def _send_file_message(self, channel: CommunicationChannel, message: CommunicationMessage) -> bool:
        """通过文件发送消息"""
        try:
            sync_dir = channel.endpoint
            message_file = os.path.join(sync_dir, f"message_{message.message_id}.json")
            
            data = asdict(message)
            data["timestamp"] = message.timestamp.isoformat()
            
            with open(message_file, "w") as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"文件消息发送失败: {e}")
            return False
    
    def _record_message(self, message: CommunicationMessage):
        """记录消息"""
        try:
            self.message_history.append(message)
            
            # 限制历史记录大小
            if len(self.message_history) > self.max_message_history:
                self.message_history = self.message_history[-self.max_message_history:]
            
        except Exception as e:
            self.logger.error(f"记录消息失败: {e}")
    
    def _cleanup_message_history(self):
        """清理消息历史"""
        try:
            # 删除超过1小时的消息
            cutoff_time = datetime.now() - timedelta(hours=1)
            self.message_history = [
                msg for msg in self.message_history 
                if msg.timestamp > cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"清理消息历史失败: {e}")
    
    async def _notify_status_change(self):
        """通知状态变更"""
        try:
            for callback in self.status_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(self.communication_status)
                    else:
                        callback(self.communication_status)
                except Exception as e:
                    self.logger.error(f"状态回调执行失败: {e}")
                    
        except Exception as e:
            self.logger.error(f"通知状态变更失败: {e}")
    
    # 公共接口
    async def send_code_sync(self, code_data: Dict[str, Any]) -> bool:
        """发送代码同步"""
        try:
            message = CommunicationMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.CODE_SYNC,
                source="claude_code",
                target="claudeeditor",
                timestamp=datetime.now(),
                data=code_data,
                priority=1
            )
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"发送代码同步失败: {e}")
            return False
    
    async def send_command_request(self, command_data: Dict[str, Any]) -> bool:
        """发送命令请求"""
        try:
            message = CommunicationMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.COMMAND_REQUEST,
                source="claude_code",
                target="claudeeditor",
                timestamp=datetime.now(),
                data=command_data,
                priority=2
            )
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"发送命令请求失败: {e}")
            return False
    
    def register_message_callback(self, message_type: MessageType, callback: Callable):
        """注册消息回调"""
        if message_type not in self.message_callbacks:
            self.message_callbacks[message_type] = []
        self.message_callbacks[message_type].append(callback)
    
    def register_status_callback(self, callback: Callable):
        """注册状态回调"""
        self.status_callbacks.append(callback)
    
    def get_communication_status(self) -> Dict[str, Any]:
        """获取通信状态"""
        return {
            "status": self.communication_status.value,
            "channels": {
                channel_id: {
                    "type": channel.channel_type,
                    "status": channel.status.value,
                    "endpoint": channel.endpoint,
                    "last_activity": channel.last_activity.isoformat(),
                    "message_count": channel.message_count,
                    "error_count": channel.error_count
                }
                for channel_id, channel in self.channels.items()
            },
            "sync_enabled": self.sync_enabled,
            "sync_statistics": self.sync_statistics,
            "message_history_count": len(self.message_history)
        }
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 取消监控任务
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # 取消心跳任务
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            self.communication_status = CommunicationStatus.DISCONNECTED
            self.logger.info("Mirror Code 通信器清理完成")
            
        except Exception as e:
            self.logger.error(f"清理 Mirror Code 通信器失败: {e}")

# 全局通信器实例
mirror_code_communicator = MirrorCodeCommunicator()

# 便捷函数
async def initialize_mirror_code_communication() -> bool:
    """初始化 Mirror Code 通信的便捷函数"""
    return await mirror_code_communicator.initialize()

async def send_code_sync(code_data: Dict[str, Any]) -> bool:
    """发送代码同步的便捷函数"""
    return await mirror_code_communicator.send_code_sync(code_data)

async def send_command_request(command_data: Dict[str, Any]) -> bool:
    """发送命令请求的便捷函数"""
    return await mirror_code_communicator.send_command_request(command_data)

def get_mirror_code_status() -> Dict[str, Any]:
    """获取 Mirror Code 状态的便捷函数"""
    return mirror_code_communicator.get_communication_status()

async def cleanup_mirror_code_communication():
    """清理 Mirror Code 通信的便捷函数"""
    await mirror_code_communicator.cleanup()

