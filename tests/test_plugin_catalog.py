import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "tikhub-xhs-mcp"


class PluginCatalogTests(unittest.TestCase):
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
        self.assertEqual(manifest["skills"], ["./skills/tikhub-xhs-setup"])
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
        self.assertNotIn("ExecutionPolicy", setup_skill)
        self.assertNotIn("ByPass", setup_skill)
        self.assertNotIn("TIKHUB_API_KEY=", setup_skill)

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
            self.assertNotIn("TIKHUB_API_KEY", text)
            self.assertNotIn("setx", text.lower())
            self.assertNotIn("export tikhub_api_key", text.lower())
            self.assertNotIn("tikhub.io", text.lower())

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
