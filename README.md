# PowerAutomation v4.6.9.5

🚀 **AI-Powered Code Editor with K2 Dual Provider & Mirror Code Intelligence**

## Quick Start

```bash
# Clone repository
git clone https://github.com/alexchuang650730/aicore0711.git
cd aicore0711

# Start PowerAutomation ecosystem
./claude "Hello K2!"

# Or start ClaudeEditor directly
cd claudeditor && npm start
```

## Features

- 🤖 **K2 Dual Provider** - Smart routing between Infini-AI Cloud and Moonshot Official
- 🪞 **Mirror Code** - Intelligent routing between K2 and Claude Code
- 📡 **Command MCP** - Unified command interface with 19+ supported commands
- 🔄 **Task Sync** - Real-time synchronization between ClaudeEditor and Claude Code
- 📱 **Responsive Design** - Works on desktop, mobile, and web

## Documentation

📚 All documentation is in [`docs/`](./docs/) directory:
- [Installation Guide](./docs/README_STARTUP.md)
- [Release Notes](./docs/RELEASE_NOTES_v4.6.9.5.md)
- [Architecture](./docs/PROJECT_ARCHITECTURE.md)

## Testing

🧪 All tests and scripts are in [`tests/`](./tests/) directory:
- Run tests: `cd tests && python run_tests.py`
- Integration tests: `python test_mirror_code_fix.py`
- HITL tests: `python test_hitl_completeness.py`

## Deployment

🚀 Deployment configurations in [`deployment/`](./deployment/) directory:
- npm ecosystem: `deployment/npm-ecosystem/`
- Install via npm: `npm install -g @powerautomation/claudeeditor`
- Install via curl: `curl -fsSL https://install.powerautomation.ai | bash`

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

**PowerAutomation Team** | [Website](https://powerautomation.ai) | [GitHub](https://github.com/alexchuang650730/aicore0711)
