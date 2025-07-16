# Claude Code + PowerAutomation K2 路由配置指南

## 🎯 **目标**
配置 Claude Code 使用 PowerAutomation 的 K2 路由，完全避免 Claude 模型服务余额消耗。

## 🔧 **配置步骤**

### **第一步：运行代理配置脚本**

在您的 aicore0716 目录中运行：

```bash
cd /Users/alexchuang/Desktop/alex/tests/package1/aicore0716
bash claude_code_proxy_config.sh
```

这将创建：
- 🔧 Claude API 代理服务器
- 🚀 代理启动脚本
- ⚙️ 环境变量配置

### **第二步：启动代理服务器**

在**第一个终端窗口**中启动代理：

```bash
bash ~/.powerautomation/proxy/start_claude_proxy.sh
```

您应该看到：
```
🚀 Claude API 代理服务器已启动
📍 监听地址: http://127.0.0.1:8080
🎯 所有 Claude API 请求将路由到 PowerAutomation K2 服务
```

### **第三步：配置环境变量**

在**第二个终端窗口**中配置环境变量：

```bash
source ~/.powerautomation/proxy/claude_code_env.sh
```

您应该看到：
```
✅ Claude Code 环境变量已配置
🔄 API 请求将路由到: http://127.0.0.1:8080
🎯 PowerAutomation K2 服务将处理所有 AI 推理
```

### **第四步：启动 Claude Code**

在**同一个终端窗口**（已配置环境变量）中启动 Claude Code：

```bash
cd /Users/alexchuang/Desktop/alex/tests/package1/aicore0716
claude
```

## ✅ **验证配置**

### **测试 1：检查代理连接**
在 Claude Code 中输入：
```
> hi
```

如果配置成功，您应该看到：
- ❌ **不再出现** "Credit balance too low" 错误
- ✅ **正常响应** 来自 K2 服务的回复

### **测试 2：检查代理日志**
在代理服务器终端中，您应该看到：
```
🔄 拦截 Claude API 请求: /v1/messages
📝 请求数据: {...}
✅ K2 路由成功，返回响应
```

## 🔄 **工作原理**

```
Claude Code → 本地代理 (127.0.0.1:8080) → PowerAutomation K2 → 响应
     ↑                                                              ↓
环境变量重定向                                                    转换格式
```

1. **环境变量重定向** - Claude Code 的 API 请求被重定向到本地代理
2. **请求拦截** - 代理服务器拦截所有 Claude API 请求
3. **格式转换** - 将 Claude API 格式转换为 K2 API 格式
4. **K2 路由** - 发送到 PowerAutomation K2 服务进行 AI 推理
5. **响应转换** - 将 K2 响应转换回 Claude API 格式
6. **返回结果** - Claude Code 接收到正常的 API 响应

## 🎯 **核心优势**

- ✅ **零余额消耗** - 完全避免 Claude 模型服务费用
- ✅ **无缝体验** - Claude Code 使用体验完全不变
- ✅ **智能路由** - 自动使用 PowerAutomation K2 服务
- ✅ **格式兼容** - 完全兼容 Claude API 格式
- ✅ **实时监控** - 代理日志显示所有请求处理

## 🛠️ **故障排除**

### **问题 1：代理服务器启动失败**
```bash
# 检查端口是否被占用
lsof -i :8080

# 如果被占用，杀死进程
kill -9 $(lsof -t -i:8080)

# 重新启动代理
bash ~/.powerautomation/proxy/start_claude_proxy.sh
```

### **问题 2：环境变量未生效**
```bash
# 检查环境变量
echo $ANTHROPIC_API_URL
echo $CLAUDE_API_URL

# 如果为空，重新配置
source ~/.powerautomation/proxy/claude_code_env.sh
```

### **问题 3：仍然出现余额错误**
```bash
# 确保在配置了环境变量的终端中启动 Claude Code
source ~/.powerautomation/proxy/claude_code_env.sh
claude
```

## 📋 **快速启动脚本**

创建一个快速启动脚本：

```bash
cat > ~/start_claude_with_k2.sh << 'EOF'
#!/bin/bash
echo "🚀 启动 Claude Code + PowerAutomation K2 路由..."

# 启动代理服务器（后台运行）
bash ~/.powerautomation/proxy/start_claude_proxy.sh &
PROXY_PID=$!

# 等待代理启动
sleep 3

# 配置环境变量
source ~/.powerautomation/proxy/claude_code_env.sh

# 启动 Claude Code
cd /Users/alexchuang/Desktop/alex/tests/package1/aicore0716
claude

# 清理：停止代理服务器
kill $PROXY_PID
EOF

chmod +x ~/start_claude_with_k2.sh
```

然后只需运行：
```bash
bash ~/start_claude_with_k2.sh
```

## 🎉 **成功标志**

配置成功后，您将看到：
- ✅ Claude Code 正常启动和响应
- ✅ 代理日志显示请求拦截和路由
- ✅ 不再出现余额不足错误
- ✅ 所有 AI 推理通过 K2 服务处理

**现在您可以无限制地使用 Claude Code，而不消耗任何 Claude 模型服务余额！** 🚀

