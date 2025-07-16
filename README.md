# PowerAutomation v4.6.9.7 - 统一 MCP 解决方案

[![npm version](https://badge.fury.io/js/powerautomation-unified.svg)](https://badge.fury.io/js/powerautomation-unified)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D14.0.0-brightgreen.svg)](https://nodejs.org/)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.8.0-blue.svg)](https://www.python.org/)

> 🚀 **革命性的 AI 开发解决方案** - 完全避免 Claude 模型推理余额消耗，保留所有工具功能，自动路由 AI 推理到 K2 服务

## ✨ 核心特性

### 🎯 **零余额消耗**
- ✅ 完全禁用 Claude 模型推理，避免意外费用
- ✅ 保留所有 Claude 工具和指令功能
- ✅ 智能拦截模型推理请求

### 🔄 **智能路由**
- ✅ 自动路由 AI 推理任务到 K2 服务
- ✅ 无缝切换，用户无感知
- ✅ 成本优化，性能保障

### 🔗 **无缝同步**
- ✅ ClaudeEditor 和本地环境实时同步
- ✅ WebSocket 连接 + HTTP 回退
- ✅ 代码执行结果即时反馈

### 🏗️ **统一架构**
- ✅ 一个 MCP 组件解决所有问题
- ✅ 简化配置，统一管理
- ✅ 模块化设计，易于扩展

## 🚀 快速开始

### 安装

#### 方式 1: npm 全局安装（推荐）
```bash
npm install -g powerautomation-unified
```

#### 方式 2: curl 一键安装
```bash
curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/install_powerautomation_v4697.sh | bash
```

#### 方式 3: 从 GitHub 安装
```bash
npm install -g https://github.com/alexchuang650730/aicore0716.git
```

### 基本使用

```bash
# 启动 PowerAutomation 服务
powerautomation start

# 查看服务状态
powerautomation status

# 测试所有功能
powerautomation test

# 查看帮助
powerautomation --help
```

## 📋 功能详解

### 🔧 Claude 工具模式

PowerAutomation 的核心创新 - 完全禁用 Claude 模型推理，只保留工具功能：

```bash
# 启用工具模式
powerautomation tool-mode --action enable

# 查看工具模式状态
powerautomation tool-mode --action status

# 管理允许的工具
powerautomation tool-mode --tool file_read --add
```

**支持的工具类型：**
- 📁 文件操作：`file_read`, `file_write`, `file_append`, `file_replace`
- 🖥️ Shell 命令：`shell_exec`, `shell_view`, `shell_wait`, `shell_input`
- 🌐 浏览器操作：`browser_navigate`, `browser_view`, `browser_click`
- 🎨 媒体生成：`media_generate_image`, `media_generate_video`
- 🔍 信息搜索：`info_search_web`, `info_search_image`

### 🔄 K2 服务路由

自动将 AI 推理任务路由到 K2 服务，实现成本优化：

```bash
# 测试 K2 路由
powerautomation k2-test

# 查看 K2 统计
powerautomation status | grep k2
```

**路由的请求类型：**
- 💬 聊天完成
- 📝 文本生成
- 💻 代码生成
- 📊 数据分析
- 🌐 翻译服务

### 🔗 Claude Code 同步

与 ClaudeEditor 的无缝同步功能：

```bash
# 测试同步功能
powerautomation claude-sync

# 查看同步状态
powerautomation status | grep sync
```

**同步功能：**
- 📝 代码实时同步
- ⚡ 命令执行结果反馈
- 🔄 双向通信
- 📊 状态监控

## ⚙️ 配置

### 环境要求

- **Node.js**: >= 14.0.0
- **Python**: >= 3.8.0
- **操作系统**: macOS, Linux, Windows

### 配置文件

PowerAutomation 的配置文件位于 `~/.powerautomation/`：

```
~/.powerautomation/
├── tool_mode.json          # 工具模式配置
├── k2_config.json          # K2 服务配置
├── sync_config.json        # 同步配置
└── powerautomation         # 启动脚本
```

### 高级配置

```bash
# 自定义配置
powerautomation start --host 0.0.0.0 --port 8765

# 禁用特定功能
powerautomation start --disable-claude-sync --disable-k2-router

# 调试模式
powerautomation start --log-level DEBUG
```

## 🏗️ 架构设计

```
PowerAutomation 统一 MCP
├── claude_sync/              # Claude Code 同步服务
│   ├── sync_manager.py       # 同步管理器
│   └── websocket_client.py   # WebSocket 客户端
├── k2_router/                # K2 服务路由
│   ├── k2_client.py          # K2 客户端
│   └── request_router.py     # 请求路由器
├── tool_mode/                # Claude 工具模式
│   ├── tool_manager.py       # 工具管理器
│   └── request_interceptor.py # 请求拦截器
├── startup_trigger/          # 启动触发管理
├── mirror_tracker/           # Mirror Code 追踪
└── unified_mcp_server.py     # 统一 MCP 服务器
```

## 📊 监控和统计

PowerAutomation 提供详细的监控和统计信息：

```bash
# 查看详细状态
powerautomation status

# 输出示例
{
  "server_name": "PowerAutomation Unified MCP",
  "version": "4.6.9.7",
  "running": true,
  "uptime_seconds": 3600,
  "stats": {
    "total_requests": 150,
    "k2_routes": 45,
    "claude_syncs": 30,
    "tool_blocks": 75
  },
  "components": {
    "claude_sync": {
      "connected": true,
      "total_syncs": 30,
      "success_rate": 100
    },
    "k2_router": {
      "connected": true,
      "total_requests": 45,
      "success_rate": 98.5,
      "total_cost": 0.0234
    },
    "tool_mode": {
      "enabled": true,
      "blocked_requests": 75,
      "allowed_tools": 120
    }
  }
}
```

## 🔧 故障排除

### 常见问题

#### 1. Python 依赖问题
```bash
# 安装 Python 依赖
pip3 install asyncio websockets httpx aiofiles

# 检查 Python 版本
python3 --version
```

#### 2. 权限问题
```bash
# 修复权限
chmod +x ~/.powerautomation/powerautomation

# 重新安装
powerautomation install
```

#### 3. 端口冲突
```bash
# 使用自定义端口
powerautomation start --port 8766
```

#### 4. K2 服务连接问题
```bash
# 测试 K2 连接
powerautomation k2-test

# 检查网络连接
curl -I https://cloud.infini-ai.com
```

### 日志调试

```bash
# 启用调试日志
powerautomation start --log-level DEBUG

# 查看日志文件
tail -f ~/.powerautomation/logs/powerautomation.log
```

## 🤝 贡献

我们欢迎社区贡献！请查看 [贡献指南](CONTRIBUTING.md)。

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/alexchuang650730/aicore0716.git
cd aicore0716

# 安装开发依赖
npm install

# 运行测试
npm test

# 本地开发
npm link
powerautomation start
```

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🔗 相关链接

- 📦 [npm 包](https://www.npmjs.com/package/powerautomation-unified)
- 🐙 [GitHub 仓库](https://github.com/alexchuang650730/aicore0716)
- 🐛 [问题反馈](https://github.com/alexchuang650730/aicore0716/issues)
- 📚 [文档](https://github.com/alexchuang650730/aicore0716/wiki)

## 🌟 支持项目

如果 PowerAutomation 对您有帮助，请给我们一个 ⭐️！

---

<div align="center">

**PowerAutomation v4.6.9.7** - 让 AI 开发更智能！

Made with ❤️ by PowerAutomation Team

</div>

