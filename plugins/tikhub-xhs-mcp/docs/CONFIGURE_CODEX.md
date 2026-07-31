# Configure Codex

The plugin starts with `uv run --python 3.12 --with mcp==2.0.0 xhs_mcp_server.py` from the plugin root. `uv run` selects or downloads Python 3.12 when needed and installs the pinned MCP dependency for the launch, so a separate Python environment and `pip` setup are not required.

1. Set your own `TIKHUB_API_KEY` only in the operating-system environment that starts Codex. Do not put the key in a project file, chat, screenshot, log, or source control. Examples must use a non-secret placeholder such as `your-key`.
2. Install `uv`. Review the platform script first: `scripts/setup-windows.ps1` on Windows or `scripts/setup-macos.sh` on macOS/Linux. An AI may execute a script only after your explicit agreement.
3. The first `uv run` needs network access to download Python 3.12 and `mcp==2.0.0` when they are not already cached. Let that first startup finish before treating it as an MCP failure.
4. If `uv` is not on PATH, fully close Codex and the current terminal, open a new terminal, and run `uv --version`. If it is still unavailable, install `uv` with the reviewed platform script or the official uv installation instructions, then repeat the restart and version check.
5. Fully quit Codex after installing `uv` or changing `TIKHUB_API_KEY`; reopening only a task is not enough for a running Codex process to receive the change.
6. Start Codex again, create a new task, and call `xhs_status`. It reports `ready` when configuration is available and `configuration_required` when no usable key was present. It never makes a TikHub API request or displays the key.

If `xhs_status` reports `configuration_required`, follow the dedicated [error recovery](ERRORS.md#errors-and-recovery) path. Do not make a paid TikHub request merely to test configuration.
