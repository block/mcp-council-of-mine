"""Extract plain text from MCP / FastMCP sampling responses.

FastMCP 3.x ``Context.sample()`` returns a ``SamplingResult`` dataclass with
``.text`` / ``.result`` / ``.history`` — not the older
``CreateMessageResult.content[0].text`` shape. Call sites that only know the
legacy shape fall through to ``str(response)`` and store dumps like::

    SamplingResult(text='', result='', history=[...])

as if they were member opinions. This module understands both shapes.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from mcp_council_of_mine.security import safe_extract_text

logger = logging.getLogger(__name__)

# Token budgets for ctx.sample(). Reasoning hosts (high thinking effort) often
# spend low caps on chain-of-thought and return empty visible text; keep these
# high enough for short opinions/votes on modern models.
OPINION_MAX_TOKENS = 1024
VOTE_MAX_TOKENS = 512
SYNTHESIS_MAX_TOKENS = 1024


def _text_from_content_block(block: Any) -> str | None:
    """Pull text from a single content block (object or dict)."""
    if block is None:
        return None
    if hasattr(block, "text"):
        value = getattr(block, "text", None)
        if isinstance(value, str) and value.strip():
            return value
    if isinstance(block, dict):
        value = block.get("text")
        if isinstance(value, str) and value.strip():
            return value
    if isinstance(block, str) and block.strip():
        return block
    return None


def _text_from_content(content: Any) -> str | None:
    """Pull text from CreateMessageResult-style ``content`` (list or single)."""
    if content is None:
        return None
    if isinstance(content, (list, tuple)):
        for item in content:
            text = _text_from_content_block(item)
            if text:
                return text
        return None
    return _text_from_content_block(content)


def _text_from_history(history: Any) -> str | None:
    """Last-resort: last assistant message text in SamplingResult.history."""
    if not history:
        return None
    try:
        for message in reversed(list(history)):
            role = getattr(message, "role", None)
            if role is None and isinstance(message, dict):
                role = message.get("role")
            if role not in ("assistant", "model"):
                continue
            content = getattr(message, "content", None)
            if content is None and isinstance(message, dict):
                content = message.get("content")
            text = _text_from_content(content)
            if text:
                return text
    except (TypeError, AttributeError) as exc:
        logger.debug("history walk failed: %s", exc)
    return None


def _regex_text_fallback(blob: str) -> str | None:
    """Legacy string-repr scrape used when structured fields are unavailable."""
    content_str = safe_extract_text(blob)
    match = re.search(
        r"text='(.+?)'(?:\s+annotations=|\s+meta=|$)",
        content_str,
        re.DOTALL,
    )
    if not match:
        match = re.search(
            r'text="(.+?)"(?:\s+annotations=|\s+meta=|$)',
            content_str,
            re.DOTALL,
        )
    if not match:
        return None
    text = match.group(1)
    return text.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')


def extract_text_from_response(response: Any) -> str:
    """Extract plain text from any sampling response format.

    Order of preference:
    1. FastMCP 3 ``SamplingResult.text`` / non-empty string ``.result``
    2. Legacy ``CreateMessageResult.content`` (list or single block)
    3. Plain string response
    4. Assistant text from ``SamplingResult.history``
    5. Regex scrape of content-block repr (legacy)
    6. Empty string — never ``str(SamplingResult(...))`` dumps
    """
    if response is None:
        return ""

    try:
        # 1) FastMCP 3 SamplingResult
        text = getattr(response, "text", None)
        if isinstance(text, str) and text.strip():
            return text

        result = getattr(response, "result", None)
        if isinstance(result, str) and result.strip():
            return result

        # 2) Legacy CreateMessageResult / dict with content
        content = getattr(response, "content", None)
        if content is None and isinstance(response, dict):
            content = response.get("content")
            # dict-shaped SamplingResult
            dict_text = response.get("text")
            if isinstance(dict_text, str) and dict_text.strip():
                return dict_text
            dict_result = response.get("result")
            if isinstance(dict_result, str) and dict_result.strip():
                return dict_result

        extracted = _text_from_content(content)
        if extracted:
            return extracted

        # 3) Bare string from some handlers
        if isinstance(response, str) and response.strip():
            # Avoid treating a SamplingResult repr as a successful opinion
            if response.lstrip().startswith("SamplingResult("):
                return ""
            return response

        # 4) History fallback (assistant turns only)
        history = getattr(response, "history", None)
        if history is None and isinstance(response, dict):
            history = response.get("history")
        extracted = _text_from_history(history)
        if extracted:
            return extracted

        # 5) Regex on content item / response repr (legacy path only when
        #    content existed but lacked .text attribute)
        if content is not None:
            scraped = _regex_text_fallback(str(content))
            if scraped and scraped.strip():
                return scraped

        # 6) Empty — do NOT return str(response); that reintroduces the bug
        return ""

    except (AttributeError, KeyError, IndexError, TypeError) as exc:
        logger.warning("Failed to extract text from response: %s", exc)
        return ""
