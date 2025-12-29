from __future__ import annotations


def truncate_title(value: object, max_len: int = 18, ellipsis: str = "…") -> str:
    """
    Truncate a value for UI titles (e.g. subplot titles) to a maximum length.

    Args:
        value: Any value convertible to string. None becomes "".
        max_len: Maximum length of the returned string (including ellipsis).
        ellipsis: The truncation marker to append when truncating.

    Returns:
        A string of length <= max_len.
    """
    if value is None:
        return ""
    s = str(value)
    if max_len <= 0:
        return ""
    if len(s) <= max_len:
        return s
    if max_len == 1:
        return ellipsis[:1]
    return s[: max_len - 1] + ellipsis


