# Errors and recovery

This plugin does not expose API keys. Keep your own `TIKHUB_API_KEY` private, and remember that TikHub data calls may be charged.

| Symptom | Meaning and next action |
| --- | --- |
| `configuration_required` or a message naming `TIKHUB_API_KEY` | No usable key was present when Codex started. Set your own environment variable, restart Codex, then call `xhs_status` again. |
| HTTP 401 | Authentication failed. Verify that your own TikHub key is correct, active, and set in the environment used by Codex. |
| HTTP 402 | Your TikHub balance or plan may not cover this endpoint. Check your TikHub balance and plan before retrying. |
| HTTP 403 | Access was refused. Do not retry repeatedly; review TikHub access limits or contact TikHub support. |
| HTTP 404 | The requested TikHub endpoint is unavailable. Update the plugin, confirm the endpoint from `xhs_list_endpoints`, and retry only when appropriate. |
| Network or JSON error | A network failure occurred or TikHub returned non-JSON data. Check connectivity, parameters, and TikHub service status, then retry later if appropriate. |
| `ModuleNotFoundError: mcp` or dependency error | Install dependencies with `python -m pip install -r requirements.txt` using the same Python interpreter that the plugin command resolves to. |
| MCP server does not start | Confirm `python` can run `xhs_mcp_server.py` from the plugin root, `mcp==2.0.0` is installed for that interpreter, and restart Codex after configuration changes. |

For endpoint syntax, use `resource.method` names from [TOOLS.md](TOOLS.md), never a URL.
