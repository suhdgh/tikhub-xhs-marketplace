# Configure Codex

The plugin starts with `uv run --locked --python 3.12 xhs_mcp_server.py` from the plugin root. `uv run` selects or downloads Python 3.12 when needed and creates a persistent environment from the committed dependency lock file, so a separate Python environment and `pip` setup are not required. Later starts reuse that environment.

1. Set your own `TIKHUB_API_KEY` only in the operating-system environment that starts Codex. Do not put the key in a project file, chat, screenshot, log, or source control. Examples must use a non-secret placeholder such as `your-key`.
2. Install `uv`. Review the platform script first: `scripts/setup-windows.ps1` on Windows or `scripts/setup-macos.sh` on macOS/Linux. An AI may execute a script only after your explicit agreement.
3. The first `uv run` needs network access to download Python 3.12 and the locked dependency set when they are not already cached. Let that first startup finish before treating it as an MCP failure. Later starts reuse the environment.
4. If `uv` is not on PATH, fully close Codex and the current terminal, open a new terminal, and run `uv --version`. If it is still unavailable, install `uv` with the reviewed platform script or the official uv installation instructions, then repeat the restart and version check.
5. Fully quit Codex after installing `uv` or changing `TIKHUB_API_KEY`; reopening only a task is not enough for a running Codex process to receive the change.
6. Start Codex again, create a new task, and call `xhs_status`. It reports `ready` when configuration is available and `configuration_required` when no usable key was present. It never makes a TikHub API request or displays the key.

## Run read-only data tools without repeated confirmations

The MCP tools are marked read-only. To ensure Codex only asks for confirmation if a future write tool is added, add the following once to your own `~/.codex/config.toml`, then fully restart Codex:

```toml
[plugins."tikhub-xhs-mcp@tikhub-xhs-marketplace".mcp_servers.tikhub_xhs]
default_tools_approval_mode = "writes"
```

This setting applies only to this MCP server. It does not expose your API key, and it does not remove confirmation from write-capable tools. TikHub data requests may still create charges.

## Cache and refresh behavior

Successful identical data calls are cached in memory for five minutes. The cache includes pagination, so fetching more pages after a smaller result set reuses already fetched pages. When the user explicitly asks to refresh, re-fetch, or avoid cached data, call the relevant tool with `refresh=true`; it bypasses the cache and requests TikHub again.

If `xhs_status` reports `configuration_required`, follow the dedicated [error recovery](ERRORS.md#errors-and-recovery) path. Do not make a paid TikHub request merely to test configuration.
