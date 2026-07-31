# TikHub XHS MCP

`tikhub-xhs-mcp` is a public, read-only MCP plugin for querying TikHub Xiaohongshu data. It requires `uv` and your own TikHub account and API key. TikHub may charge for API calls; confirm your plan and pricing before using data tools.

Never share your TikHub API key in chat, source control, screenshots, or logs. This plugin reads `TIKHUB_API_KEY` only from your environment and never displays it.

## Configure your API key

Create a TikHub account and API key, then set the key in the environment where Codex runs.

Windows (open a new Codex session after running this command):

```powershell
setx TIKHUB_API_KEY "your-key"
```

macOS/Linux:

```bash
export TIKHUB_API_KEY="your-key"
```

`your-key` is a non-secret placeholder. Replace it only in your local shell or operating-system environment with your own TikHub key.

## Install uv and prepare the MCP runtime

Install `uv`, then fully restart Codex. On the first plugin start, Codex automatically uses `uv` to prepare Python 3.12 and `mcp==2.0.0`; no separate `pip` installation is required.

Platform setup scripts are included for review:

- Windows: `scripts/setup-windows.ps1`
- macOS/Linux: `scripts/setup-macos.sh`

An AI may run either script only after you explicitly agree. The scripts do not accept, store, or display `TIKHUB_API_KEY`. For Codex-specific `uv`, PATH, and restart guidance, see [Configure Codex](docs/CONFIGURE_CODEX.md).

## Check configuration

After restarting Codex, call `xhs_status`. With no key it safely reports `configuration_required`; with your key configured it reports `ready`. `xhs_status` makes no TikHub API request.

For tool arguments and the complete endpoint allowlist, see [Tools](docs/TOOLS.md). For problem resolution, see [Errors](docs/ERRORS.md).
