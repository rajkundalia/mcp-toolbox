# MCP Toolbox - Quick Start Guide

Get up and running with MCP Toolbox in 5 minutes.

## Step 1: Install (2 minutes)

```bash
# Clone repository
git clone https://github.com/rajkundalia/mcp-toolbox.git
cd mcp-toolbox

#Note: I have used PyCharm and everything was simpler there, if there is a mistake in the process here. Please raise an issue.

# Create virtual environment
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows) - I have not done this, since I used PyCharm to work on this project
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py
```

**Expected output:** "✓ All required components are installed!"

## Step 2: Test with Inspector (1 minute)

```bash
npx @modelcontextprotocol/inspector python server/stdio_server.py
```

This opens your browser with an interactive interface:

1. Click **"Initialize"** - should see "Connected"
2. Click **"List Tools"** - should see 6 tools
3. Select **"yaml_to_json"**
4. Enter: 
```
name: Raj
id: 1
```
5. Click **"Run Tool"**
6. See JSON output!

## Step 3: Run Example Client (30 seconds)

```bash
python client/example_usage.py
```

Watch it automatically test all 6 tools with examples.

**Expected output:** Multiple ✓ checkmarks showing successful tests.

You'll see server pushing events to the client in real-time!

## Step 4: Try with Ollama (1 minute)

```bash
# Install Ollama (if not installed)
# Visit: https://ollama.ai

# Download model
ollama pull llama3

# Start the host
python host/run_ollama.py
```

Now chat:

```
You: Convert this YAML to JSON: name: Alice, age: 30
```

The AI will automatically use the yaml_to_json tool!

## What Just Happened?

You've successfully:

1. ✓ Set up a working MCP server (STDIO transport)
2. ✓ Tested it with the official Inspector tool
3. ✓ Connected it to a Python client
4. ✓ Integrated it with an LLM (Ollama)

## Next Steps

### Learn the Architecture

Read through `README.md` to understand:
- How MCP protocol works
- Server vs Client vs Host
- STDIO vs HTTP transports

### Explore the Code

Start with these files:
1. `server/stdio_server.py` - See how servers work
2. `server/tools/format_tools.py` - See tool implementations
3. `server/registry.py` - See tool registration
4. `host/run_ollama.py` - See LLM integration

### Test Different Transports

### Run the Tests

```bash
pytest tests/ -v
```

See how tools are tested with mocks and edge cases.

## Common Issues

### "Command not found: npx"

Install Node.js from https://nodejs.org

### "Cannot connect to Ollama"

```bash
# Start Ollama
ollama serve

# In another terminal
ollama pull llama3
```

### "ModuleNotFoundError: No module named 'mcp'"

```bash
pip install -r requirements.txt
```

## Useful Commands

```bash
# Run STDIO server
python server/stdio_server.py

# Test with Inspector (STDIO)
npx @modelcontextprotocol/inspector python server/stdio_server.py

# Run example client
python client/example_usage.py

# Run Ollama host
python host/run_ollama.py

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_format_tools.py

# Run tests with coverage
pytest tests/ --cov=server

# Format code
black server/ client/ host/ tests/

# Lint code
ruff check server/

# Verify setup
python verify_setup.py
```

## Project Structure Quick Reference

```
mcp-toolbox/
├── server/              # MCP servers and tools
│   ├── stdio_server.py  # STDIO transport
│   ├── registry.py      # Tool registration
│   └── tools/           # Tool implementations
│
├── client/              # Example clients
│   └── example_usage.py # Client demo
│
├── host/                # LLM integration
│   ├── run_ollama.py    # Ollama host
│   └── config.yaml      # Configuration
│
└── tests/               # Test suite
    ├── test_format_tools.py
    ├── test_text_tools.py
    └── test_network_tools.py
```

## Resources

- **MCP Spec**: https://spec.modelcontextprotocol.io
- **MCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Inspector**: https://github.com/modelcontextprotocol/inspector
- **Ollama**: https://ollama.ai
- **FastAPI**: https://fastapi.tiangolo.com

## Need Help?

- Check `README.md` for detailed documentation
- Check `client/inspector_integration.md` for Inspector help
- Look at test files for usage examples

## Success Checklist

- [ ] Installed dependencies
- [ ] Verified setup with `verify_setup.py`
- [ ] Tested with MCP Inspector
- [ ] Ran example client successfully
- [ ] Connected with Ollama
- [ ] Explored the code
- [ ] Read architecture documentation
- [ ] Ran test suite

Once you've checked all boxes, you're ready to build with MCP! 