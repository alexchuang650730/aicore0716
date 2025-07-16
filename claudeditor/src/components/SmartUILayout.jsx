import React, { useState, useEffect } from 'react';
import './SmartUILayout.css';

// 基于 CodeFlow 分析和三大系统指导书的 SmartUI 三栏布局组件
const SmartUILayout = () => {
  // 系统状态数据 - 基于三大核心系统
  const [systemStatus, setSystemStatus] = useState({
    mcpCoordinator: { status: '运行中', color: 'blue', components: 24 },
    feishuIntegration: { status: '已连接', color: 'green', notifications: 24, groups: 3 },
    githubSync: { status: '同步中', color: 'yellow', branch: 'v0.6', lastSync: '2分钟前' }
  });

  // 六大工作流状态 - 基于 CodeFlow 分析结果
  const [sixWorkflows, setSixWorkflows] = useState([
    {
      id: 'code_generation',
      name: '代码生成工作流',
      icon: '💻',
      status: '运行中',
      color: 'blue',
      progress: 100,
      quality: 92,
      components: ['codeflow', 'zen', 'mirror_code', 'test']
    },
    {
      id: 'ui_design',
      name: 'UI设计工作流',
      icon: '🎨',
      status: '运行中',
      color: 'purple',
      progress: 85,
      quality: 95,
      components: ['smartui', 'ag-ui', 'stagewise', 'codeflow']
    },
    {
      id: 'api_development',
      name: 'API开发工作流',
      icon: '🔗',
      status: '待执行',
      color: 'orange',
      progress: 15,
      quality: 0,
      components: ['codeflow', 'test', 'security', 'release_trigger']
    },
    {
      id: 'database_design',
      name: '数据库设计工作流',
      icon: '🗄️',
      status: '规划中',
      color: 'green',
      progress: 30,
      quality: 88,
      components: ['deepgraph', 'codeflow', 'test']
    },
    {
      id: 'test_automation',
      name: '测试自动化工作流',
      icon: '🧪',
      status: '运行中',
      color: 'cyan',
      progress: 78,
      quality: 94,
      components: ['test', 'ag-ui', 'stagewise', 'intelligent_monitoring']
    },
    {
      id: 'deployment_pipeline',
      name: '部署流水线工作流',
      icon: '🚀',
      status: '监控中',
      color: 'red',
      progress: 92,
      quality: 97,
      components: ['release_trigger', 'zen', 'intelligent_monitoring', 'operations']
    }
  ]);

  // AI对话历史
  const [chatHistory, setChatHistory] = useState([
    {
      type: 'ai',
      message: '✅ 完全理解！右侧面板已经集成了六大工作流Dashboard，实时显示代码生成、UI设计、API开发、数据库设计、测试自动化、部署流水线的状态。',
      timestamp: new Date()
    },
    {
      type: 'user',
      message: '很好！我需要实时看到所有工作流的状态，特别是六大工作流节点的进度和质量指标。',
      timestamp: new Date()
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');

  // 当前任务状态
  const [currentTask, setCurrentTask] = useState({
    title: '正在创建智慧UI Dashboard...',
    progress: 75,
    tasks: [
      { name: '查看GitHub最新状态', status: '立即查看', action: 'github' },
      { name: '测试飞书通知功能', status: '发送测试', action: 'feishu' },
      { name: '检查MCP协调器状态', status: '系统检查', action: 'mcp' }
    ]
  });

  // 发送消息
  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      setChatHistory(prev => [...prev, {
        type: 'user',
        message: inputMessage,
        timestamp: new Date()
      }]);
      setInputMessage('');
      
      // 模拟AI回复
      setTimeout(() => {
        setChatHistory(prev => [...prev, {
          type: 'ai',
          message: '我理解您的需求，正在分析工作流状态并提供智能建议...',
          timestamp: new Date()
        }]);
      }, 1000);
    }
  };

  return (
    <div className="smartui-layout">
      {/* 顶部导航栏 */}
      <header className="smartui-header">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">🌐</span>
            <span className="logo-text">PowerAutomation AI</span>
          </div>
          <div className="subtitle">智慧UI助手 - 在线 | MCP协调中</div>
        </div>
        <div className="header-right">
          <button className="header-btn">Manus</button>
          <button className="header-btn">应用</button>
          <button className="header-btn">飞书</button>
        </div>
      </header>

      {/* 主要内容区域 */}
      <main className="smartui-main">
        {/* 左侧系统状态监控面板 - 第三核心系统：运维监控区 */}
        <aside className="left-panel">
          <div className="panel-section">
            <h3 className="panel-title">
              <span className="status-dot green"></span>
              系统状态监控
            </h3>
          </div>

          {/* MCP协调器状态 */}
          <div className="status-card blue">
            <div className="card-header">
              <span className="status-dot blue"></span>
              <span className="card-title">MCP协调器</span>
              <span className="card-status">{systemStatus.mcpCoordinator.status}</span>
            </div>
            <div className="card-content">
              <p>统一工作流协调 | 智能介入管理</p>
              <ul className="status-list">
                <li>• Owen BB本地模型: 活跃</li>
                <li>• RL-SRT学习引擎: 运行</li>
                <li>• 开发介入检测: 启用</li>
                <li>• 架构合规检查: 实时</li>
              </ul>
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-value">{systemStatus.mcpCoordinator.components}</div>
                  <div className="stat-label">MCP组件</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">70.8%</div>
                  <div className="stat-label">集成度</div>
                </div>
              </div>
            </div>
          </div>

          {/* 飞书集成状态 */}
          <div className="status-card green">
            <div className="card-header">
              <span className="status-dot green"></span>
              <span className="card-title">飞书集成</span>
              <span className="card-status">{systemStatus.feishuIntegration.status}</span>
            </div>
            <div className="card-content">
              <p>实时通知 | 团队协作 | 移动端同步</p>
              <div className="stats-grid">
                <div className="stat-item">
                  <div className="stat-value">{systemStatus.feishuIntegration.notifications}</div>
                  <div className="stat-label">今日通知</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{systemStatus.feishuIntegration.groups}</div>
                  <div className="stat-label">活跃群组</div>
                </div>
              </div>
            </div>
          </div>

          {/* GitHub同步状态 */}
          <div className="status-card yellow">
            <div className="card-header">
              <span className="status-dot yellow"></span>
              <span className="card-title">GitHub同步</span>
              <span className="card-status">{systemStatus.githubSync.status}</span>
            </div>
            <div className="card-content">
              <p>powerauto_ai_0.53 | {systemStatus.githubSync.branch}分支</p>
              <ul className="status-list">
                <li>• Webhook: 正常监听</li>
                <li>• 自动部署: 启用</li>
                <li>• 代码质量检查: 通过</li>
              </ul>
              <div className="sync-info">最后同步: {systemStatus.githubSync.lastSync}</div>
            </div>
          </div>
        </aside>

        {/* 中间主工作区域 - 第一核心系统：ClaudeEditor 编辑/演示区 */}
        <section className="center-panel">
          {/* 任务进度区域 */}
          <div className="task-progress">
            <div className="progress-header">
              <span className="progress-icon">⚡</span>
              <span className="progress-title">{currentTask.title}</span>
              <span className="progress-percentage">{currentTask.progress}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${currentTask.progress}%` }}
              ></div>
            </div>
          </div>

          {/* 任务卡片区域 */}
          <div className="task-cards">
            {currentTask.tasks.map((task, index) => (
              <div key={index} className="task-card">
                <div className="task-info">
                  <span className="task-name">{task.name}</span>
                </div>
                <button className="task-action">{task.status}</button>
              </div>
            ))}
          </div>

          {/* AI对话区域 - 第二核心系统：AI助手对话区 */}
          <div className="ai-chat-section">
            <div className="chat-header">
              <h4>🤖 AI助手对话区</h4>
              <span className="chat-status">智能协作中</span>
            </div>
            
            <div className="chat-messages">
              {chatHistory.map((msg, index) => (
                <div key={index} className={`message ${msg.type}-message`}>
                  <div className="message-avatar">
                    {msg.type === 'ai' ? 'AI' : 'U'}
                  </div>
                  <div className="message-bubble">
                    {msg.type === 'ai' && msg.message.startsWith('✅') && (
                      <span className="ai-check">✅ 完全理解！</span>
                    )}
                    <p>{msg.message.replace('✅ 完全理解！', '')}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* 输入区域 */}
            <div className="chat-input-area">
              <div className="input-container">
                <input 
                  type="text" 
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="描述您的开发需求，AI将智能介入协助..."
                  className="chat-input"
                />
                <div className="input-actions">
                  <button className="action-btn">Manus</button>
                  <button className="action-btn">应用</button>
                  <button className="action-btn">飞书</button>
                  <button className="send-btn" onClick={handleSendMessage}>📤</button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 右侧六大工作流Dashboard */}
        <aside className="right-panel">
          <div className="panel-section">
            <h3 className="panel-title">六大工作流Dashboard</h3>
          </div>

          {/* 快捷操作按钮 */}
          <div className="quick-actions">
            <button className="quick-btn blue" title="代码生成">
              <span className="btn-icon">💻</span>
            </button>
            <button className="quick-btn purple" title="UI设计">
              <span className="btn-icon">🎨</span>
            </button>
            <button className="quick-btn orange" title="API开发">
              <span className="btn-icon">🔗</span>
            </button>
          </div>

          {/* 六大工作流卡片 */}
          {sixWorkflows.map((workflow, index) => (
            <div key={workflow.id} className={`workflow-card ${workflow.color}`}>
              <div className="workflow-header">
                <span className="workflow-icon">{workflow.icon}</span>
                <span className="workflow-title">{workflow.name}</span>
                <span className="workflow-status">{workflow.status}</span>
              </div>
              <div className="workflow-stats">
                <div className="stat-row">
                  <span className="stat-label">进度</span>
                  <span className="stat-value">{workflow.progress}%</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">质量</span>
                  <span className="stat-value">{workflow.quality}</span>
                </div>
                <div className="workflow-components">
                  <span className="components-label">组件:</span>
                  <div className="components-list">
                    {workflow.components.map((comp, i) => (
                      <span key={i} className="component-tag">{comp}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </aside>
      </main>
    </div>
  );
};

export default SmartUILayout;

