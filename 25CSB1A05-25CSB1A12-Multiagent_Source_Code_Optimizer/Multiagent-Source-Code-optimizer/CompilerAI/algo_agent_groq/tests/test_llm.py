import unittest
from unittest.mock import patch

from algo_agent.llm import APIError, GroqClient, _extract_json


class FakeResponse:
    status_code = 200

    def json(self):
        return {
            "choices": [{
                "message": {
                    "content": '{"optimized_code":"print(1)"}'
                }
            }]
        }


class FakeHTTPClient:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, *args, **kwargs):
        self.request_args = args
        self.request_kwargs = kwargs
        return FakeResponse()


class GroqClientTests(unittest.TestCase):
    def test_extracts_json(self):
        self.assertEqual(
            _extract_json('```json\\n{"ok": true}\\n```'),
            {"ok": True},
        )

    def test_parses_groq_response(self):
        with patch("algo_agent.llm.httpx.Client", FakeHTTPClient):
            client = GroqClient(api_key="test-key")
            data = client.generate_json("system", "user")
        self.assertEqual(data["optimized_code"], "print(1)")

    def test_missing_api_key_is_clear_error(self):
        with patch("algo_agent.llm._load_dotenv", lambda: None):
            with patch.dict("os.environ", {"GROQ_API_KEY": ""}, clear=False):
                client = GroqClient(api_key="")
                with self.assertRaisesRegex(APIError, "API key is missing"):
                    client.generate_json("system", "user")


if __name__ == "__main__":
    unittest.main()
