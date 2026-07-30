# Configure Codex

The plugin starts the command `python xhs_mcp_server.py` with the plugin root as its current working directory. Therefore, `python` must resolve to the Python interpreter where `mcp==2.0.0` was installed.

1. Set your own `TIKHUB_API_KEY` in the environment used to launch Codex. Do not put the key in a project file or share it.
2. From the plugin root, install dependencies with `python -m pip install -r requirements.txt`.
3. Confirm that `python -m pip show mcp` reports version `2.0.0` for that same interpreter.
4. Restart Codex after setting `TIKHUB_API_KEY`, because an already-running Codex process does not receive newly set environment variables.
5. Start a new task and call `xhs_status`. It should report `ready` and never display your key.

If `xhs_status` reports `configuration_required`, close Codex fully, verify the variable in the launching environment, then restart Codex. Do not make a paid TikHub request merely to test configuration.
