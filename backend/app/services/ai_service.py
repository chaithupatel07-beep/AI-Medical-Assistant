"""Server-side LLM and Vision AI integration service."""

import base64
import json
import logging
from typing import Any, Dict, List

from fastapi import HTTPException, status
from openai import APIStatusError, AsyncOpenAI, AuthenticationError, RateLimitError

from app.core.config import get_settings
from app.core.safety import (
    EMERGENCY_GUIDANCE,
    GENERAL_DISCLAIMER,
    IMAGE_DISCLAIMER,
    REPORT_DISCLAIMER,
)

logger = logging.getLogger("ai_medical_assistant.ai")

CHAT_SYSTEM_PROMPT = """You are AI Medical Assistant, a careful, empathetic, educational healthcare companion.

STRICT SAFETY & CLINICAL RULES:
1. Provide GENERAL HEALTH EDUCATION only. Never diagnose any condition or prescribe any medication or dosage.
2. Never present yourself as a doctor or a replacement for professional medical care.
3. Explain medical terminology in simple, clear English.
4. Explain common possibilities neutrally using phrases like "may be associated with" or "common explanations include", never definitive diagnostic statements.
5. Clearly state when professional medical evaluation is appropriate.
6. If emergency warning signs are mentioned (chest pain, severe shortness of breath, stroke symptoms, severe bleeding, suicidal thoughts, anaphylaxis), IMMEDIATELY advise calling local emergency services or going to the nearest emergency room.
7. Suggest helpful questions the user can ask their healthcare provider.
8. Format responses clearly in Markdown."""

SYMPTOM_SYSTEM_PROMPT = """You are an educational healthcare information assistant helping a user prepare for a clinician visit.

STRICT RULES:
- Do NOT diagnose any disease or condition.
- Do NOT prescribe or recommend specific prescription medications or dosages.
- Clearly label possible explanations as general educational possibilities, NOT diagnoses.
- Highlight warning signs / red flags and when to seek urgent or emergency care.

Return ONLY valid JSON matching this exact schema:
{
  "educational_overview": "string",
  "possible_explanations": [
    {"title": "string (phrased as a general possibility)", "description": "string"}
  ],
  "recommended_next_steps": ["string"],
  "warning_signs": ["string"],
  "when_to_consult_doctor": "string",
  "questions_for_doctor": ["string"]
}"""

REPORT_SUMMARY_SYSTEM_PROMPT = """You are a medical report educational assistant helping a non-medical reader understand a laboratory or clinical report.

CRITICAL ACCURACY & SAFETY RULES:
1. Use ONLY the values, units, and reference ranges actually present in the supplied report text.
2. NEVER invent, guess, or fabricate laboratory reference ranges or test values. If a test has no reference range printed in the report, set "reference_range" to "Not specified in report" and "status" to "unknown".
3. Only classify "status" as "high", "low", or "normal" when a reference range is explicitly supplied in the report text and the comparison is unambiguous.
4. Do NOT diagnose conditions or prescribe treatments.
5. Explain medical terms in simple English.

Return ONLY valid JSON matching this exact schema:
{
  "plain_summary": "string",
  "lab_markers": [
    {
      "name": "string",
      "value": "string",
      "unit": "string",
      "reference_range": "string",
      "status": "high | low | normal | unknown",
      "explanation": "string"
    }
  ],
  "medical_terms": [
    {"term": "string", "simple_explanation": "string"}
  ],
  "questions_for_doctor": ["string"],
  "warnings": ["string"]
}"""

IMAGE_VISION_SYSTEM_PROMPT = """You are an educational medical image observation assistant.

CRITICAL SAFETY RULES:
1. NEVER claim that the image has been medically diagnosed or clinically validated.
2. NEVER provide a definitive diagnosis or prescribe treatment.
3. Describe only neutral, high-level visual observations (visible redness, swelling, text/labels, image quality/lighting) without diagnostic claims.
4. Clearly explain visual limitations, uncertainty, and why an in-person clinical exam or specialist/radiologist review is essential.
5. If emergency signs are described or visible, advise immediate medical care.

Return ONLY valid JSON matching this exact schema:
{
  "analysis_summary": "string",
  "observations": ["string"],
  "limitations": "string",
  "recommended_next_steps": "string"
}"""


