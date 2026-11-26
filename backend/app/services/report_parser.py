"""Deterministic lab marker parser and Markdown report exporter."""

import re
from typing import Any, Dict, List

MARKER_WITH_RANGE_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9\s/().,%-]{2,50}?)\s*[:\-]?\s+"
    r"(?P<value>-?\d+(?:\.\d+)?)\s*"
    r"(?P<unit>[a-zA-Z/%*^0-9._-]{0,18})\s*"
    r"(?:\(|\[|Ref[:\s]*)?"
    r"(?P<low>-?\d+(?:\.\d+)?)\s*(?:-|to|–)\s*(?P<high>-?\d+(?:\.\d+)?)"
    r"(?:\)|\])?",
    re.IGNORECASE,
)

MARKER_VALUE_ONLY_RE = re.compile(
    r"^(?P<name>[A-Za-z][A-Za-z0-9\s/().,%-]{2,45}?)\s*[:\-]\s*"
    r"(?P<value>-?\d+(?:\.\d+)?)\s*"
    r"(?P<unit>[a-zA-Z/%*^0-9._-]{1,18})?$",
    re.IGNORECASE,
)


def parse_lab_markers_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract lab markers strictly from text without inventing reference ranges."""
    if not text:
        return []

    markers: List[Dict[str, Any]] = []
    seen_names = set()

    for raw_line in text.splitlines():
        line = " ".join(raw_line.strip().split())
        if len(line) < 4 or len(line) > 160:
            continue

        match = MARKER_WITH_RANGE_RE.match(line)
        if match:
            name = match.group("name").strip(" :-\t")
            value_str = match.group("value")
            unit = (match.group("unit") or "").strip()
            low_str = match.group("low")
            high_str = match.group("high")

            try:
                val = float(value_str)
                low = float(low_str)
                high = float(high_str)
                if low <= high:
                    if val < low:
                        status_val = "low"
                    elif val > high:
                        status_val = "high"
                    else:
                        status_val = "normal"
                else:
                    status_val = "unknown"
            except ValueError:
                status_val = "unknown"

            key = name.lower()
            if key not in seen_names:
                seen_names.add(key)
                markers.append(
                    {
                        "name": name,
                        "value": value_str,
                        "unit": unit,
                        "reference_range": f"{low_str} - {high_str}",
                        "status": status_val,
                        "explanation": "",
                    }
                )
            continue

        val_match = MARKER_VALUE_ONLY_RE.match(line)
        if val_match:
            name = val_match.group("name").strip(" :-\t")
            key = name.lower()
            if key not in seen_names and not any(
                skip in key for skip in ("date", "page", "phone", "age", "id", "dob", "mrn")
            ):
                seen_names.add(key)
                markers.append(
                    {
                        "name": name,
                        "value": val_match.group("value"),
                        "unit": (val_match.group("unit") or "").strip(),
                        "reference_range": "Not specified in report",
                        "status": "unknown",
                        "explanation": "",
                    }
                )

    return markers


def format_summary_for_download(
    *,
    filename: str,
    created_at: str,
    summary_data: Dict[str, Any],
) -> tuple[str, str]:
    """Generate a clean Markdown summary document for download."""
    safe_stem = re.sub(r"[^A-Za-z0-9_-]", "_", filename.rsplit(".", 1)[0]) or "report"
    download_name = f"{safe_stem}_ai_summary.md"

    lines = [
        f"# Medical Report Educational Summary: {filename}",
        f"- **Generated:** {created_at}",
        f"- **AI Model:** {summary_data.get('ai_model') or 'N/A'}",
        "",
        f"> **Disclaimer:** {summary_data.get('disclaimer', '')}",
        "",
        "## Plain-Language Summary",
        summary_data.get("plain_summary", ""),
        "",
    ]

    markers = summary_data.get("lab_markers") or []
    if markers:
        lines.extend(
            [
                "## Extracted Laboratory Markers",
                "| Marker | Measured Value | Unit | Reference Range (from report) | Status |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for m in markers:
            lines.append(
                f"| {m.get('name', '')} | {m.get('value', '')} | {m.get('unit', '')} | "
                f"{m.get('reference_range', 'Not specified in report')} | {str(m.get('status', 'unknown')).upper()} |"
            )
        lines.append("")

    terms = summary_data.get("medical_terms") or []
    if terms:
        lines.append("## Medical Terms Explained")
        for t in terms:
            lines.append(f"- **{t.get('term', '')}:** {t.get('simple_explanation', '')}")
        lines.append("")

    questions = summary_data.get("questions_for_doctor") or []
    if questions:
        lines.append("## Questions to Ask Your Doctor")
        for q in questions:
            lines.append(f"- {q}")
        lines.append("")

    warnings = summary_data.get("warnings") or []
    if warnings:
        lines.append("## Important Notes & Limitations")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    return download_name, "\n".join(lines)
