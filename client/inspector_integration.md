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

## Testing STDIO Server

STDIO is the **recommended transport for local development** because it's simpler and more reliable.

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

![Inspector Interface](img.png)

### Step 4: Test Tool Execution

Let's test the `yaml_to_json` tool:

1. **Select Tool**: Click on "yaml_to_json"
2. **View Schema**: Examine the input parameters
3. **Enter Arguments**:
```yaml
name: Raj
id: 1
```
4. **Click "Run Tool"**
5. **View Result**: You should see the JSON output

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

## Troubleshooting [Provided by LLM, I haven't tried them]

### Issue: Inspector won't connect to STDIO server

**Symptoms**: "Connection Failed" or "Server not responding"

**Solutions**:
1. Verify server runs standalone: `python server/stdio_server.py`
2. Check for Python errors in Inspector console (F12 Developer Tools)
3. Ensure no other process is using the server
4. Verify Python version 3.10+ is installed
5. Check that all dependencies are installed: `pip install -r requirements.txt`

### Issue: Tools don't appear after connecting

**Symptoms**: List tools returns empty or errors

**Solutions**:
1. Check server initialized successfully (look for initialization in logs)
2. Verify `registry.py` is properly imported in your server
3. Check for Python import errors in server stderr
4. Click "Initialize" button in Inspector before "List Tools"
5. Check browser console (F12) for JavaScript errors
6. Restart server and reconnect

### Issue: Tool execution fails

**Symptoms**: Error when calling tools despite successful connection

**Solutions**:
1. **Verify input matches schema exactly**: Check data types and required fields
2. **Check server logs**: Look for detailed error messages in server terminal
3. **Test tool directly in Python**:
   ```python
   from registry import get_tool_function
   func = get_tool_function("yaml_to_json")
   result = func(yaml="name: test")
   print(result)
   ```
4. **Ensure dependencies installed**: `pip install -r requirements.txt`
5. **Check argument format**: Inspector sends JSON, ensure your tool accepts it
6. **Review error response**: Check both Inspector UI and server logs

### Common Issues Summary

| Issue | Quick Fix | Best Solution |
|-------|-----------|---------------|
| Tools not showing | Click Initialize | Check registry import |
| Execution fails | Check logs | Validate input schema |
| Connection drops | Check firewall | Add keepalives |
| CORS errors | Add middleware | Configure origins |

## Advanced Usage [Provided by LLM, I haven't tried them]

### Testing Multiple Tools in Sequence

Create a testing workflow to verify tool chaining:

1. **Convert YAML to JSON**:
   ```yaml
   name: John Doe
   age: 30
   ```

2. **Base64 encode the JSON**:
   ```json
   {"json": "{\"name\": \"John Doe\", \"age\": 30}"}
   ```

3. **Hash the encoded string**:
   ```json
   {"text": "<base64-output>"}
   ```

4. **Validate URL format** (if applicable)

This workflow tests:
- Data transformation between tools
- Error handling at each step
- Output format compatibility
- 
## Best Practices

1. **Start with STDIO**: Use STDIO transport during initial development for simplicity

2. **Test Early and Often**: Use Inspector from the start of development, not just at the end

3. **Validate Schemas First**: Before writing tool logic, verify schemas in Inspector

4. **Test Error Cases**: Always test with:
   - Invalid inputs
   - Missing required fields
   - Wrong data types
   - Edge cases (empty strings, null values)

5. **Document Working Examples**: Save successful test cases as documentation

## Resources

- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector) - Official Inspector repository
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io) - Complete protocol docs
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Python implementation
- [MCP Documentation](https://modelcontextprotocol.io) - Getting started guides
- [FastAPI Documentation](https://fastapi.tiangolo.com) - Alternative to Starlette

## Conclusion

The MCP Inspector is an invaluable tool for:
- **Rapid Development**: Test tools without building a full client
- **Debugging**: See exactly what's happening in the protocol
- **Schema Validation**: Catch issues before deployment
- **Documentation**: Generate examples from working tests

**Key Takeaway**: Always start with STDIO transport in Inspector for the simplest, most reliable development experience. 