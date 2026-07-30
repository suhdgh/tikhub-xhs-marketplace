import sys
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "tikhub-xhs-mcp"
CLIENT_PATH = PLUGIN_ROOT / "xiaohongshu_tikhub.py"
sys.path.insert(0, str(PLUGIN_ROOT))

from xiaohongshu_tikhub import ENDPOINTS, TikHubAPIError, TikHubXiaohongshuClient


class FakeResponse:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def getcode(self):
        return self.status

    def read(self):
        return self.body


class RecordingOpener:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append(request)
        return FakeResponse(self.body, self.status)


class TikHubClientPackagingTests(unittest.TestCase):
    def test_public_plugin_contains_the_xiaohongshu_client(self):
        self.assertTrue(CLIENT_PATH.is_file())

    def test_endpoint_registry_has_all_79_allowlisted_entries(self):
        self.assertEqual(sum(len(group) for group in ENDPOINTS.values()), 79)
        self.assertEqual(
            ENDPOINTS["web_v3"]["fetch_note_detail"],
            ("GET", "/api/v1/xiaohongshu/web_v3/fetch_note_detail"),
        )
        self.assertEqual(
            ENDPOINTS["web"]["get_note_info_v5"],
            ("POST", "/api/v1/xiaohongshu/web/get_note_info_v5"),
        )

    def test_get_and_post_emit_expected_tikhub_transport(self):
        opener = RecordingOpener(b'{"code": 200}')
        client = TikHubXiaohongshuClient("test-key", opener=opener)

        client.app_v2.search_notes(keyword="鎶よ偆", page=2)
        get_request = opener.requests[-1]
        self.assertEqual(
            parse_qs(urlparse(get_request.full_url).query),
            {"keyword": ["鎶よ偆"], "page": ["2"]},
        )
        self.assertEqual(get_request.get_header("Authorization"), "Bearer test-key")

        client.web.get_note_info_v5(note_id="note-1")
        post_request = opener.requests[-1]
        self.assertEqual(post_request.get_method(), "POST")
        self.assertEqual(post_request.data, b'{"note_id": "note-1"}')

    def test_non_2xx_response_raises_tikhub_api_error(self):
        client = TikHubXiaohongshuClient(
            "test-key", opener=RecordingOpener(b'{"error": "unavailable"}', status=503)
        )

        with self.assertRaises(TikHubAPIError) as context:
            client.app.get_note_info(note_id="note-1")

        self.assertEqual(context.exception.status_code, 503)

    def test_invalid_json_response_raises_tikhub_api_error(self):
        client = TikHubXiaohongshuClient("test-key", opener=RecordingOpener(b"not-json"))

        with self.assertRaises(TikHubAPIError) as context:
            client.app.get_note_info(note_id="note-1")

        self.assertEqual(context.exception.response_body, "not-json")
