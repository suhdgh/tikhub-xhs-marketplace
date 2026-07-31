import base64
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "tikhub-xhs-mcp"


class PluginCatalogTests(unittest.TestCase):
    def run_windows_setup_offline(
        self,
        *,
        uv_available: bool,
        winget_exit_code: int = 0,
        expose_uv_after_install: bool = True,
        uv_exit_code: int = 0,
    ):
        powershell = shutil.which("powershell.exe") or shutil.which("pwsh")
        if powershell is None:
            self.skipTest("PowerShell is required for the Windows setup behavior test")

        setup_script = PLUGIN_ROOT / "scripts" / "setup-windows.ps1"
        with tempfile.TemporaryDirectory() as temp_dir:
            event_log = Path(temp_dir) / "events.log"
            quoted_script = str(setup_script).replace("'", "''")
            quoted_log = str(event_log).replace("'", "''")
            harness = f"""
$global:StubUvAvailable = ${str(uv_available).lower()}
$global:StubWingetExitCode = {winget_exit_code}
$global:StubExposeUvAfterInstall = ${str(expose_uv_after_install).lower()}
$global:StubUvExitCode = {uv_exit_code}
$global:StubEventLog = '{quoted_log}'

function global:Get-Command {{
    [CmdletBinding()]
    param([Parameter(Position = 0, Mandatory = $true)][string]$Name)

    if ($Name -eq 'uv') {{
        if ($global:StubUvAvailable) {{
            return [pscustomobject]@{{ Name = 'uv' }}
        }}
        return
    }}
    if ($Name -eq 'winget') {{
        return [pscustomobject]@{{ Name = 'winget' }}
    }}
    return Microsoft.PowerShell.Core\\Get-Command $Name -ErrorAction SilentlyContinue
}}

function global:winget {{
    Add-Content -LiteralPath $global:StubEventLog -Value 'winget install'
    $global:LASTEXITCODE = $global:StubWingetExitCode
    if (
        $global:StubWingetExitCode -eq 0 -and
        $global:StubExposeUvAfterInstall
    ) {{
        $global:StubUvAvailable = $true
    }}
}}

function global:uv {{
    Add-Content -LiteralPath $global:StubEventLog -Value 'uv --version'
    $global:LASTEXITCODE = $global:StubUvExitCode
}}

$source = Get-Content -LiteralPath '{quoted_script}' -Raw
& ([scriptblock]::Create($source))
"""
            encoded_harness = base64.b64encode(harness.encode("utf-16le")).decode("ascii")
            result = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-NonInteractive",
                    "-EncodedCommand",
                    encoded_harness,
                ],
                check=False,
                capture_output=True,
            )
            events = (
                event_log.read_text(encoding="utf-8-sig").splitlines()
                if event_log.exists()
                else []
            )
            diagnostic = (result.stdout + result.stderr).decode(
                "utf-8", errors="replace"
            )
            return result.returncode, events, diagnostic

    def test_catalog_and_plugin_manifest_expose_the_public_plugin(self):
        self.assertTrue(MARKETPLACE.is_file())
        self.assertTrue((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").is_file())
        self.assertTrue((PLUGIN_ROOT / ".mcp.json").is_file())
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["name"], "tikhub-xhs-marketplace")
        self.assertEqual(marketplace["plugins"][0]["name"], "tikhub-xhs-mcp")
        self.assertEqual(
            marketplace["plugins"][0]["source"],
            {"source": "local", "path": "./plugins/tikhub-xhs-mcp"},
        )
        self.assertEqual(
            marketplace["plugins"][0]["policy"],
            {"installation": "AVAILABLE", "authentication": "ON_USE"},
        )
        self.assertEqual(manifest["name"], "tikhub-xhs-mcp")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")

    def test_mcp_server_forwards_only_tikhub_api_key(self):
        mcp_config = json.loads((PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        server = mcp_config["mcpServers"]["tikhub_xhs"]
        self.assertEqual(server["env_vars"], ["TIKHUB_API_KEY"])
        self.assertEqual(manifest["version"], "1.1.0")

    def test_uv_runtime_and_setup_skill_are_packaged(self):
        mcp_config = json.loads((PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        server = mcp_config["mcpServers"]["tikhub_xhs"]
        self.assertEqual(server["command"], "uv")
        self.assertEqual(
            server["args"],
            ["run", "--python", "3.12", "--with", "mcp==2.0.0", "xhs_mcp_server.py"],
        )
        self.assertEqual(server["cwd"], ".")
        self.assertEqual(server["env_vars"], ["TIKHUB_API_KEY"])
        self.assertEqual(manifest["version"], "1.1.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue((PLUGIN_ROOT / "skills" / "tikhub-xhs-setup" / "SKILL.md").is_file())

    def test_setup_skill_requires_safe_cross_platform_onboarding(self):
        setup_skill = (
            PLUGIN_ROOT / "skills" / "tikhub-xhs-setup" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("xhs_status", setup_skill)
        self.assertIn("user explicitly agrees", setup_skill)
        self.assertIn("fully restart Codex", setup_skill)
        self.assertIn("create a new task", setup_skill)
        self.assertIn("Do not ask the user to paste `TIKHUB_API_KEY`", setup_skill)
        self.assertIn("scripts/setup-windows.ps1", setup_skill)
        self.assertIn("scripts/setup-macos.sh", setup_skill)
        self.assertRegex(setup_skill, r"(?i)powershell\b[^\n]*-File\b")
        self.assertRegex(setup_skill, r"(?i)\bbash\b[^\n]*setup-macos\.sh")
        self.assertNotIn("ExecutionPolicy", setup_skill)
        self.assertNotIn("ByPass", setup_skill)
        self.assertNotIn("TIKHUB_API_KEY=", setup_skill)
        self.assertNotRegex(
            setup_skill,
            r"(?i)\b(?:irm|iex|invoke-restmethod|invoke-webrequest|curl|wget)\b",
        )

    def test_windows_setup_execution_order_and_exit_contract_are_offline(self):
        cases = (
            ("existing uv", True, 0, True, 0, 0, ["uv --version"]),
            (
                "existing broken uv",
                True,
                0,
                True,
                17,
                "nonzero",
                ["uv --version"],
            ),
            (
                "successful install",
                False,
                0,
                True,
                0,
                0,
                ["winget install", "uv --version"],
            ),
            (
                "failed install",
                False,
                23,
                True,
                0,
                "nonzero",
                ["winget install"],
            ),
            (
                "uv missing after install",
                False,
                0,
                False,
                0,
                "nonzero",
                ["winget install"],
            ),
        )

        for (
            name,
            uv_available,
            winget_exit_code,
            expose_uv_after_install,
            uv_exit_code,
            expected_exit,
            expected_events,
        ) in cases:
            with self.subTest(name=name):
                exit_code, events, diagnostic = self.run_windows_setup_offline(
                    uv_available=uv_available,
                    winget_exit_code=winget_exit_code,
                    expose_uv_after_install=expose_uv_after_install,
                    uv_exit_code=uv_exit_code,
                )
                if expected_exit == "nonzero":
                    self.assertNotEqual(exit_code, 0, diagnostic)
                else:
                    self.assertEqual(exit_code, expected_exit, diagnostic)
                self.assertEqual(events, expected_events, diagnostic)

    def test_platform_setup_scripts_are_safe_and_auditable(self):
        windows = (PLUGIN_ROOT / "scripts" / "setup-windows.ps1").read_text(
            encoding="utf-8"
        )
        macos = (PLUGIN_ROOT / "scripts" / "setup-macos.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("winget install --id astral-sh.uv -e", windows)
        self.assertIn("uv --version", windows)
        self.assertIn("if ($LASTEXITCODE -ne 0)", windows)
        self.assertIn('throw "WinGet installation failed', windows)
        self.assertNotIn("exit 0", windows)
        uv_missing_branch = windows.split(
            "if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {", maxsplit=1
        )[1]
        self.assertTrue(
            "throw" in uv_missing_branch or "exit 1" in uv_missing_branch,
            "uv unavailable after installation must return a failure status",
        )
        self.assertIn("brew install uv", macos)
        self.assertIn("https://astral.sh/uv/install.sh", macos)
        self.assertIn("uv --version", macos)
        for text in (windows, macos):
            lowered = text.lower()
            executable_lines = "\n".join(
                line
                for line in text.splitlines()
                if not line.lstrip().startswith(("#", "printf "))
            )
            self.assertNotIn("tikhub_api_key", lowered)
            self.assertNotIn("setx", lowered)
            self.assertNotIn("tikhub.io", lowered)
            self.assertNotIn("executionpolicy", lowered)
            self.assertNotIn("bypass", lowered)
            self.assertNotRegex(
                executable_lines,
                r"(?im)^\s*(?:remove-item|del|erase|rd|rmdir|rm)\b",
            )
            self.assertNotRegex(
                lowered,
                r"(?i)(?:\$env:|export\s+)?(?:path|https?_proxy|all_proxy)\s*=",
            )
            self.assertNotRegex(
                lowered,
                r"(?i)setenvironmentvariable\s*\(\s*['\"]"
                r"(?:path|https?_proxy|all_proxy)['\"]",
            )
            self.assertNotRegex(
                executable_lines,
                r"(?i)\b(?:irm|invoke-restmethod|invoke-webrequest|curl|wget)\b"
                r"[^\n|]*\|\s*(?:iex|sh|bash)\b",
            )

    def test_documentation_points_to_uv_and_platform_setup_scripts(self):
        readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
        configure = (PLUGIN_ROOT / "docs" / "CONFIGURE_CODEX.md").read_text(
            encoding="utf-8"
        )
        errors = (PLUGIN_ROOT / "docs" / "ERRORS.md").read_text(encoding="utf-8")

        for text in (readme, configure, errors):
            self.assertIn("uv", text)
        self.assertIn("scripts/setup-windows.ps1", readme)
        self.assertIn("scripts/setup-macos.sh", readme)
        self.assertIn("TIKHUB_API_KEY", configure)
        self.assertNotIn("python -m pip install -r requirements.txt", configure)
