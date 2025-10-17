# AIM Quick Start Guide

Get started with AIM (AI Agent Manager) in 5 minutes!

## Prerequisites

- Python 3.10+
- Anthropic API key (get one at https://console.anthropic.com/)
- Claude Desktop (download at https://claude.ai/download)

## Step 1: Install AIM

```bash
cd /Users/mihir/work25/AIM
pip install -e .
```

## Step 2: Set Your API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Step 3: Configure Claude Desktop

### Option A: Automatic (Recommended)

```bash
python -m aim_mcp_server.configure
```

### Option B: Manual

1. Find your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add this configuration:

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

## Step 4: Restart Claude Desktop

Close and reopen Claude Desktop to load the AIM server.

## Step 5: Test It!

In Claude Desktop, try:

```
Can you list the available MCP tools?
```

You should see AIM tools like `create_task`, `execute_task`, etc.

## Example Usage

### Simple Task

```
Create a Python function to calculate the nth Fibonacci number with:
- Unit tests
- Docstrings
- Type hints
- >90% test coverage
```

AIM will:
1. Parse constraints (test coverage requirement)
2. Decompose into subtasks (function + tests + docs)
3. Execute each subtask with specialized agents
4. Validate outputs against constraints
5. Iterate until all requirements are met
6. Return the final validated output

### Complex Task

```
Refactor my authentication system to:
- Use OAuth2 with JWT tokens
- Add rate limiting (100 req/min per IP)
- Implement RBAC with 3 roles (admin, user, guest)
- Add comprehensive logging
- Achieve >85% test coverage
- Generate OpenAPI documentation

Context: Using FastAPI and PostgreSQL
```

AIM will orchestrate multiple agents and iterate until every constraint is satisfied.

## Troubleshooting

### "Module not found: mcp"

```bash
pip install mcp
```

### "ANTHROPIC_API_KEY not set"

Make sure you've exported the key or added it to the config file.

### Claude Desktop doesn't show AIM tools

1. Check that the config file is in the right location
2. Verify the JSON syntax is valid
3. Restart Claude Desktop
4. Check Claude Desktop logs for errors

### Test the server directly

```bash
python -m aim_mcp_server
# Should start without errors
# Press Ctrl+C to stop
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [examples/](examples/) for more use cases
- Check out the [architecture documentation](docs/architecture.md)
- Join discussions on GitHub

## Getting Help

- 📖 [Documentation](https://github.com/aim-mcp/aim-mcp-server)
- 🐛 [Report Issues](https://github.com/aim-mcp/aim-mcp-server/issues)
- 💬 [Community Discussions](https://github.com/aim-mcp/aim-mcp-server/discussions)

---

Happy orchestrating! 🚀

