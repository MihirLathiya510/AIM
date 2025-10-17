# AIM (AI Agent Manager) - MCP Server

**Meta Control Plane server for orchestrating multi-agent AI tasks with iterative refinement, constraint enforcement, and validation.**

AIM is a Model Context Protocol (MCP) server that acts as a sophisticated task orchestrator for AI agents. It breaks down complex tasks, assigns them to specialized agents, enforces constraints, and iteratively refines outputs until they perfectly match user requirements.

## Features

- 🎯 **Intelligent Task Decomposition** - Automatically breaks complex tasks into manageable subtasks
- 🤖 **Multi-Agent Orchestration** - Routes subtasks to specialized agents (coding, testing, documentation, review)
- 🔄 **Iterative Refinement Loop** - Keeps refining outputs until all constraints are met
- ✅ **Constraint Enforcement** - Parses and validates requirements, output formats, and quality standards
- 📝 **Audit Trail** - Complete logging of all decisions, iterations, and validations
- 🔌 **Plug-and-Play** - Works with Claude Desktop, Claude Code, and any MCP-compatible client
- 🛡️ **Hallucination Mitigation** - Review agents validate outputs for accuracy and completeness

## Architecture

```
User Request → AIM Server → Task Decomposition → Agent Assignment → Execution → Review → Iteration → Final Output
```

**Core Components:**
- **Task Manager**: Decomposes tasks and tracks execution state
- **Agent Registry**: Manages specialized AI agents (Claude, GPT, etc.)
- **Refinement Loop**: Iteratively improves outputs until perfect
- **Review System**: Validates against constraints and provides feedback
- **Storage**: Persists tasks, state, and audit logs

## Installation

### Prerequisites

- Python 3.10 or higher
- Anthropic API key (for Claude agents)

### From Source

```bash
# Clone the repository
git clone https://github.com/aim-mcp/aim-mcp-server.git
cd aim-mcp-server

# Install in development mode
pip install -e .

# Or install dependencies manually
pip install mcp anthropic pydantic python-dateutil pyyaml
```

### From PyPI (when published)

```bash
pip install aim-mcp-server
```

## Configuration

### 1. Set API Key

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 2. Connect to Claude Desktop

#### Option A: Using Claude CLI

```bash
# Add AIM to Claude Desktop
claude mcp add --transport stdio aim -- python -m aim_mcp_server

# Verify installation
claude mcp list
```

#### Option B: Manual Configuration

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aim": {
      "command": "python",
      "args": ["-m", "aim_mcp_server"],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

After adding the configuration, restart Claude Desktop to load the AIM server.

## Usage

Once installed, you can use AIM tools directly from Claude Desktop:

### Example 1: Simple Task

```
You: Create a Python function to calculate fibonacci numbers with unit tests and documentation.

[AIM automatically decomposes into subtasks, assigns to agents, and iterates until perfect]
```

### Example 2: Complex Task with Constraints

```
You: Refactor the authentication module to use Auth3 SDK, add comprehensive unit 
tests with >90% coverage, enforce TypeScript strict mode + FIDO2 compliance, 
and generate API documentation.

[AIM parses constraints, validates each one, and won't finish until all are met]
```

### Example 3: Using AIM Tools Directly

```
You: Use create_task tool with:
{
  "description": "Implement a REST API for user management with JWT auth, 
  PostgreSQL storage, and OpenAPI docs",
  "context": {
    "framework": "FastAPI",
    "database": "PostgreSQL"
  }
}
```

## Available Tools

AIM exposes the following tools via MCP:

### `create_task`
Create a new orchestrated task with automatic decomposition.

**Input:**
- `description` (required): Detailed task description with constraints
- `context` (optional): Additional context dictionary
- `deadline` (optional): ISO format deadline

**Output:** Task ID, decomposition plan, and subtasks

### `execute_task`
Execute a task with iterative refinement until all constraints are met.

**Input:**
- `task_id` (required): The task ID to execute

**Output:** Final validated output with execution details

### `get_task_status`
Monitor task execution progress.

**Input:**
- `task_id` (required): The task ID

**Output:** Current status, subtask statuses, and progress

### `get_task_output`
Retrieve task results.

**Input:**
- `task_id` (required): The task ID

**Output:** Final output or current iteration results

### `review_and_iterate`
Manually trigger additional refinement with feedback.

**Input:**
- `task_id` (required): The task ID
- `feedback` (required): User feedback for refinement

**Output:** Refined output after additional iterations

### `list_tasks`
List all tasks with optional filtering.

**Input:**
- `status` (optional): Filter by status (pending/in_progress/completed/failed/cancelled)
- `limit` (optional): Maximum tasks to return (default: 100)

**Output:** List of task summaries

## How It Works

### 1. Task Decomposition

When you submit a task, AIM:
- Parses the description for constraints (test coverage, frameworks, languages, compliance, etc.)
- Breaks it into logical subtasks
- Identifies dependencies between subtasks
- Assigns each subtask to the appropriate agent type

### 2. Execution with Refinement

For each subtask:
- The assigned agent executes the task
- A review agent validates the output against constraints
- If validation fails, specific feedback is generated
- The task is retried with feedback (up to 10 iterations)
- Process continues until output is perfect or max iterations reached

### 3. Validation & Review

The review system:
- Checks constraint compliance (test coverage, language requirements, etc.)
- Uses LLM-based semantic review for quality
- Detects hallucinations and errors
- Generates actionable feedback
- Scores output quality (0.0 to 1.0)

### 4. Audit Trail

Everything is logged:
- Task creation and decomposition
- Subtask assignments
- Each iteration attempt
- Validation results and feedback
- Final outputs and scores

Logs are stored in `~/.aim/logs/` and accessible via MCP resources.

## Storage

AIM stores tasks and state in:
- **Tasks**: `~/.aim/tasks/` (JSON files)
- **Logs**: `~/.aim/logs/` (JSONL audit trail)

These directories are created automatically on first run.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=aim_mcp_server tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## Extending AIM

### Adding New Agent Types

```python
from aim_mcp_server.agents.base import Agent, AgentType, AgentCapability

class MyCustomAgent(Agent):
    def __init__(self):
        super().__init__(
            agent_type=AgentType.CUSTOM,
            capabilities=[AgentCapability.CODE_GENERATION]
        )
    
    async def execute(self, task):
        # Your implementation
        pass
```

Register with the agent registry:

```python
from aim_mcp_server.agents.registry import AgentRegistry

registry = AgentRegistry()
registry.register_agent(AgentType.CUSTOM, MyCustomAgent())
```

### Adding New Constraint Types

Edit `src/aim_mcp_server/utils/constraints.py` to add new patterns and validation logic.

## Roadmap

- [ ] Support for more LLM providers (OpenAI, local models)
- [ ] Database backend options (SQLite, PostgreSQL)
- [ ] Web dashboard for monitoring
- [ ] GitHub integration for automated PRs
- [ ] CI/CD pipeline integration
- [ ] Custom agent plugins
- [ ] Team collaboration features
- [ ] Cost tracking and optimization

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 [Documentation](https://github.com/aim-mcp/aim-mcp-server#readme)
- 🐛 [Issue Tracker](https://github.com/aim-mcp/aim-mcp-server/issues)
- 💬 [Discussions](https://github.com/aim-mcp/aim-mcp-server/discussions)

## Acknowledgments

Built on:
- [Model Context Protocol](https://modelcontextprotocol.io) by Anthropic
- [Claude API](https://anthropic.com/claude)
- Python ecosystem (Pydantic, asyncio, etc.)

---

**Made with ❤️ by the AIM team**

