"""Tests for output.py — response builders and formatters."""

from cli_anything.k_skill.output import (
    success_response,
    error_response,
    format_json,
    format_human,
    emit,
)


class TestSuccessResponse:
    """success_response envelope builder tests."""

    def test_basic_success(self):
        resp = success_response("fine-dust", {"pm10": 35})
        assert resp["skill"] == "fine-dust"
        assert resp["status"] == "success"
        assert resp["data"] == {"pm10": 35}
        assert "source" in resp["meta"]

    def test_with_response_time(self):
        resp = success_response("test", {}, response_time_ms=142.5)
        assert resp["meta"]["response_time_ms"] == 142.5

    def test_with_custom_source(self):
        resp = success_response("test", {}, source="mcp://myrealtrip")
        assert resp["meta"]["source"] == "mcp://myrealtrip"

    def test_nested_data(self):
        data = {"items": [{"name": "A"}, {"name": "B"}], "count": 2}
        resp = success_response("search", data)
        assert resp["data"]["count"] == 2
        assert len(resp["data"]["items"]) == 2


class TestErrorResponse:
    """error_response envelope builder tests."""

    def test_basic_error(self):
        resp = error_response("srt", "MISSING_DEPENDENCY", "SRTrain not found")
        assert resp["skill"] == "srt"
        assert resp["status"] == "error"
        assert resp["error"]["code"] == "MISSING_DEPENDENCY"
        assert "fix" not in resp["error"]

    def test_error_with_fix(self):
        resp = error_response(
            "srt", "MISSING_DEPENDENCY", "SRTrain not found",
            fix="pip install SRTrain",
        )
        assert resp["error"]["fix"] == "pip install SRTrain"


class TestFormatJson:
    """format_json serialization tests."""

    def test_serializes_success(self):
        resp = success_response("test", {"key": "한글"})
        result = format_json(resp)
        assert '"skill": "test"' in result
        assert '"status": "success"' in result
        assert "한글" in result

    def test_serializes_error(self):
        resp = error_response("test", "ERR", "msg")
        result = format_json(resp)
        assert '"status": "error"' in result

    def test_non_serializable_fallback(self):
        """Non-serializable objects should not crash."""
        from datetime import datetime
        resp = success_response("test", {"ts": datetime(2026, 1, 1)})
        result = format_json(resp)
        assert "2026" in result


class TestFormatHuman:
    """format_human human-readable output tests."""

    def test_error_output(self):
        resp = error_response("test", "CODE", "Something broke", fix="try again")
        result = format_human(resp)
        assert "❌" in result
        assert "CODE" in result
        assert "Something broke" in result
        assert "💡" in result

    def test_dict_data_output(self):
        resp = success_response("test", {"pm10": 35, "grade": "보통"})
        result = format_human(resp)
        assert "pm10: 35" in result
        assert "grade: 보통" in result

    def test_list_data_output(self):
        resp = success_response("test", [{"name": "A"}, {"name": "B"}, {"name": "C"}])
        result = format_human(resp)
        assert "3건" in result
        assert "A" in result

    def test_large_list_truncation(self):
        items = [{"name": f"Item{i}"} for i in range(10)]
        resp = success_response("test", items)
        result = format_human(resp)
        assert "10건" in result
        assert "외 5건" in result

    def test_response_time_display(self):
        resp = success_response("test", {}, response_time_ms=50.0, source="proxy")
        result = format_human(resp)
        assert "50.0ms" in result
