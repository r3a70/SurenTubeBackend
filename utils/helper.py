import re
from re import Pattern
from typing import Union


def extract_url_short_code(*, url: str) -> str:

    pattern: str = r"[a-zA-Z0-9-_]{11}"
    compiled_pattern: Pattern = re.compile(pattern)

    return compiled_pattern.search(url).group() if compiled_pattern.search(url) else ""


def remove_color_tags(*, input_str: str) -> str:

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    return ansi_escape.sub('', input_str).strip()


def find_chosed_formats(
    *, formats: dict, format_id: str
) -> tuple[Union[str, None], Union[str, None], Union[str, None], bool]:

    for _format in formats["formats"]:

        if _format["format_id"] == format_id:

            return (
                _format["format_id"], _format["ext"], _format["need_audio"]
            )

    return None, None, None
