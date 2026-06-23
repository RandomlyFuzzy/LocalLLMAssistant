# LocalLLMAssistant

MCP server that exposes [Ollama](https://ollama.ai) as tools for AI assistants like [opencode](https://opencode.ai).

## Tools

- `ask` – send a text prompt to any Ollama model
- `ask_with_image` – send text + image to a vision model (e.g. `llava`)
- `list_models` – list available models

## Usage

```json
{
  "mcp": {
    "ollama-asker": {
      "type": "local",
      "command": ["python", "server.py"],
      "enabled": true,
      "env": {
        "OLLAMA_URL": "http://localhost:11434"
      }
    }
  }
}
```

Defaults to `http://localhost:11433` if `OLLAMA_URL` is not set.
