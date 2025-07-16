import React, { useState, useEffect, useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import './MonacoEditorComponent.css';

// 专业的 Monaco Editor 组件，集成 LSP 功能
const MonacoEditorComponent = ({ isVisible, onClose, initialFile = null }) => {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  
  // 编辑器状态
  const [editorState, setEditorState] = useState({
    language: 'javascript',
    theme: 'vs-light',
    content: initialFile?.content || `// PowerAutomation ClaudeEditor - Monaco Editor with LSP
// 智能代码编辑器，支持语法高亮、智能补全、错误检测

import React from 'react';

/**
 * 示例组件 - 展示 Monaco Editor 的强大功能
 * @param {Object} props - 组件属性
 * @returns {JSX.Element} React 组件
 */
const ExampleComponent = ({ title, data }) => {
  const [state, setState] = React.useState({
    loading: false,
    items: data || []
  });

  // 异步数据处理函数
  const handleDataFetch = async () => {
    setState(prev => ({ ...prev, loading: true }));
    
    try {
      const response = await fetch('/api/data');
      const result = await response.json();
      
      setState({
        loading: false,
        items: result.items
      });
    } catch (error) {
      console.error('数据获取失败:', error);
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  return (
    <div className="example-component">
      <h2>{title}</h2>
      {state.loading ? (
        <div>加载中...</div>
      ) : (
        <ul>
          {state.items.map((item, index) => (
            <li key={index}>{item.name}</li>
          ))}
        </ul>
      )}
      <button onClick={handleDataFetch}>
        刷新数据
      </button>
    </div>
  );
};

export default ExampleComponent;`,
    fileName: initialFile?.name || 'example.jsx',
    modified: false,
    cursorPosition: { line: 1, column: 1 },
    selections: []
  });

  // LSP 功能状态
  const [lspState, setLspState] = useState({
    diagnostics: [],
    completions: [],
    hover: null,
    definitions: [],
    references: [],
    symbols: [],
    isConnected: false,
    serverStatus: 'disconnected'
  });

  // 文件管理状态
  const [fileManager, setFileManager] = useState({
    openFiles: [
      { name: 'example.jsx', content: editorState.content, language: 'javascript', modified: false },
      { name: 'styles.css', content: '/* CSS 样式文件 */\n.example-component {\n  padding: 20px;\n  border: 1px solid #ccc;\n}\n\n.example-component h2 {\n  color: #333;\n  margin-bottom: 16px;\n}', language: 'css', modified: false },
      { name: 'config.json', content: '{\n  "name": "PowerAutomation",\n  "version": "4.6.9.6",\n  "description": "智能开发平台",\n  "main": "index.js",\n  "scripts": {\n    "start": "react-scripts start",\n    "build": "react-scripts build",\n    "test": "react-scripts test"\n  }\n}', language: 'json', modified: false }
    ],
    activeFileIndex: 0,
    recentFiles: []
  });

  // 编辑器配置
  const editorOptions = {
    selectOnLineNumbers: true,
    roundedSelection: false,
    readOnly: false,
    cursorStyle: 'line',
    automaticLayout: true,
    glyphMargin: true,
    useTabStops: false,
    fontSize: 14,
    lineHeight: 20,
    fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
    minimap: {
      enabled: true,
      side: 'right'
    },
    scrollBeyondLastLine: false,
    wordWrap: 'on',
    theme: editorState.theme,
    language: editorState.language,
    // LSP 相关配置
    quickSuggestions: {
      other: true,
      comments: true,
      strings: true
    },
    parameterHints: {
      enabled: true
    },
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: 'on',
    tabCompletion: 'on',
    wordBasedSuggestions: true,
    // 错误和警告
    renderValidationDecorations: 'on',
    // 代码折叠
    folding: true,
    foldingStrategy: 'auto',
    showFoldingControls: 'always',
    // 括号匹配
    matchBrackets: 'always',
    // 自动缩进
    autoIndent: 'full',
    formatOnPaste: true,
    formatOnType: true
  };

  // 初始化 Monaco Editor
  const handleEditorDidMount = useCallback((editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // 配置语言服务
    setupLanguageServices(monaco);
    
    // 设置主题
    setupCustomThemes(monaco);
    
    // 注册快捷键
    registerKeyBindings(editor, monaco);
    
    // 启动 LSP 连接
    initializeLSP(editor, monaco);
    
    // 监听编辑器事件
    setupEditorEvents(editor, monaco);
    
    console.log('Monaco Editor 初始化完成');
  }, []);

  // 设置语言服务
  const setupLanguageServices = (monaco) => {
    // JavaScript/TypeScript 语言配置
    monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.ES2020,
      allowNonTsExtensions: true,
      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: monaco.languages.typescript.ModuleKind.CommonJS,
      noEmit: true,
      esModuleInterop: true,
      jsx: monaco.languages.typescript.JsxEmit.React,
      reactNamespace: 'React',
      allowJs: true,
      typeRoots: ['node_modules/@types']
    });

    // 添加 React 类型定义
    const reactTypes = `
      declare module 'react' {
        export interface Component<P = {}, S = {}> {}
        export function useState<T>(initialState: T): [T, (value: T) => void];
        export function useEffect(effect: () => void, deps?: any[]): void;
        export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
        export function useRef<T>(initialValue: T): { current: T };
        export const Fragment: any;
        export default React;
      }
    `;
    
    monaco.languages.typescript.javascriptDefaults.addExtraLib(
      reactTypes,
      'file:///node_modules/@types/react/index.d.ts'
    );

    // CSS 语言配置
    monaco.languages.css.cssDefaults.setOptions({
      validate: true,
      lint: {
        compatibleVendorPrefixes: 'ignore',
        vendorPrefix: 'warning',
        duplicateProperties: 'warning',
        emptyRules: 'warning',
        importStatement: 'ignore',
        boxModel: 'ignore',
        universalSelector: 'ignore',
        zeroUnits: 'ignore',
        fontFaceProperties: 'warning',
        hexColorLength: 'error',
        argumentsInColorFunction: 'error',
        unknownProperties: 'warning',
        ieHack: 'ignore',
        unknownVendorSpecificProperties: 'ignore',
        propertyIgnoredDueToDisplay: 'warning',
        important: 'ignore',
        float: 'ignore',
        idSelector: 'ignore'
      }
    });

    // JSON 语言配置
    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
      validate: true,
      allowComments: false,
      schemas: [{
        uri: 'http://myserver/package-schema.json',
        fileMatch: ['package.json'],
        schema: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            version: { type: 'string' },
            description: { type: 'string' },
            main: { type: 'string' },
            scripts: { type: 'object' }
          }
        }
      }]
    });
  };

  // 设置自定义主题
  const setupCustomThemes = (monaco) => {
    // PowerAutomation 亮色主题
    monaco.editor.defineTheme('powerautomation-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6a737d', fontStyle: 'italic' },
        { token: 'keyword', foreground: '8b5cf6', fontStyle: 'bold' },
        { token: 'string', foreground: '10b981' },
        { token: 'number', foreground: 'f59e0b' },
        { token: 'regexp', foreground: 'ec4899' },
        { token: 'type', foreground: '3b82f6' },
        { token: 'class', foreground: 'ef4444' },
        { token: 'function', foreground: '06b6d4' },
        { token: 'variable', foreground: '1f2937' }
      ],
      colors: {
        'editor.background': '#ffffff',
        'editor.foreground': '#1f2937',
        'editor.lineHighlightBackground': '#f8fafc',
        'editor.selectionBackground': '#e0e7ff',
        'editor.inactiveSelectionBackground': '#f1f5f9',
        'editorCursor.foreground': '#8b5cf6',
        'editorWhitespace.foreground': '#e5e7eb'
      }
    });

    // PowerAutomation 暗色主题
    monaco.editor.defineTheme('powerautomation-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6b7280', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'a78bfa', fontStyle: 'bold' },
        { token: 'string', foreground: '34d399' },
        { token: 'number', foreground: 'fbbf24' },
        { token: 'regexp', foreground: 'f472b6' },
        { token: 'type', foreground: '60a5fa' },
        { token: 'class', foreground: 'f87171' },
        { token: 'function', foreground: '22d3ee' },
        { token: 'variable', foreground: 'f9fafb' }
      ],
      colors: {
        'editor.background': '#1f2937',
        'editor.foreground': '#f9fafb',
        'editor.lineHighlightBackground': '#374151',
        'editor.selectionBackground': '#4c1d95',
        'editor.inactiveSelectionBackground': '#374151',
        'editorCursor.foreground': '#a78bfa',
        'editorWhitespace.foreground': '#4b5563'
      }
    });
  };

  // 注册快捷键
  const registerKeyBindings = (editor, monaco) => {
    // Ctrl+S 保存
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSaveFile();
    });

    // Ctrl+Shift+P 命令面板
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyP, () => {
      editor.trigger('', 'editor.action.quickCommand');
    });

    // F12 跳转到定义
    editor.addCommand(monaco.KeyCode.F12, () => {
      editor.trigger('', 'editor.action.revealDefinition');
    });

    // Shift+F12 查找所有引用
    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.F12, () => {
      editor.trigger('', 'editor.action.goToReferences');
    });

    // Ctrl+Shift+F 格式化文档
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF, () => {
      editor.trigger('', 'editor.action.formatDocument');
    });
  };

  // 初始化 LSP
  const initializeLSP = (editor, monaco) => {
    // 模拟 LSP 连接
    setLspState(prev => ({
      ...prev,
      isConnected: true,
      serverStatus: 'connected'
    }));

    // 注册诊断信息提供者
    const diagnosticsProvider = monaco.languages.registerCodeActionProvider('javascript', {
      provideCodeActions: (model, range, context) => {
        const diagnostics = context.markers.map(marker => ({
          title: `修复: ${marker.message}`,
          kind: 'quickfix',
          edit: {
            edits: [{
              resource: model.uri,
              edit: {
                range: marker,
                text: '// 已修复'
              }
            }]
          }
        }));
        return { actions: diagnostics, dispose: () => {} };
      }
    });

    // 注册悬停信息提供者
    const hoverProvider = monaco.languages.registerHoverProvider('javascript', {
      provideHover: (model, position) => {
        const word = model.getWordAtPosition(position);
        if (word) {
          return {
            range: new monaco.Range(position.lineNumber, word.startColumn, position.lineNumber, word.endColumn),
            contents: [
              { value: `**${word.word}**` },
              { value: `类型: ${getTypeInfo(word.word)}` },
              { value: `描述: ${getDescription(word.word)}` }
            ]
          };
        }
        return null;
      }
    });

    // 注册自动补全提供者
    const completionProvider = monaco.languages.registerCompletionItemProvider('javascript', {
      provideCompletionItems: (model, position) => {
        const suggestions = [
          {
            label: 'useState',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'useState(${1:initialValue})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for state management'
          },
          {
            label: 'useEffect',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'useEffect(() => {\n\t${1:// effect}\n}, [${2:dependencies}])',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'React Hook for side effects'
          },
          {
            label: 'console.log',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'console.log(${1:value})',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Log output to console'
          },
          {
            label: 'function',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'function ${1:functionName}(${2:parameters}) {\n\t${3:// function body}\n}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Function declaration'
          }
        ];
        return { suggestions };
      }
    });

    // 存储提供者引用以便清理
    setLspState(prev => ({
      ...prev,
      providers: [diagnosticsProvider, hoverProvider, completionProvider]
    }));
  };

  // 设置编辑器事件
  const setupEditorEvents = (editor, monaco) => {
    // 内容变化事件
    editor.onDidChangeModelContent(() => {
      const content = editor.getValue();
      setEditorState(prev => ({
        ...prev,
        content,
        modified: true
      }));
      
      // 更新当前文件
      setFileManager(prev => ({
        ...prev,
        openFiles: prev.openFiles.map((file, index) => 
          index === prev.activeFileIndex 
            ? { ...file, content, modified: true }
            : file
        )
      }));

      // 模拟实时诊断
      setTimeout(() => {
        const model = editor.getModel();
        const diagnostics = performDiagnostics(content);
        monaco.editor.setModelMarkers(model, 'javascript', diagnostics);
        setLspState(prev => ({ ...prev, diagnostics }));
      }, 500);
    });

    // 光标位置变化事件
    editor.onDidChangeCursorPosition((e) => {
      setEditorState(prev => ({
        ...prev,
        cursorPosition: { line: e.position.lineNumber, column: e.position.column }
      }));
    });

    // 选择变化事件
    editor.onDidChangeCursorSelection((e) => {
      setEditorState(prev => ({
        ...prev,
        selections: [e.selection]
      }));
    });
  };

  // 辅助函数
  const getTypeInfo = (word) => {
    const typeMap = {
      'useState': 'React Hook',
      'useEffect': 'React Hook',
      'console': 'Global Object',
      'function': 'Keyword',
      'const': 'Keyword',
      'let': 'Keyword',
      'var': 'Keyword'
    };
    return typeMap[word] || 'Variable';
  };

  const getDescription = (word) => {
    const descMap = {
      'useState': '用于在函数组件中添加状态',
      'useEffect': '用于处理副作用',
      'console': '浏览器控制台对象',
      'function': '函数声明关键字'
    };
    return descMap[word] || '用户定义的标识符';
  };

  const performDiagnostics = (content) => {
    const diagnostics = [];
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      // 检查未使用的变量
      if (line.includes('const ') && !content.includes(line.split('const ')[1]?.split(' ')[0])) {
        diagnostics.push({
          startLineNumber: index + 1,
          startColumn: 1,
          endLineNumber: index + 1,
          endColumn: line.length + 1,
          message: '未使用的变量',
          severity: monaco.languages.MarkerSeverity.Warning
        });
      }
      
      // 检查缺少分号
      if (line.trim() && !line.trim().endsWith(';') && !line.trim().endsWith('{') && !line.trim().endsWith('}')) {
        diagnostics.push({
          startLineNumber: index + 1,
          startColumn: line.length,
          endLineNumber: index + 1,
          endColumn: line.length + 1,
          message: '缺少分号',
          severity: monaco.languages.MarkerSeverity.Info
        });
      }
    });
    
    return diagnostics;
  };

  // 文件操作函数
  const handleSaveFile = useCallback(() => {
    const currentFile = fileManager.openFiles[fileManager.activeFileIndex];
    console.log(`保存文件: ${currentFile.name}`);
    
    setFileManager(prev => ({
      ...prev,
      openFiles: prev.openFiles.map((file, index) => 
        index === prev.activeFileIndex 
          ? { ...file, modified: false }
          : file
      )
    }));
    
    setEditorState(prev => ({ ...prev, modified: false }));
  }, [fileManager.activeFileIndex, fileManager.openFiles]);

  const handleRunCode = useCallback(() => {
    const content = editorRef.current?.getValue();
    console.log('运行代码:', content);
    // 这里可以集成代码执行功能
  }, []);

  const handleFormatCode = useCallback(() => {
    if (editorRef.current) {
      editorRef.current.trigger('', 'editor.action.formatDocument');
    }
  }, []);

  const switchFile = useCallback((index) => {
    const file = fileManager.openFiles[index];
    setFileManager(prev => ({ ...prev, activeFileIndex: index }));
    setEditorState(prev => ({
      ...prev,
      content: file.content,
      language: file.language,
      fileName: file.name,
      modified: file.modified
    }));
    
    if (editorRef.current && monacoRef.current) {
      const model = monacoRef.current.editor.createModel(file.content, file.language);
      editorRef.current.setModel(model);
    }
  }, [fileManager.openFiles]);

  const toggleTheme = useCallback(() => {
    const newTheme = editorState.theme === 'powerautomation-light' ? 'powerautomation-dark' : 'powerautomation-light';
    setEditorState(prev => ({ ...prev, theme: newTheme }));
    if (monacoRef.current) {
      monacoRef.current.editor.setTheme(newTheme);
    }
  }, [editorState.theme]);

  if (!isVisible) return null;

  return (
    <div className="monaco-editor-modal">
      <div className="monaco-editor-container">
        {/* 编辑器头部 */}
        <div className="monaco-header">
          <div className="header-left">
            <h3>📝 Monaco Editor with LSP</h3>
            <div className="lsp-status">
              <span className={`lsp-indicator ${lspState.isConnected ? 'connected' : 'disconnected'}`}></span>
              <span>LSP: {lspState.serverStatus}</span>
            </div>
          </div>
          <div className="header-right">
            <div className="editor-stats">
              <span>行: {editorState.cursorPosition.line}</span>
              <span>列: {editorState.cursorPosition.column}</span>
              <span>语言: {editorState.language}</span>
            </div>
            <button className="theme-toggle-btn" onClick={toggleTheme}>
              {editorState.theme === 'powerautomation-light' ? '🌙' : '☀️'}
            </button>
            <button className="close-btn" onClick={onClose}>✖️</button>
          </div>
        </div>

        {/* 文件标签栏 */}
        <div className="file-tabs">
          {fileManager.openFiles.map((file, index) => (
            <div 
              key={index}
              className={`file-tab ${index === fileManager.activeFileIndex ? 'active' : ''} ${file.modified ? 'modified' : ''}`}
              onClick={() => switchFile(index)}
            >
              <span className="file-icon">
                {file.language === 'javascript' && '📄'}
                {file.language === 'css' && '🎨'}
                {file.language === 'json' && '⚙️'}
              </span>
              <span className="file-name">{file.name}</span>
              {file.modified && <span className="modified-indicator">●</span>}
            </div>
          ))}
        </div>

        {/* 编辑器主体 */}
        <div className="monaco-body">
          <div className="editor-area">
            <Editor
              height="100%"
              language={editorState.language}
              theme={editorState.theme}
              value={editorState.content}
              options={editorOptions}
              onMount={handleEditorDidMount}
            />
          </div>
          
          {/* 侧边面板 */}
          <div className="side-panel">
            {/* 诊断信息 */}
            <div className="panel-section">
              <h4>🔍 诊断信息</h4>
              <div className="diagnostics-list">
                {lspState.diagnostics.length === 0 ? (
                  <div className="no-issues">无问题</div>
                ) : (
                  lspState.diagnostics.map((diagnostic, index) => (
                    <div key={index} className={`diagnostic-item ${diagnostic.severity === 8 ? 'error' : diagnostic.severity === 4 ? 'warning' : 'info'}`}>
                      <span className="diagnostic-line">行 {diagnostic.startLineNumber}</span>
                      <span className="diagnostic-message">{diagnostic.message}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* 大纲视图 */}
            <div className="panel-section">
              <h4>📋 大纲</h4>
              <div className="outline-list">
                <div className="outline-item">
                  <span className="outline-icon">🔧</span>
                  <span>ExampleComponent</span>
                </div>
                <div className="outline-item">
                  <span className="outline-icon">⚡</span>
                  <span>handleDataFetch</span>
                </div>
                <div className="outline-item">
                  <span className="outline-icon">📦</span>
                  <span>useState</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 编辑器底部 */}
        <div className="monaco-footer">
          <div className="footer-left">
            <div className="editor-info">
              <span>文件: {editorState.fileName}</span>
              <span>大小: {editorState.content.length} 字符</span>
              <span>行数: {editorState.content.split('\n').length}</span>
              {editorState.modified && <span className="modified-status">● 已修改</span>}
            </div>
          </div>
          <div className="footer-right">
            <button className="footer-btn" onClick={handleSaveFile}>
              💾 保存 (Ctrl+S)
            </button>
            <button className="footer-btn" onClick={handleRunCode}>
              ▶️ 运行
            </button>
            <button className="footer-btn" onClick={handleFormatCode}>
              🔧 格式化 (Ctrl+Shift+F)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonacoEditorComponent;

