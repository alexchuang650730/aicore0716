import React, { useEffect, useState } from 'react';
import './App.css';
import './styles/SmartUI.css';
import FileExplorer from './components/FileExplorer';
import TaskList from './components/TaskList';
import AIAssistant from './ai-assistant/AIAssistant';
import ToolManager from './components/ToolManager';
import MonacoEditor from './editor/MonacoEditor';
import PowerAutomationService from './services/PowerAutomationService';
import SmartUIService from './services/SmartUIService';

function App() {
  const [currentFile, setCurrentFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [selectedTask, setSelectedTask] = useState(null);
  const [activeLeftPanel, setActiveLeftPanel] = useState('tasks');
  const [powerAutomationStatus, setPowerAutomationStatus] = useState('initializing');
  const [smartUIConfig, setSmartUIConfig] = useState(null);
  const [deviceType, setDeviceType] = useState('desktop');

  // SmartUI 初始化
  useEffect(() => {
    const initializeSmartUI = async () => {
      try {
        console.log('🎨 初始化 SmartUI 系统...');
        
        // SmartUI 服务会自动初始化
        const unsubscribe = window.smartUIService?.subscribe((event, data) => {
          if (event === 'config_applied') {
            setSmartUIConfig(data);
            setDeviceType(data.device_type);
            console.log('📱 SmartUI 配置已应用:', data);
          } else if (event === 'device_change') {
            console.log('📱 设备类型变化:', data);
            setDeviceType(data.newDeviceType);
          }
        });
        
        // 获取初始配置
        if (window.smartUIService?.isInitialized) {
          const config = window.smartUIService.getCurrentConfig();
          if (config) {
            setSmartUIConfig(config);
            setDeviceType(config.device_type);
          }
        }
        
        return unsubscribe;
        
      } catch (error) {
        console.error('❌ SmartUI 初始化失败:', error);
      }
    };

    const cleanup = initializeSmartUI();
    
    return () => {
      if (cleanup && typeof cleanup === 'function') {
        cleanup();
      }
    };
  }, []);

  // PowerAutomation 服务初始化
  useEffect(() => {
    const initializePowerAutomation = async () => {
      try {
        console.log('🚀 ClaudeEditor 启动，初始化 PowerAutomation...');
        
        // 启动 PowerAutomation 服务
        await PowerAutomationService.initialize();
        
        setPowerAutomationStatus('ready');
        console.log('✅ PowerAutomation 服务已就绪');
        
      } catch (error) {
        console.error('❌ PowerAutomation 初始化失败:', error);
        setPowerAutomationStatus('error');
      }
    };

    initializePowerAutomation();

    // 监听 PowerAutomation 就绪事件
    const handlePowerAutomationReady = (event) => {
      console.log('🎉 PowerAutomation 就绪事件:', event.detail);
      setPowerAutomationStatus('ready');
    };

    window.addEventListener('powerautomation:ready', handlePowerAutomationReady);

    return () => {
      window.removeEventListener('powerautomation:ready', handlePowerAutomationReady);
    };
  }, []);

  const handleFileSelect = (file, content) => {
    setCurrentFile(file);
    setFileContent(content);
  };

  const handleFileContentChange = (newContent) => {
    setFileContent(newContent);
  };

  const handleProjectOpen = (projectPath) => {
    console.log('Opening project:', projectPath);
  };

  const handleTaskSelect = (task) => {
    setSelectedTask(task);
    console.log('Selected task:', task);
    
    if (task && task.type) {
      switch (task.type) {
        case 'open_file':
          console.log('Opening file from task:', task.filePath);
          break;
        case 'edit_code':
          console.log('Edit code request:', task.changes);
          break;
        case 'show_diff':
          console.log('Show diff request:', task.before, task.after);
          break;
        default:
          break;
      }
    }
  };

  const handleAgentAssign = (taskId, agentId) => {
    console.log('Agent assigned:', { taskId, agentId });
  };

  // 根据设备类型决定是否显示侧边栏
  const shouldShowSidebar = () => {
    return window.smartUIService?.shouldShowSidebar() !== false;
  };

  // 根据设备类型决定布局
  const getLayoutClass = () => {
    if (!smartUIConfig) return '';
    return `columns-${smartUIConfig.layout_columns}`;
  };

  return (
    <div className={`app ${getLayoutClass()}`}>
      <header className="app-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1>ClaudeEditor</h1>
            <p>
              AI-Powered Code Editor with SmartUI v4.6.9.6
              {smartUIConfig && (
                <span style={{ marginLeft: '10px', opacity: 0.7 }}>
                  📱 {deviceType} | {smartUIConfig.breakpoint}
                </span>
              )}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => setActiveLeftPanel('tasks')}
              className={`btn ${activeLeftPanel === 'tasks' ? 'btn-primary' : 'btn-secondary'}`}
            >
              🎯 任务管理
            </button>
            {/* 在移动端隐藏文件浏览按钮 */}
            {deviceType !== 'mobile' && (
              <button
                onClick={() => setActiveLeftPanel('files')}
                className={`btn ${activeLeftPanel === 'files' ? 'btn-primary' : 'btn-secondary'}`}
              >
                📁 文件浏览
              </button>
            )}
          </div>
        </div>
      </header>
      
      <div className="app-content">
        {/* File Explorer Section - 在移动端和平板隐藏 */}
        {activeLeftPanel === 'files' && deviceType !== 'mobile' && deviceType !== 'tablet' && (
          <div className="file-explorer-section">
            <FileExplorer 
              onFileSelect={handleFileSelect}
              onProjectOpen={handleProjectOpen}
            />
          </div>
        )}
        
        {/* Task List Section - 在移动端显示为全宽 */}
        {activeLeftPanel === 'tasks' && (
          <div className="file-explorer-section">
            <TaskList 
              onTaskSelect={handleTaskSelect}
              onAgentAssign={handleAgentAssign}
            />
          </div>
        )}
        
        {/* Main Editor Area */}
        <div className="editor-section">
          {/* Task Info Bar */}
          {selectedTask && (
            <div style={{
              padding: '8px 15px',
              backgroundColor: '#e3f2fd',
              borderBottom: '1px solid #e9ecef',
              fontSize: '12px',
              color: '#1976d2'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>
                  🎯 当前任务: <strong>{selectedTask.title}</strong>
                  {selectedTask.assignedAgent && (
                    <span style={{ marginLeft: '10px', opacity: 0.8 }}>
                      分配给: {selectedTask.assignedAgent}
                    </span>
                  )}
                </span>
                <button
                  onClick={() => setSelectedTask(null)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#1976d2',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  ✕
                </button>
              </div>
              {selectedTask.description && (
                <div style={{ marginTop: '4px', opacity: 0.8 }}>
                  {selectedTask.description}
                </div>
              )}
            </div>
          )}
          
          {/* Monaco Editor */}
          <div style={{ flex: 1, height: '100%' }}>
            <MonacoEditor 
              currentFile={currentFile}
              fileContent={fileContent}
              onFileContentChange={handleFileContentChange}
              selectedTask={selectedTask}
            />
          </div>
        </div>
        
        {/* Right Sidebar - 根据设备类型显示/隐藏 */}
        {shouldShowSidebar() && (
          <div className="sidebar">
            <div style={{ flex: 1 }}>
              <AIAssistant selectedTask={selectedTask} />
            </div>
            <div style={{ 
              borderTop: '1px solid #e9ecef',
              maxHeight: deviceType === 'mobile' ? '150px' : '200px',
              overflowY: 'auto'
            }}>
              <ToolManager />
            </div>
          </div>
        )}
      </div>
      
      {/* 移动端底部导航 */}
      {deviceType === 'mobile' && (
        <div style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          height: '60px',
          backgroundColor: 'white',
          borderTop: '1px solid #e9ecef',
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
          zIndex: 100
        }}>
          <button
            onClick={() => setActiveLeftPanel('tasks')}
            className={`btn ${activeLeftPanel === 'tasks' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '12px', padding: '8px 12px' }}
          >
            🎯 任务
          </button>
          <button
            onClick={() => setActiveLeftPanel('files')}
            className={`btn ${activeLeftPanel === 'files' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '12px', padding: '8px 12px' }}
          >
            📁 文件
          </button>
          <button
            className="btn btn-secondary"
            style={{ fontSize: '12px', padding: '8px 12px' }}
          >
            🤖 AI
          </button>
          <button
            className="btn btn-secondary"
            style={{ fontSize: '12px', padding: '8px 12px' }}
          >
            🛠️ 工具
          </button>
        </div>
      )}
    </div>
  );
}

export default App;

