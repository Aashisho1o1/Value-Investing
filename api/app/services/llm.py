from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import Settings
from app.models import (
    MEMO_SECTION_TITLES,
    SCORECARD_LABELS,
    AnalyzeResponse,
    Citation,
    EvidenceChunk,
    MemoParagraph,
    MemoSection,
    MetricSeries,
    ScorecardItem,
)


class LLMValidationError(ValueError):
    pass


def empty_memo_sections() -> dict[str, MemoSection]:
    return {
        key: MemoSection(key=key, title=title, paragraphs=[])
        for key, title in MEMO_SECTION_TITLES.items()
    }


def _extract_json(value: str) -> dict[str, Any]:
    content = value.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?", "", content).strip()
        content = re.sub(r"```$", "", content).strip()
    return json.loads(content)


def _normalize_number_string(value: str) -> str:
    return value.replace("$", "").replace(",", "").strip().lower()


def _allowed_numeric_tokens(metrics: list[MetricSeries], filing_date: str) -> set[str]:
    allowed: set[str] = {filing_date[:4]}
    for metric in metrics:
        for point in metric.points:
            allowed.add(point.fiscal_year)
            if point.value is None:
                continue
            raw = float(point.value)
            allowed.add(str(int(raw)) if raw.is_integer() else f"{raw:.2f}")
            allowed.add(f"{raw:.1f}")
            allowed.add(f"{raw:,.0f}")
            if abs(raw) >= 1_000_000_000:
                allowed.add(f"{raw / 1_000_000_000:.1f}b")
            if abs(raw) >= 1_000_000:
                allowed.add(f"{raw / 1_000_000:.1f}m")
    return {_normalize_number_string(token) for token in allowed}


def _validate_numeric_claims(text: str, allowed_tokens: set[str]) -> None:
    for token in re.findall(r"(?<!\w)\$?\d[\d,.]*%?", text):
        normalized = _normalize_number_string(token.rstrip("%"))
        if len(normalized) <= 1:
            continue
        if normalized.isdigit() and 1900 <= int(normalized) <= 2100:
            continue
        if normalized not in allowed_tokens:
            raise LLMValidationError(f"Model used unsupported numeric claim: {token}")


