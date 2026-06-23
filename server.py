#!/usr/bin/env python3
import sys, json, httpx, base64, os, traceback

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11433")
client = httpx.Client(base_url=OLLAMA_URL, timeout=120)

def respond(id, result):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"result":result})+"\n")
    sys.stdout.flush()

def respond_error(id, code, msg):
    sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":id,"error":{"code":code,"message":msg}})+"\n")
    sys.stdout.flush()

def handle_tool_call(id, name, args):
    if name == "ask":
        prompt = args["prompt"]
        model = args.get("model", "llama3.2")
        r = client.post("/api/generate", json={"model":model,"prompt":prompt,"stream":False})
        r.raise_for_status()
        return respond(id, {"content":[{"type":"text","text":r.json()["response"]}]})

    elif name == "ask_with_image":
        prompt = args["prompt"]
        img_path = args["image_path"]
        model = args.get("model", "llava")
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        r = client.post("/api/chat", json={
            "model": model,
            "messages": [{"role":"user","content":prompt,"images":[b64]}],
            "stream": False
        })
        r.raise_for_status()
        return respond(id, {"content":[{"type":"text","text":r.json()["message"]["content"]}]})

    elif name == "list_models":
        r = client.get("/api/tags")
        r.raise_for_status()
        models = [m["name"] for m in r.json()["models"]]
        return respond(id, {"content":[{"type":"text","text":json.dumps(models, indent=2)}]})

    else:
        respond_error(id, -32601, f"Unknown tool: {name}")

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = req.get("method")
        rid = req.get("id")
        params = req.get("params", {})

        try:
            if method == "initialize":
                respond(rid, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "ollama-mcp", "version": "1.0.0"}
                })
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                respond(rid, {
                    "tools": [
                        {
                            "name": "ask",
                            "description": "Send a text prompt to Ollama",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string"},
                                    "model": {"type": "string", "default": "llama3.2"}
                                },
                                "required": ["prompt"]
                            }
                        },
                        {
                            "name": "ask_with_image",
                            "description": "Send text + image to a vision model",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string"},
                                    "image_path": {"type": "string", "description": "Local path to image file"},
                                    "model": {"type": "string", "default": "llava"}
                                },
                                "required": ["prompt", "image_path"]
                            }
                        },
                        {
                            "name": "list_models",
                            "description": "List available Ollama models",
                            "inputSchema": {"type": "object", "properties": {}}
                        }
                    ]
                })
            elif method == "tools/call":
                handle_tool_call(rid, params["name"], params.get("arguments", {}))
            else:
                respond_error(rid, -32601, f"Unknown method: {method}")
        except Exception as e:
            respond_error(rid, -32000, f"{type(e).__name__}: {e}")
            print(f"[ollama-mcp] {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()

if __name__ == "__main__":
    main()
