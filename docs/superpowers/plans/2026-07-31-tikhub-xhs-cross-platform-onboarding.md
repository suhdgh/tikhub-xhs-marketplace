# TikHub XHS 跨平台环境引导版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** 发布 \`v1.1.0\`，让 Windows 和 macOS 用户通过 \`uv\` 获得统一的 TikHub XHS MCP 运行环境，并在环境不可用时由插件 Skill 提供安全引导。

**Architecture:** \`.mcp.json\` 将以 \`uv run\` 启动现有 Python MCP 入口，指定 Python 3.12 和 \`mcp==2.0.0\`，并继续只转发 \`TIKHUB_API_KEY\`。独立的插件 Skill 不依赖 MCP 成功启动，负责识别工具不可用、获得用户授权后调用平台脚本、提示重启，并禁止索取或写入用户密钥。

**Tech Stack:** Codex plugin manifest、MCP STDIO JSON 配置、Python \`unittest\`、PowerShell、POSIX shell、uv。

## Global Constraints

- 目标平台必须同时为 Windows 和 macOS；不得引入 Linux 专属或 Windows 专属的 MCP 启动命令。
- MCP 启动命令必须为 \`uv run --python 3.12 --with mcp==2.0.0 xhs_mcp_server.py\`，且保留 \`cwd: "."\`。
- \`.mcp.json\` 的唯一 \`env_vars\` 值必须是 \`TIKHUB_API_KEY\`；不得添加其值、占位符插值或其他密钥变量。
- 只有在用户明确授权后，Skill 才能让 AI 执行安装脚本；不得静默安装软件、修改代理/PATH/安全策略或发送 TikHub 请求。
- PowerShell 和 shell 脚本不得包含 \`TIKHUB_API_KEY\`、\`setx\`、\`export TIKHUB_API_KEY\`、TikHub URL 或删除命令。
- 插件版本必须更新为 \`1.1.0\`；不得修改现有九个数据工具、端点允许列表和只读安全边界。

---

## 文件结构

- \`plugins/tikhub-xhs-mcp/.mcp.json\`：跨平台 \`uv\` STDIO 启动配置与 Key 转发白名单。
- \`plugins/tikhub-xhs-mcp/.codex-plugin/plugin.json\`：版本升级并声明引导 Skill。
- \`plugins/tikhub-xhs-mcp/skills/tikhub-xhs-setup/SKILL.md\`：AI 可读取的缺失环境/缺失 Key 引导工作流。
- \`plugins/tikhub-xhs-mcp/scripts/setup-windows.ps1\`：使用 WinGet 安装/验证 uv 的可审阅 Windows 引导。
- \`plugins/tikhub-xhs-mcp/scripts/setup-macos.sh\`：使用已有 Homebrew 安装 uv、或输出官方命令的可审阅 macOS 引导。
- \`plugins/tikhub-xhs-mcp/README.md\`：面向普通用户的 uv 安装、Key 配置与验证入口。
- \`plugins/tikhub-xhs-mcp/docs/CONFIGURE_CODEX.md\`：解释 \`uv\` 启动模型、首次下载和重启要求。
- \`plugins/tikhub-xhs-mcp/docs/ERRORS.md\`：将 Python/pip 故障替换为 uv/环境引导故障排查。
- \`tests/test_plugin_catalog.py\`：验证发布清单、运行命令、Skill、脚本安全约束与文档入口。

## Task 1: uv 启动配置和 AI 引导 Skill

**Files:**
- Create: \`plugins/tikhub-xhs-mcp/skills/tikhub-xhs-setup/SKILL.md\`
- Modify: \`plugins/tikhub-xhs-mcp/.mcp.json\`
- Modify: \`plugins/tikhub-xhs-mcp/.codex-plugin/plugin.json\`
- Modify: \`tests/test_plugin_catalog.py\`

**Interfaces:**
- Consumes: 已有 \`xhs_status\` 工具；\`.mcp.json\` 中的 \`tikhub_xhs\` 配置；用户操作系统环境。
- Produces: \`tikhub-xhs-setup\` Skill 与 \`uv\` 启动定义，供平台脚本、文档和 Codex 插件加载器使用。

- [ ] **Step 1: 写入失败的发布配置测试**

在 \`PluginCatalogTests\` 增加 \`test_uv_runtime_and_setup_skill_are_packaged\`：

\`\`\`python
server = mcp_config["mcpServers"]["tikhub_xhs"]
self.assertEqual(server["command"], "uv")
self.assertEqual(
    server["args"],
    ["run", "--python", "3.12", "--with", "mcp==2.0.0", "xhs_mcp_server.py"],
)
self.assertEqual(server["cwd"], ".")
self.assertEqual(server["env_vars"], ["TIKHUB_API_KEY"])
self.assertEqual(manifest["version"], "1.1.0")
self.assertEqual(manifest["skills"], ["./skills/tikhub-xhs-setup"])
self.assertTrue((PLUGIN_ROOT / "skills" / "tikhub-xhs-setup" / "SKILL.md").is_file())
\`\`\`

- [ ] **Step 2: 运行测试，确认当前版本失败**

Run:

\`\`\`powershell
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' -m unittest tests.test_plugin_catalog.PluginCatalogTests.test_uv_runtime_and_setup_skill_are_packaged -v
\`\`\`

Expected: FAIL，因为当前命令仍为 \`python\`、版本仍为 \`1.0.1\`，且 Skill 文件不存在。

- [ ] **Step 3: 最小实现 MCP 和 Skill 声明**

将服务器配置替换为：

\`\`\`json
{
  "command": "uv",
  "args": ["run", "--python", "3.12", "--with", "mcp==2.0.0", "xhs_mcp_server.py"],
  "cwd": ".",
  "env_vars": ["TIKHUB_API_KEY"]
}
\`\`\`

将 \`plugin.json\` 的版本改为 \`1.1.0\`，并添加：

\`\`\`json
"skills": ["./skills/tikhub-xhs-setup"]
\`\`\`

创建 Skill，要求 AI 按以下顺序工作：

\`\`\`markdown
1. 工具存在时先调用 xhs_status。
2. 工具缺失、服务器无法启动或 uv 不可用时，明确说明不能采集数据，按当前系统给出对应脚本。
3. 仅在用户明确同意后执行安装脚本；否则只给可审阅命令。
4. 结束后要求完全重启 Codex、建立新任务，再调用 xhs_status。
5. 不要求用户粘贴 TIKHUB_API_KEY，不在命令、日志或文件中处理 Key。
\`\`\`

- [ ] **Step 4: 运行目标测试，确认通过**

Run:

\`\`\`powershell
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' -m unittest tests.test_plugin_catalog.PluginCatalogTests.test_uv_runtime_and_setup_skill_are_packaged -v
\`\`\`

Expected: PASS。

- [ ] **Step 5: 提交 Task 1**

\`\`\`powershell
git add -- plugins/tikhub-xhs-mcp/.mcp.json plugins/tikhub-xhs-mcp/.codex-plugin/plugin.json plugins/tikhub-xhs-mcp/skills/tikhub-xhs-setup/SKILL.md tests/test_plugin_catalog.py
git commit -m "feat: add uv runtime onboarding skill"
\`\`\`

## Task 2: Windows/macOS 可审阅环境脚本

**Files:**
- Create: \`plugins/tikhub-xhs-mcp/scripts/setup-windows.ps1\`
- Create: \`plugins/tikhub-xhs-mcp/scripts/setup-macos.sh\`
- Modify: \`tests/test_plugin_catalog.py\`

**Interfaces:**
- Consumes: 用户显式执行的脚本、系统 \`winget\`/\`brew\` 可用性和 \`uv\` 命令。
- Produces: 可由引导 Skill 引用的两份平台脚本；成功时输出 \`uv --version\`，不处理 TikHub 密钥。

- [ ] **Step 1: 写入失败的脚本契约测试**

增加 \`test_platform_setup_scripts_are_safe_and_auditable\`：

\`\`\`python
windows = (PLUGIN_ROOT / "scripts" / "setup-windows.ps1").read_text(encoding="utf-8")
macos = (PLUGIN_ROOT / "scripts" / "setup-macos.sh").read_text(encoding="utf-8")
self.assertIn("winget install --id astral-sh.uv -e", windows)
self.assertIn("uv --version", windows)
self.assertIn("brew install uv", macos)
self.assertIn("https://astral.sh/uv/install.sh", macos)
self.assertIn("uv --version", macos)
for text in (windows, macos):
    self.assertNotIn("TIKHUB_API_KEY", text)
    self.assertNotIn("setx", text.lower())
    self.assertNotIn("export tikhub_api_key", text.lower())
    self.assertNotIn("tikhub.io", text.lower())
\`\`\`

- [ ] **Step 2: 运行测试，确认当前版本失败**

Run:

\`\`\`powershell
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' -m unittest tests.test_plugin_catalog.PluginCatalogTests.test_platform_setup_scripts_are_safe_and_auditable -v
\`\`\`

Expected: FAIL，因为 \`scripts/\` 与两个脚本不存在。

- [ ] **Step 3: 创建最小、可审阅脚本**

Windows 脚本的核心路径：

\`\`\`powershell
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Error "WinGet 不可用。请从 https://docs.astral.sh/uv/getting-started/installation/ 安装 uv 后重试。"
    exit 1
}

winget install --id astral-sh.uv -e --accept-package-agreements --accept-source-agreements
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv 已安装；请关闭并重新打开终端，然后再次运行此脚本。"
    exit 0
}

uv --version
\`\`\`

macOS 脚本的核心路径：

\`\`\`bash
if command -v uv >/dev/null 2>&1; then
  uv --version
  exit 0
fi

if command -v brew >/dev/null 2>&1; then
  brew install uv
  uv --version
  exit 0
fi

printf '%s\n' 'Homebrew 未安装。请审阅并自行执行：curl -LsSf https://astral.sh/uv/install.sh | sh'
exit 1
\`\`\`

脚本须设置严格错误处理，输出“无需粘贴 TikHub Key”的安全提示，且不得下载/运行远程 shell 脚本、删除文件或改写 PATH。

- [ ] **Step 4: 运行目标测试，确认通过**

Run:

\`\`\`powershell
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' -m unittest tests.test_plugin_catalog.PluginCatalogTests.test_platform_setup_scripts_are_safe_and_auditable -v
\`\`\`

Expected: PASS。

- [ ] **Step 5: 提交 Task 2**

\`\`\`powershell
git add -- plugins/tikhub-xhs-mcp/scripts/setup-windows.ps1 plugins/tikhub-xhs-mcp/scripts/setup-macos.sh tests/test_plugin_catalog.py
git commit -m "feat: add cross-platform uv setup scripts"
\`\`\`

## Task 3: 用户文档与完整发布验证

**Files:**
- Modify: \`plugins/tikhub-xhs-mcp/README.md\`
- Modify: \`plugins/tikhub-xhs-mcp/docs/CONFIGURE_CODEX.md\`
- Modify: \`plugins/tikhub-xhs-mcp/docs/ERRORS.md\`
- Modify: \`tests/test_plugin_catalog.py\`

**Interfaces:**
- Consumes: Task 1 的 \`uv\` 命令与 Skill 路径，Task 2 的脚本路径。
- Produces: 完整的安装、排错和安全说明，供用户与引导 Skill 一致引用。

- [ ] **Step 1: 写入失败的文档入口测试**

增加 \`test_documentation_points_to_uv_and_platform_setup_scripts\`：

\`\`\`python
readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
configure = (PLUGIN_ROOT / "docs" / "CONFIGURE_CODEX.md").read_text(encoding="utf-8")
errors = (PLUGIN_ROOT / "docs" / "ERRORS.md").read_text(encoding="utf-8")
for text in (readme, configure, errors):
    self.assertIn("uv", text)
self.assertIn("scripts/setup-windows.ps1", readme)
self.assertIn("scripts/setup-macos.sh", readme)
self.assertIn("TIKHUB_API_KEY", configure)
self.assertNotIn("python -m pip install -r requirements.txt", configure)
\`\`\`

- [ ] **Step 2: 运行测试，确认当前版本失败**

Run:

\`\`\`powershell
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' -m unittest tests.test_plugin_catalog.PluginCatalogTests.test_documentation_points_to_uv_and_platform_setup_scripts -v
\`\`\`

Expected: FAIL，因为现有文档仍要求 \`python -m pip install -r requirements.txt\`，且未列出平台脚本。

- [ ] **Step 3: 更新文档**

README 必须把“安装依赖”替换为“安装 uv 后重启 Codex，插件首次启动自动准备 Python 3.12 与 \`mcp==2.0.0\`”；列出两个脚本路径，并说明 AI 只有在用户同意后才可执行脚本。配置文档必须解释 \`uv run\`、首次联网下载、\`uv\` 不在 PATH 时的步骤、完全重启 Codex 与 \`xhs_status\` 验证。错误文档必须将 Python/pip 故障行替换为 \`uv\` 缺失、首次下载失败、MCP 启动失败和 \`configuration_required\` 的独立处理路径。

所有文档中的 Key 示例必须继续使用非秘密占位符；不得把真实 Key 写进命令、文件或截图。

- [ ] **Step 4: 运行目标测试与完整测试**

Run:

\`\`\`powershell
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' -m unittest tests.test_plugin_catalog.PluginCatalogTests.test_documentation_points_to_uv_and_platform_setup_scripts -v
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' -m unittest tests.test_plugin_catalog tests.test_xiaohongshu_tikhub tests.test_xhs_mcp_service tests.test_xhs_mcp_server -v
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' -m compileall -q .\plugins\tikhub-xhs-mcp
& 'C:\Users\Mayn\AppData\Roaming\uv\python\cpython-3.14.4-windows-x86_64-none\python.exe' 'C:\Users\Mayn\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py' .\plugins\tikhub-xhs-mcp
git diff --check
\`\`\`

Expected: 所有测试通过、编译无输出、插件校验通过、Git diff 检查无输出。

- [ ] **Step 5: 提交 Task 3**

\`\`\`powershell
git add -- plugins/tikhub-xhs-mcp/README.md plugins/tikhub-xhs-mcp/docs/CONFIGURE_CODEX.md plugins/tikhub-xhs-mcp/docs/ERRORS.md tests/test_plugin_catalog.py
git commit -m "docs: guide cross-platform uv setup"
\`\`\`

## 最终发布检查

- [ ] 在合并/发布前重新运行 Task 3 的完整验证命令。
- [ ] 确认 \`git status --short --branch\` 没有未提交改动。
- [ ] 确认版本号仅为 \`1.1.0\`、没有把 \`TIKHUB_API_KEY\` 值提交到 Git 历史或文件。
- [ ] 以非强制方式推送 \`main\`，创建带注释的 \`v1.1.0\` 标签，并用 \`git ls-remote --heads --tags origin main refs/tags/v1.1.0\` 验证远端。

