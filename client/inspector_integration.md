# MCP Inspector Integration Guide

## What is MCP Inspector?

The MCP Inspector is an official debugging and testing tool provided by Anthropic for MCP servers. It provides:

- **Interactive Testing**: Call tools and see responses in real-time
- **Schema Validation**: Verify your tool schemas are correct
- **Request/Response Inspection**: See the raw JSON-RPC messages
- **Development Workflow**: Test without building a full client

Think of it as "Postman for MCP servers" - an essential development tool.

## Installation

The Inspector is distributed as an npm package. You don't need to install it globally; you can run it directly with `npx`:

```bash
npx @modelcontextprotocol/inspector
```

This will:
1. Download the latest Inspector version (if needed)
2. Launch the web-based Inspector interface
3. Open your browser to `http://localhost:5173`

## Testing STDIO Server

### Step 1: Start the Inspector

```bash
npx @modelcontextprotocol/inspector python server/stdio_server.py
```

This command:
- Launches the Inspector web UI
- Starts your STDIO server as a subprocess
- Connects them together
- Opens browser to Inspector interface

### Step 2: Connect and Initialize

In the Inspector UI:

1. **Connection Status**: You should see "Connected" with a green indicator
2. **Click "Initialize"**: This sends the MCP initialization handshake
3. **View Server Info**: After initialization, you'll see server metadata

**Screenshot placeholder**: Inspector connection screen showing green "Connected" status

### Step 3: Discover Tools

1. **Click "List Tools"** button
2. **View Results**: You should see all 6 tools:
   - yaml_to_json
   - json_to_yaml
   - base64_encode
   - sha256_hash
   - is_port_open
   - validate_url

Each tool displays:
- Name
- Description
- Input schema (click to expand)

**Screenshot placeholder**: Inspector tools list showing all 6 tools with schemas

### Step 4: Test Tool Execution

Let's test the `yaml_to_json` tool:

1. **Select Tool**: Click on "yaml_to_json"
2. **View Schema**: Examine the input parameters
3. **Enter Arguments**:
   ```json
   {
     "yaml": "name: John\nage: 30\ncity: NYC"
   }
   ```
4. **Click "Call Tool"**
5. **View Result**: You should see the JSON output

**Screenshot placeholder**: Inspector showing yaml_to_json execution with input and output

### Step 5: Test Error Handling

Try invalid input to test error handling:

1. **Select Tool**: `yaml_to_json`
2. **Invalid YAML**:
   ```json
   {
     "yaml": "invalid: yaml: [[["
   }
   ```
3. **Expected Result**: Error message about invalid YAML

**Screenshot placeholder**: Inspector showing error response with error code and message

## Testing HTTP SSE Server

### Step 1: Start HTTP Server

In a terminal:

```bash
python server/http_server.py
```

Leave this running. You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Configure Inspector for HTTP

Create a configuration file `inspector-config.json`:

```json
{
  "mcpServers": {
    "mcp-toolbox-http": {
      "url": "http://localhost:8000",
      "transport": "sse"
    }
  }
}
```

### Step 3: Launch Inspector with Config

```bash
npx @modelcontextprotocol/inspector --config inspector-config.json
```

### Step 4: Test HTTP Server

Follow the same testing steps as STDIO, but note:
- Connection uses HTTP instead of subprocess
- You can monitor server logs in the terminal where HTTP server runs
- Health endpoint available at `http://localhost:8000/health`

## Configuration File Format

For complex setups, create a `mcp-config.json`:

```json
{
  "mcpServers": {
    "toolbox-stdio": {
      "command": "python",
      "args": ["server/stdio_server.py"],
      "transport": "stdio"
    },
    "toolbox-http": {
      "url": "http://localhost:8000",
      "transport": "sse"
    }
  }
}
```

Use with:
```bash
npx @modelcontextprotocol/inspector --config mcp-config.json
```

## Troubleshooting

### Issue: Inspector won't connect to STDIO server

**Symptoms**: "Connection Failed" or "Server not responding"

**Solutions**:
1. Check server path is correct: `python server/stdio_server.py` works standalone
2. Check for Python errors in Inspector console
3. Verify no other process is using the server
4. Check Python version (3.10+ required)

### Issue: HTTP server connection fails

**Symptoms**: "Cannot connect to http://localhost:8000"

**Solutions**:
1. Verify server is running: `curl http://localhost:8000/health`
2. Check port 8000 is not blocked
3. Look for errors in server terminal
4. Try different port in config and `http_server.py`

### Issue: Tools don't appear

**Symptoms**: List tools returns empty or errors

**Solutions**:
1. Check server initialized successfully (look for initialization in logs)
2. Verify `registry.py` is properly imported
3. Check for Python import errors in server stderr
4. Restart server and try again

### Issue: Tool execution fails

**Symptoms**: Error when calling tools

**Solutions**:
1. Verify input matches schema exactly
2. Check server logs for detailed error
3. Test tool function directly in Python
4. Ensure all dependencies installed (`requirements.txt`)

### Issue: SSE connection drops

**Symptoms**: HTTP server connects then disconnects

**Solutions**:
1. Check for proxy/firewall blocking SSE
2. Verify server sends keepalive messages
3. Look for server crashes in logs
4. Try increasing timeout in browser

## Advanced Usage

### Inspecting Raw Messages

The Inspector shows raw JSON-RPC messages:

1. **Open DevTools**: Browser developer console
2. **Network Tab**: See HTTP requests (for HTTP transport)
3. **Console Tab**: See connection logs
4. **Inspector Logs**: Built-in message viewer

### Testing Multiple Tools in Sequence

Create a testing workflow:

1. Convert YAML to JSON
2. Base64 encode the JSON
3. Hash the encoded string
4. Validate the result

This helps test tool chaining and integration.

### Automated Testing

While Inspector is primarily interactive, you can:

1. Document test cases as JSON files
2. Use Inspector to validate schemas
3. Export working requests for integration tests
4. Share test cases with team

## Best Practices

1. **Test Early**: Use Inspector from the start of development
2. **Validate Schemas**: Ensure input/output schemas match implementation
3. **Test Errors**: Always test invalid inputs
4. **Document Findings**: Save working examples for documentation
5. **Version Control Config**: Commit `inspector-config.json` to repo

## Next Steps

After validating with Inspector:

1. **Build Integration Tests**: Use `pytest` (see `tests/` directory)
2. **Develop Real Client**: See `client/example_usage.py`
3. **Connect to LLM**: Try `host/run_ollama.py`
4. **Deploy**: Move to production with proper error handling

## Resources

- [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)