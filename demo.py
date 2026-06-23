#!/usr/bin/env python3
"""Minimal MCP client to test the server."""
import subprocess, json, sys

proc = subprocess.Popen(
    [sys.executable, "server.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
)

def send(msg):
    line = json.dumps(msg) + "\n"
    proc.stdin.write(line)
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())

# Initialize
r = send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{}})
print("init:", json.dumps(r, indent=2))

r = send({"jsonrpc":"2.0","id":2,"method":"notifications/initialized","params":{}})

# List tools
r = send({"jsonrpc":"2.0","id":3,"method":"tools/list","params":{}})
print("tools:", json.dumps(r, indent=2))

# Ask a question
r = send({"jsonrpc":"2.0","id":4,"method":"tools/call","params":{
    "name":"ask",
    "arguments":{"prompt":"Say hello in one word","model":"llama3.2"}
}})
print("ask:", json.dumps(r, indent=2))

# List models
r = send({"jsonrpc":"2.0","id":5,"method":"tools/call","params":{
    "name":"list_models","arguments":{}
}})
print("models:", json.dumps(r, indent=2))

proc.terminate()
