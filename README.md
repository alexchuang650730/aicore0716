# PowerAutomation v4.6.97 - 革命性 Claude Code 代理解决方案

[![npm version](https://badge.fury.io/js/powerautomation-unified.svg)](https://www.npmjs.com/package/powerautomation-unified)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-14%2B-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)

## 🚀 **一键安装，立即使用**

```bash
curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/one_click_install.sh | bash
```

## 🎯 **核心价值**

### ✅ **零余额消耗**
- 完全避免 Claude API 推理费用
- 智能路由对话到免费 K2 服务
- 保留所有 Claude Code 工具功能

### ⚡ **高性能响应**
- **Groq**: 0.36s 超快响应时间
- **Together AI**: 详细回答备用服务
- 基于性能测试的最优配置

### 🔧 **功能完整**
- 支持 30+ Claude Code 内置指令
- 智能检测 Shell 命令
- 无缝工具执行体验

### 🎯 **极简体验**
- 一个命令完成所有安装
- 零配置自动启动
- 无需多窗口操作

## 📊 **性能对比**

| Provider | 响应时间 | TPS | 特点 |
|----------|----------|-----|------|
| **Groq** | **0.36s** | **24.7** | 🚀 主要服务，超快响应 |
| **Together AI** | 0.96s | 21.8 | 📝 备用服务，详细回答 |

## 🛠️ **安装方式**

### **方式 1: 一键安装（推荐）**

```bash
# 一个命令解决所有问题
curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/one_click_install.sh | bash
```

**自动完成的操作：**
- ✅ 检测操作系统 (macOS/Linux)
- ✅ 下载最终版代理 (Groq + Together AI)
- ✅ 安装 Python 依赖 (aiohttp, huggingface_hub)
- ✅ 配置环境变量 (HF_TOKEN)
- ✅ 创建启动脚本
- ✅ 配置 Claude Code 环境
- ✅ 一键启动服务

### **方式 2: npm 全局安装**

```bash
npm install -g powerautomation-unified
```

### **方式 3: 手动安装**

```bash
git clone https://github.com/alexchuang650730/aicore0716.git
cd aicore0716
npm install
node scripts/install.js
```

## 🔑 **环境配置**

### **必需配置**
```bash
export HF_TOKEN='your-huggingface-token'
```

### **可选配置**
```bash
export ANTHROPIC_API_KEY='your-claude-key'  # 启用工具功能
```

### **获取 HuggingFace Token**
1. 访问 [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. 创建新 Token
3. 启用 `Make calls to Inference Providers` 权限

## 🎯 **使用方式**

### **启动服务**
```bash
# 一键启动（安装后）
~/.powerautomation/run_all.sh

# 或分步启动
~/.powerautomation/start_proxy.sh
```

### **使用 Claude Code**
```bash
# 直接使用，无需额外配置
claude

# 测试对话功能
> hi
> 帮我分析这个项目

# 测试工具功能
> /help
> /status
> git status
```

## 🏗️ **架构设计**

```
Claude Code → 127.0.0.1:8080 (PowerAutomation 代理)
                    ↓
            [智能请求分析]
                    ↓
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
工具请求          对话请求          命令查询
↓ Claude API     ↓ Groq           ↓ Together AI
(保留功能)       (0.36s 响应)     (详细回答)
```

## ✨ **核心特性**

### **🔧 智能路由**
- **工具请求** → Claude API（保留完整功能）
- **对话请求** → Groq/Together AI（避免费用）
- **自动检测** → 30+ 内置指令 + Shell 命令

### **⚡ 高性能服务**
- **主要**: Groq via HuggingFace Hub
- **备用**: Together AI via HuggingFace Hub
- **模型**: moonshotai/Kimi-K2-Instruct

### **🛡️ 成本优化**
- **零推理费用** → 所有对话通过免费服务
- **工具保留** → 重要功能仍可使用
- **智能回退** → 服务失败时自动切换

## 📋 **支持的功能**

### **Claude Code 内置指令**
```
/help, /init, /status, /permissions, /terminal-setup
/install-github-app, /login, /settings, /clear, /reset
/version, /docs, /examples, /debug, /config, /workspace
/mcp, /memory, /model, /review, /upgrade, /vim
```

### **Shell 命令检测**
```
git, npm, pip, python, node, ls, cd, mkdir, rm, cp, mv
cat, echo, curl, wget, chmod, sudo, docker, kubectl
```

## 🔍 **故障排除**

### **常见问题**

#### **Q: HuggingFace Token 权限不足**
```bash
# 确保启用以下权限：
# ✅ Make calls to Inference Providers
# ✅ Make calls to your Inference Endpoints
```

#### **Q: 端口 8080 被占用**
```bash
# 停止占用进程
kill -9 $(lsof -ti:8080)

# 重新启动
~/.powerautomation/start_proxy.sh
```

#### **Q: Python 依赖问题**
```bash
# macOS 用户
pip3 install aiohttp huggingface_hub --break-system-packages --user

# Linux 用户
pip3 install aiohttp huggingface_hub --user
```

## 📈 **版本历史**

### **v4.6.97 (最新)**
- ✅ 基于性能测试的 Groq + Together AI 配置
- ✅ 一键安装脚本，零配置体验
- ✅ 移除 Mock 服务，只使用真实 provider
- ✅ 优化响应时间到 0.36s

### **v4.6.96**
- ✅ 多 Provider 支持
- ✅ 智能路由优化
- ✅ macOS 兼容性改进

## 🤝 **贡献指南**

```bash
# 克隆项目
git clone https://github.com/alexchuang650730/aicore0716.git

# 安装依赖
npm install

# 运行测试
npm test

# 提交 PR
git checkout -b feature/your-feature
git commit -m "feat: your feature"
git push origin feature/your-feature
```

## 📄 **许可证**

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 **相关链接**

- **GitHub**: https://github.com/alexchuang650730/aicore0716
- **npm**: https://www.npmjs.com/package/powerautomation-unified
- **Issues**: https://github.com/alexchuang650730/aicore0716/issues
- **HuggingFace**: https://huggingface.co/settings/tokens

## 💡 **技术支持**

- **GitHub Issues**: 技术问题和 bug 报告
- **Discussions**: 功能建议和使用交流
- **Email**: support@powerautomation.ai

---

**PowerAutomation v4.6.97** - 让 Claude Code 使用更智能、更经济、更高效！🚀

