"""Unit tests for FastMCP 3 SamplingResult + legacy response text extraction."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from mcp_council_of_mine.response_text import (
    OPINION_MAX_TOKENS,
    SYNTHESIS_MAX_TOKENS,
    VOTE_MAX_TOKENS,
    extract_text_from_response,
)


@dataclass
class _FakeSamplingResult:
    """Minimal stand-in for fastmcp.server.sampling.run.SamplingResult."""

    text: str | None
    result: object
    history: list


class _TextBlock:
    def __init__(self, text: str) -> None:
        self.text = text
        self.type = "text"


def test_fastmcp_sampling_result_text():
    resp = _FakeSamplingResult(text="Ship the allowlist first.", result="Ship the allowlist first.", history=[])
    assert extract_text_from_response(resp) == "Ship the allowlist first."


def test_fastmcp_sampling_result_result_fallback_when_text_empty():
    resp = _FakeSamplingResult(text="", result="Use result field.", history=[])
    assert extract_text_from_response(resp) == "Use result field."


def test_fastmcp_sampling_result_empty_does_not_dump_repr():
    """Regression: empty SamplingResult must not become str(SamplingResult(...))."""
    resp = _FakeSamplingResult(text="", result="", history=[])
    out = extract_text_from_response(resp)
    assert out == ""
    assert "SamplingResult" not in out


def test_legacy_create_message_content_list():
    resp = SimpleNamespace(content=[_TextBlock("Legacy list content.")])
    assert extract_text_from_response(resp) == "Legacy list content."


def test_legacy_create_message_content_single():
    resp = SimpleNamespace(content=_TextBlock("Legacy single content."))
    assert extract_text_from_response(resp) == "Legacy single content."


def test_dict_content_block():
    resp = SimpleNamespace(content=[{"type": "text", "text": "Dict block."}])
    assert extract_text_from_response(resp) == "Dict block."


def test_plain_string():
    assert extract_text_from_response("Just a string.") == "Just a string."


def test_sampling_result_repr_string_rejected():
    dump = "SamplingResult(text='', result='', history=[SamplingMessage(...)])"
    assert extract_text_from_response(dump) == ""


def test_history_assistant_fallback():
    assistant = SimpleNamespace(
        role="assistant",
        content=[_TextBlock("From history assistant turn.")],
    )
    user = SimpleNamespace(role="user", content=[_TextBlock("prompt")])
    resp = _FakeSamplingResult(text="", result="", history=[user, assistant])
    assert extract_text_from_response(resp) == "From history assistant turn."


def test_history_skips_user_only():
    user = SimpleNamespace(role="user", content=[_TextBlock("only user")])
    resp = _FakeSamplingResult(text=None, result="", history=[user])
    assert extract_text_from_response(resp) == ""


def test_none_and_whitespace():
    assert extract_text_from_response(None) == ""
    assert extract_text_from_response(_FakeSamplingResult(text="   ", result="   ", history=[])) == ""


def test_dict_shaped_sampling_result():
    assert (
        extract_text_from_response({"text": "Dict SamplingResult.", "result": "", "history": []})
        == "Dict SamplingResult."
    )


def test_token_budgets_raised_for_reasoning_hosts():
    assert OPINION_MAX_TOKENS >= 1024
    assert VOTE_MAX_TOKENS >= 512
    assert SYNTHESIS_MAX_TOKENS >= 1024


def test_empty_sampling_result_becomes_error_marker_not_repr():
    """PR test-plan regression: empty sample → error marker path, never repr dump.

    Call sites use: opinion_text = extract(...) or "[Error: No text in response]"
    """
    resp = _FakeSamplingResult(text="", result="", history=[])
    extracted = extract_text_from_response(resp)
    opinion = extracted if extracted else "[Error: No text in response]"
    assert opinion == "[Error: No text in response]"
    assert "SamplingResult" not in opinion
    assert "history=" not in opinion
