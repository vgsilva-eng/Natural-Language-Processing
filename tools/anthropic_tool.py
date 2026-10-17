"""Small compatibility helpers for Anthropic message responses."""


def response_text(response) -> str:
    """Join text blocks while ignoring thinking and other block types."""
    parts = [
        text.strip()
        for block in response.content
        if (text := getattr(block, "text", None))
    ]
    if not parts:
        raise ValueError("Anthropic response did not contain a text block.")
    return "\n".join(parts)
