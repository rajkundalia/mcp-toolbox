# Ollama Setup Guide

Quick guide to install and use Ollama with MCP Toolbox.

## Installation

### macOS/Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
Download from: https://ollama.ai/download/windows

### Verify Installation
```bash
ollama --version
```

## Download Model

```bash
# Download llama3 (recommended, ~4.7GB)
ollama pull llama3

# Or try smaller models
ollama pull mistral    # 4.1GB
ollama pull llama2     # 3.8GB
```

## Start Ollama

```bash
# Start Ollama server (keep running)
ollama serve
```

## Run MCP Host

In a new terminal:
```bash
cd mcp-toolbox
python host/run_ollama.py
```

## Test

```
You: Convert this YAML to JSON: name: Alice, age: 25
```

The AI will automatically call the `yaml_to_json` tool!

## Troubleshooting

**"Cannot connect to Ollama"**
```bash
# Check if running
ollama list

# Start server
ollama serve
```

**"Model not found"**
```bash
ollama pull llama3
```

**Change model:** Edit `host/config.yaml`
```yaml
ollama:
  model: "mistral"  # or llama2, codellama
```

## Resources

- Website: https://ollama.ai
- Models: https://ollama.ai/library
- Documentation: https://github.com/ollama/ollama