def _get_client() -> AsyncOpenAI:
    settings = get_settings()
    if not settings.is_ai_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI service is not configured on the server. "
                "Set OPENAI_API_KEY in backend/.env and restart the FastAPI server."
            ),
        )
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


def _raise_provider_error(exc: Exception, fallback_detail: str) -> None:
    logger.exception("%s: %s", fallback_detail, exc)
    if isinstance(exc, AuthenticationError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider rejected OPENAI_API_KEY (401 Unauthorized). Check backend/.env.",
        ) from exc
    if isinstance(exc, RateLimitError):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI provider rate limit or quota exceeded (429). Please check your provider billing or try again shortly.",
        ) from exc
    if isinstance(exc, APIStatusError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{fallback_detail} (Upstream status {exc.status_code}).",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=fallback_detail,
    ) from exc


def _parse_json_response(raw_content: str) -> Dict[str, Any]:
    text = (raw_content or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def _provider_extra_kwargs(settings: Any) -> Dict[str, Any]:
    if settings.ai_provider.lower() == "gemini" or "generativelanguage.googleapis.com" in settings.openai_base_url:
        return {"reasoning_effort": "low"}
    return {}


async def generate_chat_reply(
    history: List[Dict[str, str]],
    user_message: str,
    emergency_detected: bool,
) -> tuple[str, str]:
    settings = get_settings()
    client = _get_client()

    messages: List[Dict[str, str]] = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    if emergency_detected:
        messages.append(
            {
                "role": "system",
                "content": (
                    "The user's message triggered emergency warning detection. "
                    "Begin your response with a clear recommendation to call local emergency "
                    "services or seek immediate emergency medical care."
                ),
            }
        )
    messages.extend(history[-12:])
    messages.append({"role": "user", "content": user_message})

    try:
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=0.2,
            max_tokens=2048,
            **_provider_extra_kwargs(settings),
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            raise ValueError("Empty response from AI provider.")
        if emergency_detected and "emergency" not in content.lower():
            content = f"**{EMERGENCY_GUIDANCE}**\n\n{content}"
        return content, settings.openai_chat_model
    except HTTPException:
        raise
    except Exception as exc:
        _raise_provider_error(
            exc,
            "Failed to generate response from the configured AI provider. Check your API key and model settings.",
        )


async def generate_symptom_guidance(
    payload: Dict[str, Any],
    emergency_detected: bool,
    emergency_reasons: List[str],
) -> tuple[Dict[str, Any], str]:
    settings = get_settings()
    client = _get_client()

    user_prompt = (
        f"Age: {payload['age']}\n"
        f"Gender (optional): {payload.get('gender') or 'Not specified'}\n"
        f"Main symptom: {payload['main_symptom']}\n"
        f"Duration: {payload['duration']}\n"
        f"Self-reported severity: {payload['severity']}\n"
        f"Additional symptoms: {payload.get('additional_symptoms') or 'None reported'}\n"
        f"Relevant context: {payload.get('relevant_context') or 'None provided'}\n"
    )
    if emergency_detected:
        user_prompt += (
            f"\nDetected potential urgent keywords: {', '.join(emergency_reasons)}. "
            "Emphasize immediate emergency care."
        )

    try:
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYMPTOM_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=2500,
            **_provider_extra_kwargs(settings),
        )
        parsed = _parse_json_response(response.choices[0].message.content or "{}")
        parsed["educational_overview"] = str(parsed.get("educational_overview") or "")
        explanations = parsed.get("possible_explanations")
        parsed["possible_explanations"] = (
            [
                {
                    "title": str(item.get("title", "General possibility")) if isinstance(item, dict) else "General possibility",
                    "description": str(item.get("description", "")) if isinstance(item, dict) else str(item),
                }
                for item in explanations
            ]
            if isinstance(explanations, list)
            else []
        )
        for list_key in ("recommended_next_steps", "warning_signs", "questions_for_doctor"):
            val = parsed.get(list_key)
            parsed[list_key] = [str(x) for x in val] if isinstance(val, list) else []
        parsed["when_to_consult_doctor"] = str(parsed.get("when_to_consult_doctor") or "")
        parsed["emergency_detected"] = emergency_detected
        parsed["emergency_reasons"] = emergency_reasons
        if emergency_detected:
            parsed["emergency_banner"] = EMERGENCY_GUIDANCE
        parsed["disclaimer"] = GENERAL_DISCLAIMER
        return parsed, settings.openai_chat_model
    except HTTPException:
        raise
    except Exception as exc:
        _raise_provider_error(exc, "Unable to complete symptom educational analysis from AI provider.")


