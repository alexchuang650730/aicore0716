# ClaudeEditor 目录结构

## 📁 **标准目录结构**

```
claudeditor/
├── components/                 # 组件和生成器
│   └── claudeditor_test_generator.py
├── scripts/                   # 安装和配置脚本
│   └── auto_setup_claudeeditor.sh
├── integration/              # 集成测试和组件
│   ├── claude_claudeditor_integration_simple_test.py
│   └── claude_code_memoryos_integration.py
├── tests/                    # 单元测试
├── utils/                    # 工具函数
├── api/                      # API 相关文件
│   ├── ai_assistant_backend.py
│   ├── session_sharing_backend.py
│   ├── url_processor.py
│   └── src/                  # API 源代码
├── src/                      # 主要源代码
│   ├── claudeditor_ui_main.py
│   ├── claudeditor_agui_interface.py
│   ├── claudeditor_simple_ui_server.py
│   ├── claudeditor_testing_management_ui.py
│   ├── ai-assistant/         # AI 助手组件
│   ├── collaboration/        # 协作功能
│   ├── components/           # UI 组件
│   ├── editor/               # 编辑器核心
│   ├── lsp/                  # 语言服务器协议
│   ├── services/             # 服务层
│   └── styles/               # 样式文件
├── ui/                       # 用户界面组件
│   ├── mirror_code/          # 镜像代码组件
│   └── src/                  # UI 源代码
├── static/                   # 静态资源
│   ├── css/                  # 样式文件
│   └── js/                   # JavaScript 文件
├── templates/                # 模板文件
├── src-tauri/                # Tauri 桌面应用
│   ├── icons/                # 应用图标
│   └── src/                  # Rust 源代码
└── node_modules/             # Node.js 依赖
```

## 🎯 **目录功能说明**

### **核心目录**
- **src/**: 主要的 Python 源代码，包含所有 UI 和核心功能
- **api/**: 后端 API 服务和处理器
- **components/**: 可复用的组件和生成器
- **utils/**: 工具函数和辅助模块

### **开发目录**
- **tests/**: 单元测试和测试工具
- **integration/**: 集成测试和组件集成
- **scripts/**: 安装、配置和部署脚本

### **前端目录**
- **ui/**: 用户界面组件和前端代码
- **static/**: 静态资源文件（CSS、JS、图片等）
- **templates/**: HTML 模板文件

### **构建目录**
- **src-tauri/**: Tauri 桌面应用构建文件
- **node_modules/**: Node.js 依赖包

## 📋 **文件移动记录**

### **v4.6.9.8 重构**
- `claudeditor_ui_main.py` → `src/`
- `claudeditor_agui_interface.py` → `src/`
- `claudeditor_simple_ui_server.py` → `src/`
- `claudeditor_testing_management_ui.py` → `src/`
- `ai_assistant_backend.py` → `api/`
- `session_sharing_backend.py` → `api/`

## 🚀 **使用说明**

### **启动主界面**
```bash
cd claudeditor
python src/claudeditor_ui_main.py
```

### **启动 AG-UI 界面**
```bash
python src/claudeditor_agui_interface.py
```

### **启动简单 UI 服务器**
```bash
python src/claudeditor_simple_ui_server.py
```

### **运行测试**
```bash
python tests/test_claudeditor.py
```

### **运行集成测试**
```bash
python integration/claude_claudeditor_integration_simple_test.py
```

## 📊 **统计信息**

- **Python 文件**: 25+ 个
- **JavaScript 文件**: 7,000+ 个
- **HTML 文件**: 10+ 个
- **总文件数**: 14,000+ 个

---

*最后更新: 2024-07-16*  
*版本: v4.6.9.8*
