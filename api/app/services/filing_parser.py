from __future__ import annotations

import re
from typing import Iterable

from bs4 import BeautifulSoup

from app.models import EvidenceChunk


SECTION_PATTERNS = [
    ("Business", re.compile(r"\bitem\s+1\.?\s+business\b", re.IGNORECASE)),
    ("Risk Factors", re.compile(r"\bitem\s+1a\.?\s+risk factors\b", re.IGNORECASE)),
    (
        "MD&A",
        re.compile(
            r"\bitem\s+7\.?\s+management(?:['’]s)? discussion and analysis\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Financial Statements",
        re.compile(r"\bitem\s+8\.?\s+financial statements\b", re.IGNORECASE),
    ),
]


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def locate_sections(text: str) -> dict[str, str]:
    if not text:
        return {}

    threshold = int(len(text) * 0.05)
    starts: list[tuple[str, int]] = []
    last_start = 0

    for label, pattern in SECTION_PATTERNS:
        candidates = [match.start() for match in pattern.finditer(text) if match.start() >= max(threshold, last_start)]
        if not candidates:
            candidates = [match.start() for match in pattern.finditer(text) if match.start() >= last_start]
        if not candidates:
            continue
        start = candidates[0]
        starts.append((label, start))
        last_start = start + 1

    sections: dict[str, str] = {}
    for index, (label, start) in enumerate(starts):
        end = starts[index + 1][1] if index + 1 < len(starts) else len(text)
        section_text = text[start:end].strip()
        if section_text:
            sections[label] = section_text
    return sections


def _split_long_paragraph(paragraph: str, max_chars: int = 650) -> Iterable[str]:
    if len(paragraph) <= max_chars:
        yield paragraph
        return

    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
            continue
        if current:
            yield current
        current = sentence.strip()
    if current:
        yield current


def chunk_sections(sections: dict[str, str], source_url: str) -> list[EvidenceChunk]:
    chunks: list[EvidenceChunk] = []
    for section_name, section_text in sections.items():
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", section_text) if part.strip()]
        index = 1
        for paragraph in paragraphs:
            normalized = re.sub(r"\s+", " ", paragraph).strip()
            if len(normalized) < 80:
                continue
            for snippet in _split_long_paragraph(normalized):
                if len(snippet) < 80:
                    continue
                chunk_id = f"{section_name.lower().replace(' ', '_')}-{index:03d}"
                chunks.append(
                    EvidenceChunk(
                        chunk_id=chunk_id,
                        section=section_name,
                        snippet=snippet,
                        source_url=source_url,
                        rank=0.0,
                        topics=[section_name.lower().replace(" ", "_")],
                    )
                )
                index += 1
    return chunks


def parse_filing_html(html: str, source_url: str) -> tuple[dict[str, str], list[EvidenceChunk]]:
    text = html_to_text(html)
    sections = locate_sections(text)
    return sections, chunk_sections(sections, source_url)

