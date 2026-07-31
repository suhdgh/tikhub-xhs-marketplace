# TikHub XHS 跨平台环境引导版设计（v1.1.0）

## 目标

让 Windows 与 macOS 用户在安装 `tikhub-xhs-mcp` 后，不必分别理解 Python、pip、虚拟环境或平台命令差异。插件内置的引导 Skill 在用户请求小红书数据而 MCP 不可用时，明确说明问题、提供正确的本机初始化路径，并在获得用户明确同意后协助执行该路径。

## 范围

- 将本地 MCP 的运行器从系统 `python` 改为跨平台的 `uv`。
- 使用 `uv run --python 3.12 --with mcp==2.0.0 xhs_mcp_server.py` 启动服务器，使 `uv` 在首次运行时准备 Python 3.12 和固定版本的 MCP 包。
- 新增一个插件 Skill，用于缺失运行环境、缺失 MCP 工具、缺失 TikHub Key 时的安全引导。
- 新增 Windows PowerShell 和 macOS shell 初始化脚本。
- 更新面向用户的安装、配置与报错文档；插件版本升级到 `1.1.0`。
- 新增回归测试，锁定 Skill 声明、`uv` 启动命令、脚本安全约束和文档入口。

## 非目标

- 不自动或静默执行安装命令。
- 不在插件、脚本、日志、文档示例或聊天中存储、传输或索取 `TIKHUB_API_KEY`。
- 不打包 Windows/macOS 原生二进制，也不改为托管的远程 MCP 服务。
- 不修改现有九个 TikHub 数据工具、端点允许列表或只读安全边界。

## 方案选择

选择 `uv` 作为两个系统共用的运行器。`uv` 本身通过一次安装进入用户 PATH；之后 MCP 启动命令会自动下载所需的 Python 3.12 和 `mcp==2.0.0`。这避免了当前 `python` 命令在 Windows 可能指向商店占位符、在 macOS 通常不存在的差异。

替代方案未采用：保留 Python/pip 会继续把平台差异暴露给用户；打包原生二进制需要维护 Windows/macOS 架构、签名和更新链路。

## 组件与数据流

1. `.mcp.json` 保留 `cwd: "."` 与 `env_vars: ["TIKHUB_API_KEY"]`，但命令改为 `uv`，参数固定为 `run`、Python `3.12`、`mcp==2.0.0` 和 `xhs_mcp_server.py`。
2. `skills/tikhub-xhs-setup/SKILL.md` 加入插件清单。它只是一组 AI 可读取的安全工作流，不依赖服务器成功启动。
3. 当用户提出小红书/TikHub 数据请求时，Skill 要求 AI：
   - 若工具可用，先调用 `xhs_status`；
   - 若工具不存在、MCP 无法启动或状态表明环境未就绪，坦诚说明不能采集数据；
   - 根据 Windows/macOS 给出相应脚本路径和一条启动命令；
   - 仅在用户明确授权后执行本机脚本；
   - 提醒用户完全重启 Codex，再创建新任务并调用 `xhs_status`；
   - 仅将缺失 Key 解释为配置问题，绝不要求用户在聊天中粘贴 Key。
4. `scripts/setup-windows.ps1` 优先通过 WinGet 安装 `astral-sh.uv`；缺少 WinGet 时只输出官方安装指引，不静默下载或执行远程脚本。
5. `scripts/setup-macos.sh` 在已有 Homebrew 时使用 `brew install uv`；没有 Homebrew 时只输出 Astral 官方安装命令，要求用户自行确认执行。两份脚本都只验证 `uv --version`，不写入 TikHub Key。

## 错误处理与安全

- `uv` 不在 PATH：Skill 提供平台脚本；脚本返回非零错误并输出下一步，不能伪装为 MCP 已就绪。
- 首次下载失败：提示检查网络、公司代理或包源访问；不改写用户的代理、PATH 或安全策略。
- `xhs_status` 为 `configuration_required`：提示在操作系统环境中设置自己的 Key 后完全重启 Codex；不得把 Key 写入脚本参数或文件。
- 安装脚本可见、可审计，只执行 `uv` 安装与版本检查，不包含删除、提权、密钥处理或 TikHub 请求。

## 测试与验收

- 单元测试验证 MCP 命令、参数、工作目录和唯一允许转发的环境变量。
- 单元测试验证插件清单声明引导 Skill。
- 单元测试验证两份脚本存在、包含各自的安装/验证路径，且不包含 `TIKHUB_API_KEY`、`setx`、`export TIKHUB_API_KEY` 或 TikHub 网络调用。
- 单元测试验证引导 Skill 要求状态检查、明确授权、重启与密钥保密。
- 运行现有全部测试、`compileall`、插件结构校验和 Git diff 检查。

## 发布与使用结果

发布 `v1.1.0` 后，用户安装/更新插件并重启 Codex。若 `uv` 已可用，首次 MCP 启动会准备 Python 与 MCP 依赖；若不可用，AI 会在第一次数据请求时给出与系统匹配的可审阅初始化指引。用户仍只需在本机设置自己的 `TIKHUB_API_KEY`。
