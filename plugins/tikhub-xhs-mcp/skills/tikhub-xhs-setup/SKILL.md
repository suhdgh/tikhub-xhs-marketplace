---
name: tikhub-xhs-setup
description: Use when the TikHub XHS MCP tools are missing, cannot start, or uv is unavailable on Windows, macOS, or Linux.
---

# TikHub XHS MCP setup

## First check

If the `xhs_status` tool is available, call it first. Use its result to decide whether the MCP service is configured and ready.

## Unavailable tools or runtime

If the tools are missing, the server cannot start, or `uv` is unavailable, clearly state that TikHub XHS data cannot be collected yet. Identify the current operating system and provide the corresponding installation command for review only:

| System | Command |
| --- | --- |
| Windows | `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` |
| macOS / Linux | `curl -LsSf https://astral.sh/uv/install.sh | sh` |

Do not run an installation command unless the user explicitly agrees. Do not ask the user to paste `TIKHUB_API_KEY`, and never include or handle a Key in commands, logs, or files.

## After installation

Ask the user to fully restart Codex and create a new task. In the new task, call `xhs_status` again before attempting any data collection.
