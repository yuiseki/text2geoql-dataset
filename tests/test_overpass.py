"""Tests for overpass.py — mocking httpx to avoid real network calls."""

from unittest.mock import MagicMock, patch

from overpass import fetch_elements, count_elements, DEFAULT_ENDPOINT


class TestFetchElements:
    def test_returns_elements_on_success(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "elements": [{"type": "node", "id": 1}, {"type": "way", "id": 2}]
        }
        with patch("overpass.httpx.get", return_value=mock_response) as mock_get:
            result = fetch_elements("[out:json];node[name='Tokyo'];out;")
        assert result == [{"type": "node", "id": 1}, {"type": "way", "id": 2}]
        mock_get.assert_called_once()

    def test_returns_empty_list_on_http_error(self) -> None:
        with patch("overpass.httpx.get", side_effect=Exception("connection refused")):
            result = fetch_elements("[out:json];node;out;")
        assert result == []

    def test_returns_empty_list_on_missing_elements_key(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"version": 0.6}
        with patch("overpass.httpx.get", return_value=mock_response):
            result = fetch_elements("[out:json];node;out;")
        assert result == []

    def test_uses_default_endpoint(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"elements": []}
        with patch("overpass.httpx.get", return_value=mock_response) as mock_get:
            fetch_elements("query")
        args, kwargs = mock_get.call_args
        assert args[0] == DEFAULT_ENDPOINT

    def test_uses_custom_endpoint(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"elements": []}
        with patch("overpass.httpx.get", return_value=mock_response) as mock_get:
            fetch_elements("query", endpoint="https://example.com/api")
        args, kwargs = mock_get.call_args
        assert args[0] == "https://example.com/api"


class TestCountElements:
    def test_returns_count(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"elements": [{}, {}, {}]}
        with patch("overpass.httpx.get", return_value=mock_response):
            assert count_elements("query") == 3

    def test_returns_zero_on_empty(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"elements": []}
        with patch("overpass.httpx.get", return_value=mock_response):
            assert count_elements("query") == 0

    def test_returns_zero_on_error(self) -> None:
        with patch("overpass.httpx.get", side_effect=Exception("timeout")):
            assert count_elements("query") == 0
