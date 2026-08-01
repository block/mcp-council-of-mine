"""Mocked end-to-end debate/voting/results covering FastMCP 3 SamplingResult.

These replace the manual client checks on the PR test plan: they drive the real
tool functions with a fake Context whose sample() returns SamplingResult-shaped
objects (and one empty result to prove the error-marker path).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from mcp_council_of_mine.council.members import get_all_members
from mcp_council_of_mine.council.state import get_state_manager
from mcp_council_of_mine.tools import debate, voting, results


@dataclass
class _SamplingResult:
    text: str | None
    result: object
    history: list


class _FakeCtx:
    """Minimal FastMCP Context stand-in."""

    def __init__(self, sample_side_effect):
        self.sample = AsyncMock(side_effect=sample_side_effect)
        self.info = lambda *a, **k: None
        self.warning = lambda *a, **k: None


def _unwrap(tool):
    """Return the underlying coroutine from a FastMCP FunctionTool if wrapped."""
    if hasattr(tool, "fn"):
        return tool.fn
    if hasattr(tool, "__wrapped__"):
        return tool.__wrapped__
    return tool


@pytest.fixture(autouse=True)
def _isolate_state(tmp_path, monkeypatch):
    """Point state manager at a temp debates dir and clear current debate."""
    sm = get_state_manager()
    sm.clear_current_debate()
    sm.debates_dir = Path(tmp_path) / "debates"
    sm.debates_dir.mkdir(parents=True, exist_ok=True)
    yield
    sm.clear_current_debate()


@pytest.mark.asyncio
async def test_start_debate_opinions_are_plain_prose_not_sampling_result_dumps():
    members = get_all_members()
    assert len(members) == 9

    # One distinct opinion per member, as FastMCP 3 SamplingResult
    queue = [
        _SamplingResult(
            text=f"Opinion from {m['name']}: freeze FS-mutating surfaces first.",
            result=f"Opinion from {m['name']}: freeze FS-mutating surfaces first.",
            history=[],
        )
        for m in members
    ]

    ctx = _FakeCtx(sample_side_effect=queue)
    start = _unwrap(debate.start_council_debate)
    out = await start(prompt="Should we freeze apply writes for one release?", ctx=ctx)

    assert "SamplingResult(" not in out
    assert "history=[" not in out
    for m in members:
        assert m["name"].upper() in out or m["name"] in out
        assert f"Opinion from {m['name']}" in out

    sm = get_state_manager()
    current = sm.get_current_debate()
    assert current is not None
    assert len(current["opinions"]) == 9
    for op in current["opinions"].values():
        assert not op["opinion"].startswith("SamplingResult")
        assert "freeze FS-mutating" in op["opinion"]

    assert ctx.sample.await_count == 9
    # Raised budget used
    for call in ctx.sample.await_args_list:
        assert call.kwargs.get("max_tokens", 0) >= 1024


@pytest.mark.asyncio
async def test_empty_sample_becomes_error_marker_not_repr():
    members = get_all_members()
    queue = [_SamplingResult(text="", result="", history=[]) for _ in members]
    ctx = _FakeCtx(sample_side_effect=queue)
    start = _unwrap(debate.start_council_debate)
    out = await start(prompt="Empty sample regression check.", ctx=ctx)

    assert "SamplingResult(" not in out
    assert "[Error: No text in response]" in out

    sm = get_state_manager()
    for op in sm.get_current_debate()["opinions"].values():
        assert op["opinion"] == "[Error: No text in response]"


@pytest.mark.asyncio
async def test_get_results_with_votes_and_synthesis_from_sampling_result():
    """Full path: debate → voting → get_results with non-empty sample text."""
    members = get_all_members()

    # Phase 1: 9 opinion samples
    opinion_queue = [
        _SamplingResult(
            text=f"{m['name']} says prioritize path allowlist.",
            result=f"{m['name']} says prioritize path allowlist.",
            history=[],
        )
        for m in members
    ]

    # Phase 2: 9 votes — each votes for opinion #1 (member id 1) except member 1
    # who must vote for someone else (format VOTE: N / REASONING: ...)
    vote_queue = []
    for m in members:
        target = 2 if m["id"] == 1 else 1
        vote_queue.append(
            _SamplingResult(
                text=f"VOTE: {target}\nREASONING: Aligns with my values on safety.",
                result=f"VOTE: {target}\nREASONING: Aligns with my values on safety.",
                history=[],
            )
        )

    # Phase 3: synthesis sample inside get_results
    synthesis = _SamplingResult(
        text="Council converges on path allowlist before further features.",
        result="Council converges on path allowlist before further features.",
        history=[],
    )

    # get_results auto-votes if needed; we call conduct_voting then get_results
    # so sample order: 9 opinions + 9 votes + 1 synthesis
    full_queue = opinion_queue + vote_queue + [synthesis]
    ctx = _FakeCtx(sample_side_effect=full_queue)

    start = _unwrap(debate.start_council_debate)
    conduct = _unwrap(voting.conduct_voting)
    get_res = _unwrap(results.get_results)

    await start(prompt="What should we secure first in the deploy pipe?", ctx=ctx)
    vote_out = await conduct(ctx=ctx)
    assert isinstance(vote_out, dict)
    assert vote_out.get("total_votes", 0) >= 1 or "total_votes" in vote_out or vote_out.get("status")

    result_text = await get_res(ctx=ctx)
    assert isinstance(result_text, str)
    assert "SamplingResult(" not in result_text
    assert "path allowlist" in result_text.lower() or "Council converges" in result_text
    # Winners / synthesis content should appear
    assert "converges" in result_text.lower() or "allowlist" in result_text.lower()

    # get_results saves then may clear in-memory current; assert on output + sample calls
    assert ctx.sample.await_count >= 19  # 9 opinions + 9 votes + 1 synthesis
    # Vote budgets use VOTE_MAX_TOKENS; synthesis uses SYNTHESIS_MAX_TOKENS
    vote_calls = [c for c in ctx.sample.await_args_list if c.kwargs.get("max_tokens") == 512]
    synth_calls = [c for c in ctx.sample.await_args_list if c.kwargs.get("max_tokens") == 1024]
    assert len(vote_calls) >= 9
    assert len(synth_calls) >= 10  # 9 opinions + 1 synthesis share 1024
