import sys
import json
from client import CanaryTokenSentinel

sentinel = CanaryTokenSentinel()

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-canary-token-leak-sentinel-skill", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "generate_canary_token",
                        "description": "Generate unique HMAC canary token for session tripwire",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "session_id": {"type": "string", "description": "Unique session identifier"}
                            },
                            "required": ["session_id"]
                        }
                    },
                    {
                        "name": "check_canary_leak",
                        "description": "Check if output text leaks the designated canary token",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "output_text": {"type": "string", "description": "Generated output text to verify"},
                                "canary_token": {"type": "string", "description": "Canary token string"}
                            },
                            "required": ["output_text", "canary_token"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "generate_canary_token":
            sess = args.get("session_id", "default")
            tok = sentinel.generate_canary(sess)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"canary_token": tok})}]}
            }
        elif tool_name == "check_canary_leak":
            txt = args.get("output_text", "")
            tok = args.get("canary_token", "")
            leaked = sentinel.detect_leak(txt, tok)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"leaked": leaked, "canary_token": tok})}]}
            }
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
