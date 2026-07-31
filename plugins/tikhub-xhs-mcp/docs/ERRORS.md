# Errors and recovery

This plugin does not expose API keys. Keep your own `TIKHUB_API_KEY` private, and remember that TikHub data calls may be charged.

| Symptom | Meaning and next action |
| --- | --- |
| `uv` is not found | Fully close Codex and the current terminal, open a new terminal, and run `uv --version`. If it is still unavailable, review and install `uv` with `scripts/setup-windows.ps1` on Windows or `scripts/setup-macos.sh` on macOS/Linux, then fully restart Codex. An AI may run a setup script only after your explicit agreement. |
| First `uv run` download fails | The first start may need network access to download Python 3.12 and `mcp==2.0.0`. Check connectivity and retry the startup; if a network policy blocks the download, allow the required uv download or contact your network administrator. |
| MCP server does not start | Confirm `uv --version` works in a new terminal, then fully restart Codex and create a new task. The server command is `uv run --python 3.12 --with mcp==2.0.0 xhs_mcp_server.py`; a first-run download must complete before the server can start. |
| `configuration_required` | No usable `TIKHUB_API_KEY` was present when Codex started. Set your own key only in the operating-system environment that launches Codex, fully quit and restart Codex, create a new task, then call `xhs_status` again. Do not paste the key into chat, files, screenshots, logs, or source control. |
| HTTP 401 | Authentication failed. Verify that your own TikHub key is correct, active, and set in the environment used by Codex. |
| HTTP 402 | Your TikHub balance or plan may not cover this endpoint. Check your TikHub balance and plan before retrying. |
| HTTP 403 | Access was refused. Do not retry repeatedly; review TikHub access limits or contact TikHub support. |
| HTTP 404 | The requested TikHub endpoint is unavailable. Update the plugin, confirm the endpoint from `xhs_list_endpoints`, and retry only when appropriate. |
| Network or JSON error | A network failure occurred or TikHub returned non-JSON data. Check connectivity, parameters, and TikHub service status, then retry later if appropriate. |

For endpoint syntax, use `resource.method` names from [TOOLS.md](TOOLS.md), never a URL.
