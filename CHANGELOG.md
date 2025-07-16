# Changelog

## [4.6.9.7] - 2025-07-16

### Added
- 统一 MCP 架构，整合所有相关组件
- Claude Code 同步服务，与 ClaudeEditor 无缝同步
- Claude 工具模式，完全避免模型推理余额消耗
- K2 服务路由，自动路由 AI 推理任务到 K2
- 一键安装脚本，支持 npm/curl 安装
- 统一命令行接口，简化操作

### Features
- ✅ 零余额消耗 - 完全避免 Claude 模型推理费用
- ✅ 无缝同步 - ClaudeEditor 和本地环境实时同步
- ✅ 智能路由 - AI 推理任务自动路由到 K2 服务
- ✅ 工具保留 - 保留所有 Claude 工具和指令功能
- ✅ 一键安装 - npm/curl 一键安装，开箱即用

### Technical
- 移除分散的组件目录，统一为 powerautomation_unified_mcp
- 优化 WebSocket 连接和 HTTP 回退机制
- 改进错误处理和日志记录
- 增强配置管理和状态监控

### Installation
```bash
npm install -g powerautomation-unified
```

### Usage
```bash
powerautomation start
powerautomation status
powerautomation test
```
