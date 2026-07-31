---
name: tikhub-xhs-setup
description: Use when the TikHub XHS MCP tools are missing, cannot start, or uv is unavailable on Windows or macOS.
---

# TikHub XHS MCP setup

## First check

If the `xhs_status` tool is available, call it first. Use its result to decide whether the MCP service is configured and ready.

## Unavailable tools or runtime

If the tools are missing, the server cannot start, or `uv` is unavailable, clearly state that TikHub XHS data cannot be collected yet. Resolve the installed plugin root, identify the current operating system, and provide the corresponding local script command for review only:

| System | Command |
| --- | --- |
| Windows | `powershell -NoProfile -File "<plugin-root>/scripts/setup-windows.ps1"` |
| macOS | `bash "<plugin-root>/scripts/setup-macos.sh"` |

Do not run a local script unless the user explicitly agrees. After agreement, run only the matching packaged script above; do not substitute a downloaded installer. Do not ask the user to paste `TIKHUB_API_KEY`, and never include or handle a Key in commands, logs, or files.

## After installation

Ask the user to fully restart Codex and create a new task. In the new task, call `xhs_status` again before attempting any data collection.
