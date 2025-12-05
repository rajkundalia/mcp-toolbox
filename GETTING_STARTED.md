# Getting Started - Where to Begin

**New to this project?** Start here! This guide tells you exactly which files to open and in what order.

## Installation (3 commands)

```bash
cd mcp-toolbox
pip install -r requirements.txt
python verify_setup.py
```

That's it! If you see "✓ All required components are installed!" you're ready.

## Where to Start Reading

### If you want to understand how it works (30 min read):

**Read in this order:**

1. **`server/tools/text_tools.py`** (5 min)
   - Start here - simplest tools
   - See how tools are just Python functions
   - Understand input/output format

2. **`server/registry.py`** (5 min)
   - See how tools are registered
   - Understand JSON schemas
   - See the connection between tools and MCP

3. **`server/stdio_server.py`** (10 min)
   - See how MCP server works
   - Understand the decorators (`@app.list_tools`, `@app.call_tool`)
   - See how tools are called

4. **`client/example_usage.py`** (5 min)
   - See how to connect to a server
   - See how to call tools
   - Understand client-server flow

5. **`host/run_ollama.py`** (5 min)
   - See how LLMs use MCP tools
   - Understand the host role
   - See the complete flow

### If you want to try it immediately (5 min):

**Run these commands in order:**

```bash
# 1. Test with Inspector (opens browser)
npx @modelcontextprotocol/inspector python server/stdio_server.py

# 2. In the browser:
#    - Click "Initialize"
#    - Click "List Tools"
#    - Select "base64_encode"
#    - Enter: {"text": "hello"}
#    - Click "Call Tool"

# 3. Run the example client
python client/example_usage.py

# 4. If you have Ollama:
python host/run_ollama.py
# Then type: "encode 'hello world' to base64"
```

## File Guide - What Each File Does

### Core Files (must read)

| File | What it does | Read if... |
|------|-------------|------------|
| `server/tools/text_tools.py` | Simple tools (encode, hash) | You want to understand tools |
| `server/registry.py` | Tool registration | You want to add a tool |
| `server/stdio_server.py` | MCP server implementation | You want to understand servers |

### Example Files (helpful)

| File | What it does | Read if... |
|------|-------------|------------|
| `client/example_usage.py` | How to use tools from Python + SSE streaming | You want to build a client |
| `host/run_ollama.py` | How LLMs use tools | You want LLM integration |

### Other Tools (read later)

| File | What it does |
|------|-------------|
| `server/tools/format_tools.py` | YAML/JSON conversion |
| `server/tools/network_tools.py` | Port check, URL validation |
| `server/http_server.py` | HTTP SSE server (alternative transport) |

### Documentation (reference)

| File | Purpose |
|------|---------|
| `README.md` | Full documentation |
| `QUICKSTART.md` | 5-minute tutorial |
| `client/inspector_integration.md` | MCP Inspector guide |

## Most Common Tasks

### "I want to add a new tool"

1. Open `server/tools/text_tools.py` - copy the pattern
2. Open `server/registry.py` - add your tool there
3. Run: `npx @modelcontextprotocol/inspector python server/stdio_server.py`
4. Test your tool in the browser

### "I want to understand the flow"

1. Start Inspector: `npx @modelcontextprotocol/inspector python server/stdio_server.py`
2. Open `server/stdio_server.py` in editor
3. Call a tool in Inspector
4. Watch the console output in terminal

### "I want to integrate with my LLM"

1. Read `host/run_ollama.py` (shows the pattern)
2. Copy the structure
3. Replace Ollama calls with your LLM API
4. Keep the MCP client parts the same

### "I want to understand MCP protocol"

1. Read `server/stdio_server.py` comments (explains protocol)
2. Use Inspector and watch JSON-RPC messages
3. Read `README.md` Architecture section

## Visual Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. START HERE                                       │
│    server/tools/text_tools.py                       │
│    └─> See how tools work                           │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ 2. THEN HERE                                        │
│    server/registry.py                               │
│    └─> See how tools are registered                 │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ 3. THEN HERE                                        │
│    server/stdio_server.py                           │
│    └─> See how MCP server works                     │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ 4. TRY IT                                           │
│    npx @modelcontextprotocol/inspector ...          │
│    └─> Test in browser                              │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│ 5. OPTIONAL: LLM INTEGRATION                        │
│    host/run_ollama.py                               │
│    └─> See how LLMs use tools                       │
└─────────────────────────────────────────────────────┘
```

## FAQ

**Q: Do I need to read everything?**  
A: No! Start with `text_tools.py` and `registry.py`. That's 10 minutes and you'll understand the basics.

**Q: Which file should I run first?**  
A: Run the Inspector: `npx @modelcontextprotocol/inspector python server/stdio_server.py`

**Q: Do I need Ollama?**  
A: No. You can use MCP without any LLM. Ollama is only for the interactive chat demo.

**Q: Where do I add my own tool?**  
A: Create it in `server/tools/`, then register it in `server/registry.py`. See `CONTRIBUTING.md` for details.

**Q: What's the difference between server, client, and host?**  
A: 
- **Server** = Provides tools (this project)
- **Client** = Uses tools (example in `client/`)
- **Host** = Connects LLM to tools (example in `host/`)

**Q: Can I skip the HTTP server?**  
A: Yes! Focus on STDIO server first (`stdio_server.py`). HTTP is an alternative transport.

## Next Steps After This

1. ✅ You've installed everything
2. ✅ You know which files to read
3. ✅ You've tried it with Inspector

**Now:** 
- Read the files in order above
- Try modifying a tool
- Add your own tool
- Read `README.md` for deeper understanding

---

**Remember:** Start simple! Read `text_tools.py` first, try the Inspector, then explore more. Don't try to understand everything at once.