async def generate_report_summary(
    extracted_text: str,
    deterministic_markers: List[Dict[str, Any]],
) -> tuple[Dict[str, Any], str]:
    settings = get_settings()
    client = _get_client()

    user_prompt = (
        "Here is the extracted text from an uploaded medical report:\n\n"
        f"\"\"\"\n{extracted_text[:12000]}\n\"\"\"\n\n"
        "Deterministic line-parser preliminary markers (verify strictly against the report text; "
        "NEVER invent missing reference ranges):\n"
        f"{json.dumps(deterministic_markers, indent=2)}"
    )

    try:
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": REPORT_SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=3000,
            **_provider_extra_kwargs(settings),
        )
        parsed = _parse_json_response(response.choices[0].message.content or "{}")
        normalized_markers = []
        for marker in parsed.get("lab_markers", []):
            if not isinstance(marker, dict):
                continue
            ref_range = (marker.get("reference_range") or "").strip()
            status_val = str(marker.get("status", "unknown")).lower()
            if not ref_range or ref_range.lower() in {"not specified", "not specified in report", "n/a", "none", "unknown"}:
                ref_range = "Not specified in report"
                status_val = "unknown"
            elif status_val not in {"high", "low", "normal", "unknown"}:
                status_val = "unknown"
            normalized_markers.append(
                {
                    "name": str(marker.get("name", "Unnamed Marker")),
                    "value": str(marker.get("value", "")),
                    "unit": str(marker.get("unit", "")),
                    "reference_range": ref_range,
                    "status": status_val,
                    "explanation": str(marker.get("explanation", "")),
                }
            )
        parsed["lab_markers"] = normalized_markers
        parsed["plain_summary"] = str(parsed.get("plain_summary") or "")
        terms = parsed.get("medical_terms")
        parsed["medical_terms"] = (
            [
                {
                    "term": str(t.get("term", "")) if isinstance(t, dict) else str(t),
                    "simple_explanation": str(t.get("simple_explanation", "")) if isinstance(t, dict) else "",
                }
                for t in terms
            ]
            if isinstance(terms, list)
            else []
        )
        for list_key in ("questions_for_doctor", "warnings"):
            val = parsed.get(list_key)
            parsed[list_key] = [str(x) for x in val] if isinstance(val, list) else []
        parsed["disclaimer"] = REPORT_DISCLAIMER
        return parsed, settings.openai_chat_model
    except HTTPException:
        raise
    except Exception as exc:
        _raise_provider_error(exc, "AI report summarization failed. Verify your server AI configuration.")


async def analyze_medical_image_with_vision(
    raw_bytes: bytes,
    mime_type: str,
    image_context: str | None,
) -> tuple[Dict[str, Any], str]:
    settings = get_settings()
    client = _get_client()

    b64 = base64.b64encode(raw_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"
    context_line = f"User-provided context: {image_context}" if image_context else "No additional user context provided."

    try:
        response = await client.chat.completions.create(
            model=settings.openai_vision_model,
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=2048,
            **_provider_extra_kwargs(settings),
            messages=[
                {"role": "system", "content": IMAGE_VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"{context_line}\n\n"
                                "Provide educational, non-diagnostic observations about this uploaded medical-related image, "
                                "explicitly noting limitations, uncertainty, and recommending professional medical review."
                            ),
                        },
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
        )
        parsed = _parse_json_response(response.choices[0].message.content or "{}")
        parsed["analysis_summary"] = str(parsed.get("analysis_summary") or "")
        obs = parsed.get("observations")
        parsed["observations"] = [str(x) for x in obs] if isinstance(obs, list) else []
        parsed["limitations"] = str(parsed.get("limitations") or "")
        parsed["recommended_next_steps"] = str(parsed.get("recommended_next_steps") or "")
        parsed["disclaimer"] = IMAGE_DISCLAIMER
        return parsed, settings.openai_vision_model
    except HTTPException:
        raise
    except Exception as exc:
        _raise_provider_error(exc, "Vision AI analysis failed. Verify OPENAI_API_KEY and OPENAI_VISION_MODEL.")