def validate_model_payload(
    payload: dict[str, Any],
    evidence_lookup: dict[str, EvidenceChunk],
    metrics: list[MetricSeries],
    filing_date: str,
) -> tuple[dict[str, MemoSection], list[ScorecardItem], dict[str, Citation]]:
    sections = payload.get("sections")
    scorecard = payload.get("scorecard")

    if not isinstance(sections, dict):
        raise LLMValidationError("Model response did not include sections")
    if not isinstance(scorecard, list):
        raise LLMValidationError("Model response did not include scorecard")

    allowed_numbers = _allowed_numeric_tokens(metrics, filing_date)
    memo_sections: dict[str, MemoSection] = {}
    citations: dict[str, Citation] = {}
    citation_id_by_chunk: dict[str, str] = {}
    paragraph_counter = 1

    for key, title in MEMO_SECTION_TITLES.items():
        entries = sections.get(key, [])
        if not isinstance(entries, list):
            raise LLMValidationError(f"Section {key} is not a list")

        paragraphs: list[MemoParagraph] = []
        for entry in entries:
            text = entry.get("text", "").strip()
            chunk_ids = entry.get("citation_chunk_ids", [])
            if not text:
                continue
            if not chunk_ids:
                raise LLMValidationError(f"Section {key} contains uncited narrative text")
            if not isinstance(chunk_ids, list):
                raise LLMValidationError(f"Section {key} citations are invalid")
            _validate_numeric_claims(text, allowed_numbers)
            inline_ids: list[str] = []
            for chunk_id in chunk_ids:
                if chunk_id not in evidence_lookup:
                    raise LLMValidationError(f"Unknown chunk id: {chunk_id}")
                citation_id = citation_id_by_chunk.get(chunk_id)
                if citation_id is None:
                    citation_id = f"c{len(citation_id_by_chunk) + 1}"
                    citation_id_by_chunk[chunk_id] = citation_id
                    chunk = evidence_lookup[chunk_id]
                    citations[citation_id] = Citation(
                        id=citation_id,
                        chunk_id=chunk_id,
                        section=chunk.section,
                        snippet=chunk.snippet,
                        source_url=chunk.source_url,
                    )
                inline_ids.append(citation_id)
            paragraphs.append(
                MemoParagraph(
                    id=f"p{paragraph_counter}",
                    text=text,
                    citation_ids=inline_ids,
                )
            )
            paragraph_counter += 1

        memo_sections[key] = MemoSection(key=key, title=title, paragraphs=paragraphs)

    validated_scorecard: list[ScorecardItem] = []
    seen_keys: set[str] = set()
    for entry in scorecard:
        key = entry.get("key")
        if key not in SCORECARD_LABELS:
            raise LLMValidationError(f"Unexpected scorecard key: {key}")
        score = entry.get("score")
        if score not in {1, 2, 3, 4, 5}:
            raise LLMValidationError(f"Invalid score for {key}")
        rationale = entry.get("rationale", "").strip()
        chunk_ids = entry.get("citation_chunk_ids", [])
        if not rationale or not chunk_ids:
            raise LLMValidationError(f"Scorecard item {key} is not cited")
        _validate_numeric_claims(rationale, allowed_numbers)
        citation_ids: list[str] = []
        for chunk_id in chunk_ids:
            if chunk_id not in evidence_lookup:
                raise LLMValidationError(f"Unknown scorecard chunk id: {chunk_id}")
            citation_id = citation_id_by_chunk.get(chunk_id)
            if citation_id is None:
                citation_id = f"c{len(citation_id_by_chunk) + 1}"
                citation_id_by_chunk[chunk_id] = citation_id
                chunk = evidence_lookup[chunk_id]
                citations[citation_id] = Citation(
                    id=citation_id,
                    chunk_id=chunk_id,
                    section=chunk.section,
                    snippet=chunk.snippet,
                    source_url=chunk.source_url,
                )
            citation_ids.append(citation_id)
        validated_scorecard.append(
            ScorecardItem(
                key=key,
                label=SCORECARD_LABELS[key],
                score=score,
                rationale=rationale,
                citation_ids=citation_ids,
            )
        )
        seen_keys.add(key)

    missing_keys = set(SCORECARD_LABELS) - seen_keys
    if missing_keys:
        raise LLMValidationError(f"Missing scorecard keys: {sorted(missing_keys)}")

    return memo_sections, validated_scorecard, citations


class DeepSeekClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return bool(self.settings.deepseek_api_key)

    def generate_report(
        self,
        company: dict[str, Any],
        filing: dict[str, Any],
        metrics_summary: dict[str, Any],
        warnings: list[str],
        themed_chunks: dict[str, list[EvidenceChunk]],
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        prompt_payload = {
            "company": company,
            "filing": filing,
            "metrics": metrics_summary,
            "warnings": warnings,
            "retrieved_evidence": {
                theme: [
                    {
                        "chunk_id": chunk.chunk_id,
                        "section": chunk.section,
                        "snippet": chunk.snippet,
                    }
                    for chunk in chunks
                ]
                for theme, chunks in themed_chunks.items()
            },
            "required_sections": list(MEMO_SECTION_TITLES.keys()),
            "required_scorecard_keys": list(SCORECARD_LABELS.keys()),
        }

        system_prompt = (
            "You are a conservative investment research assistant. "
            "Use only the supplied filing evidence and deterministic metrics. "
            "Do not give investment advice. Do not invent facts. "
            "Every paragraph and every score rationale must cite chunk ids from the provided evidence. "
            "If a point is unclear, say that it is not clear from the filing. "
            "Return JSON with this shape: "
            "{\"sections\": {section_key: [{\"text\": string, \"citation_chunk_ids\": [chunk_id]}]}, "
            "\"scorecard\": [{\"key\": string, \"score\": 1-5, \"rationale\": string, "
            "\"citation_chunk_ids\": [chunk_id]}]}. "
            "Avoid explicit numbers unless they appear in the provided metric summary."
        )

        response = httpx.post(
            f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.settings.deepseek_model,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(prompt_payload)},
                ],
                "temperature": 0.2,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        return _extract_json(content)

