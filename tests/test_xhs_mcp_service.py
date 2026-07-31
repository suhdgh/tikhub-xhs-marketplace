import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "tikhub-xhs-mcp"
sys.path.insert(0, str(PLUGIN_ROOT))

from xhs_mcp_service import XhsMcpService, XhsMcpToolError, redact_sensitive_text
from xiaohongshu_tikhub import TikHubAPIError


class FakeClient:
    def __init__(self, *, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []
        for resource_name in ("app", "app_v2", "web", "web_v2", "web_v3"):
            setattr(self, resource_name, FakeResource(self, resource_name))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakeResource:
    def __init__(self, client, resource_name):
        self._client = client
        self._resource_name = resource_name

    def __getattr__(self, method_name):
        def invoke(**params):
            self._client.calls.append((self._resource_name, method_name, params))
            if self._client.error:
                raise self._client.error
            return self._client.response

        return invoke


class XhsMcpServiceConfigurationTests(unittest.TestCase):
    def test_missing_key_reports_configuration_required_without_creating_client(self):
        def unexpected_client_factory(*args, **kwargs):
            raise AssertionError("missing key must prevent client creation")

        service = XhsMcpService(None, client_factory=unexpected_client_factory, version="1.0.0")

        self.assertEqual(service.xhs_status()["status"], "configuration_required")
        self.assertFalse(service.xhs_status()["api_key_configured"])
        self.assertEqual(service.xhs_list_endpoints()["endpoint_count"], 79)
        with self.assertRaisesRegex(XhsMcpToolError, "TIKHUB_API_KEY"):
            service.xhs_get_hot_list()

    def test_whitespace_key_is_treated_as_unconfigured(self):
        service = XhsMcpService("  ")

        self.assertEqual(service.xhs_status()["status"], "configuration_required")


class XhsMcpServiceBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.clients = []

        def client_factory(api_key):
            client = FakeClient(response={"ok": True, "api_key": api_key})
            self.clients.append(client)
            return client

        self.service = XhsMcpService("test-key", client_factory=client_factory, version="2.0.0")

    def test_ready_status_and_convenience_methods_preserve_parameter_mappings(self):
        self.assertEqual(
            self.service.xhs_status(),
            {"status": "ready", "version": "2.0.0", "endpoint_count": 79, "api_key_configured": True},
        )
        self.service.xhs_search_notes("coffee", page=3)
        self.service.xhs_get_note("note-1", "token-1")
        self.service.xhs_get_note_comments("note-2", "token-2", cursor="cursor-2")
        self.service.xhs_get_user("user-1", "token-3")
        self.service.xhs_get_user_notes("user-2", "token-4", cursor="cursor-4")
        self.service.xhs_get_hot_list()

        self.assertEqual(
            [call for client in self.clients for call in client.calls],
            [
                ("app_v2", "search_notes", {"keyword": "coffee", "page": 3}),
                ("web_v3", "fetch_note_detail", {"note_id": "note-1", "xsec_token": "token-1", "xsec_source": "pc_search"}),
                ("web_v3", "fetch_note_comments", {"note_id": "note-2", "xsec_token": "token-2", "xsec_source": "pc_search", "cursor": "cursor-2"}),
                ("web_v3", "fetch_user_info", {"user_id": "user-1", "xsec_token": "token-3", "xsec_source": "pc_search"}),
                ("web_v3", "fetch_user_notes", {"user_id": "user-2", "xsec_token": "token-4", "xsec_source": "pc_search", "cursor": "cursor-4"}),
                ("web_v3", "fetch_hot_list", {}),
            ],
        )

    def test_unregistered_url_shaped_endpoint_is_rejected_before_client_creation(self):
        with self.assertRaisesRegex(XhsMcpToolError, "endpoint|未登记"):
            self.service.xhs_call("https://api.tikhub.io/api/v1/xiaohongshu/web_v3/fetch_hot_list")

        self.assertEqual(self.clients, [])

    def test_generic_call_rejects_reserved_transport_and_credential_params_before_client_creation(self):
        for reserved_name in ("headers", "authorization", "api_key", "tikhub_api_key"):
            with self.subTest(reserved_name=reserved_name):
                with self.assertRaisesRegex(XhsMcpToolError, "保留参数|不允许"):
                    self.service.xhs_call(
                        "app_v2.search_notes",
                        {reserved_name: "caller-controlled-value", "keyword": "coffee"},
                    )

        self.assertEqual(self.clients, [])

    def test_generic_call_keeps_xsec_token_and_share_link_parameters_available(self):
        self.service.xhs_call(
            "app.extract_share_info",
            {
                "share_link": "https://www.xiaohongshu.com/explore/example",
                "xsec_token": "public-share-token",
            },
        )

        self.assertEqual(
            self.clients[0].calls,
            [
                (
                    "app",
                    "extract_share_info",
                    {
                        "share_link": "https://www.xiaohongshu.com/explore/example",
                        "xsec_token": "public-share-token",
                    },
                )
            ],
        )

    def test_api_errors_provide_user_owned_key_and_actionable_status_guidance(self):
        expectations = {
            401: "自己的 TikHub API Key",
            402: "余额不足",
            403: "请勿连续重试",
            404: "更新此插件",
        }
        for status_code, expected_hint in expectations.items():
            with self.subTest(status_code=status_code):
                def client_factory(api_key, status_code=status_code):
                    return FakeClient(error=TikHubAPIError("request failed", status_code=status_code))

                service = XhsMcpService("test-key", client_factory=client_factory)
                with self.assertRaisesRegex(XhsMcpToolError, expected_hint) as context:
                    service.xhs_get_hot_list()
                self.assertIn("web_v3.fetch_hot_list", str(context.exception))

    def test_402_error_redacts_caller_and_response_secrets(self):
        def client_factory(api_key):
            return FakeClient(
                error=TikHubAPIError(
                    "api_key=response-api-key-secret authorization=Bearer test-key",
                    status_code=402,
                )
            )

        service = XhsMcpService("test-key", client_factory=client_factory)
        with self.assertRaises(XhsMcpToolError) as context:
            service.xhs_get_hot_list()

        self.assertNotIn("test-key", str(context.exception))
        self.assertNotIn("response-api-key-secret", str(context.exception))
        self.assertIn("[REDACTED]", str(context.exception))

    def test_request_log_omits_key_and_parameters(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "requests.jsonl"
            service = XhsMcpService(
                "test-key",
                client_factory=lambda api_key: FakeClient(response={"ok": True}),
                request_log_path=log_path,
            )

            service.xhs_call("app_v2.search_notes", {"keyword": "private-search-term", "token": "param-secret"})

            record = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(record["endpoint"], "app_v2.search_notes")
            self.assertEqual(record["status"], "success")
            self.assertIn("timestamp", record)
            self.assertEqual(set(record), {"timestamp", "endpoint", "status"})
            raw_record = log_path.read_text(encoding="utf-8")
            self.assertNotIn("test-key", raw_record)
            self.assertNotIn("private-search-term", raw_record)
            self.assertNotIn("param-secret", raw_record)

    def test_redact_sensitive_text_removes_authorization_and_named_secrets(self):
        redacted = redact_sensitive_text(
            "Authorization: Bearer bearer-secret api_key=named-secret token: token-secret",
            api_key="caller-key",
        )

        self.assertNotIn("bearer-secret", redacted)
        self.assertNotIn("named-secret", redacted)
        self.assertNotIn("token-secret", redacted)
