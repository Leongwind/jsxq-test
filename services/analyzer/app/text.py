import re
import unicodedata

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MULTI_SPACE = re.compile(r"[ \t\u00a0]+")
EXCESS_LINES = re.compile(r"\n{3,}")


def clean_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).replace("\r\n", "\n").replace("\r", "\n")
    value = CONTROL_CHARS.sub("", value)
    value = "\n".join(MULTI_SPACE.sub(" ", line).strip() for line in value.split("\n"))
    return EXCESS_LINES.sub("\n\n", value).strip()


def evidence_in_source(evidence: str, source: str) -> bool:
    needle = MULTI_SPACE.sub(" ", unicodedata.normalize("NFKC", evidence)).strip().casefold()
    haystack = MULTI_SPACE.sub(" ", unicodedata.normalize("NFKC", source)).casefold()
    return bool(needle) and needle in haystack
