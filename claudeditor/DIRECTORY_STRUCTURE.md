# ClaudeEditor 目录结构

## 📁 目录组织

```
claudeditor/
├── scripts/                    # 安装和配置脚本
│   └── auto_setup_claudeeditor.sh
├── integration/               # 集成测试和组件
│   ├── claude_claudeditor_integration_simple_test.py
│   ├── claude_claudeditor_integration_test.py
│   └── claude_code_memoryos_integration.py
├── tests/                     # 单元测试
├── api/                       # API 相关文件
├── src/                       # 源代码
├── ui/                        # 用户界面组件
├── static/                    # 静态资源
├── templates/                 # 模板文件
└── 主要 Python 文件
    ├── claudeditor_ui_main.py
    ├── claudeditor_agui_interface.py
    ├── claudeditor_simple_ui_server.py
    ├── claudeditor_testing_management_ui.py
    ├── ai_assistant_backend.py
    └── session_sharing_backend.py
```

## 🎯 目录说明

### **scripts/**
- 包含 ClaudeEditor 的安装和配置脚本
- `auto_setup_claudeeditor.sh`: 自动安装脚本

### **integration/**
- 包含与其他组件的集成测试和集成代码
- `claude_claudeditor_integration_*.py`: 集成测试文件
- `claude_code_memoryos_integration.py`: 内存系统集成

### **tests/**
- 单元测试文件目录
- 用于存放各种测试用例

### **api/**
- API 相关的后端代码
- 数据库模型和路由定义

### **src/**
- 前端源代码
- React/Vue 组件和相关资源

### **ui/**
- 用户界面组件
- 自定义 UI 元素

## 🔧 使用说明

### 安装 ClaudeEditor
```bash
cd claudeditor
bash scripts/auto_setup_claudeeditor.sh
```

### 运行集成测试
```bash
cd claudeditor
python integration/claude_claudeditor_integration_simple_test.py
```

### 启动服务
```bash
cd claudeditor
python claudeditor_ui_main.py
```

## 📋 文件移动记录

以下文件已从根目录移动到 claudeditor 目录：

- `auto_setup_claudeeditor.sh` → `claudeditor/scripts/`
- `claude_claudeditor_integration_simple_test.py` → `claudeditor/integration/`
- `claude_claudeditor_integration_test.py` → `claudeditor/integration/`
- `claude_code_memoryos_integration.py` → `claudeditor/integration/`

所有相关的引用和配置文件已相应更新。
