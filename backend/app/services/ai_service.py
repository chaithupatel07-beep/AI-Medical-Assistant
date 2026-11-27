"""Server-side LLM and Vision AI integration service."""

import base64
import json
import logging
from typing import Any, Dict, List

from fastapi import HTTPException, status
import httpx
from openai import APIStatusError, AsyncOpenAI, AuthenticationError, RateLimitError

from app.ai.local_engine import (
    OLLAMA_BASE_URL,
    analyze_image_locally,
    detect_ollama_model,
    generate_rule_based_chat_reply,
    generate_rule_based_report_summary,
    generate_rule_based_symptom_guidance,
)
from app.core.config import get_settings
from app.core.safety import (
    get_disclaimer,
    normalize_language,
)

logger = logging.getLogger("ai_medical_assistant.ai")

LANGUAGE_DIRECTIVES = {
    "en": "Respond in clear, simple English that any patient can easily understand.",
    "te": (
        "Respond ENTIRELY in clear, simple, natural everyday Telugu (తెలుగు script) so that "
        "every Telugu-speaking user can easily understand. You may include common medical terms "
        "in brackets for clarity, e.g., హిమోగ్లోబిన్ (Hemoglobin)."
    ),
    "hi": (
        "Respond ENTIRELY in clear, simple, natural everyday Hindi (हिन्दी Devanagari script) so that "
        "every Hindi-speaking user can easily understand. You may include common medical terms "
        "in brackets for clarity, e.g., हीमोग्लोबिन (Hemoglobin)."
    ),
}

CHAT_SYSTEM_PROMPT = """You are AI Medical Assistant, a careful, empathetic, educational healthcare companion.

STRICT SAFETY & CLINICAL RULES:
1. Provide GENERAL HEALTH EDUCATION only. Never diagnose any condition or prescribe any medication or dosage.
2. Never present yourself as a doctor or a replacement for professional medical care.
3. Explain medical terminology in simple, clear language and cite trusted public health sources (MedlinePlus, CDC, or WHO) when sharing general health guidance.
4. Explain common possibilities neutrally using phrases like "may be associated with" or "common explanations include", never definitive diagnostic statements.
5. Clearly state when professional medical evaluation is appropriate.
6. If emergency warning signs are mentioned (chest pain, severe shortness of breath, stroke symptoms, severe bleeding, suicidal thoughts, anaphylaxis), IMMEDIATELY advise calling local emergency services or going to the nearest emergency room.
7. Suggest helpful questions the user can ask their healthcare provider.
8. Format responses clearly in Markdown."""

SYMPTOM_SYSTEM_PROMPT = """You are an educational healthcare information assistant helping a user prepare for a clinician visit.

STRICT RULES:
- Do NOT diagnose any disease or condition.
- Do NOT prescribe or recommend specific prescription medications or dosages.
- Clearly label possible explanations as general educational possibilities grounded in MedlinePlus, CDC, and WHO guidance, NOT diagnoses.
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
  "questions_for_doctor": ["string"],
  "questions_for_doctor_en": ["string (same questions in English for clinician visits)"]
}"""

REPORT_SUMMARY_SYSTEM_PROMPT = """You are a medical report educational assistant helping a non-medical reader understand a laboratory or clinical report.

CRITICAL ACCURACY & SAFETY RULES:
1. Use ONLY the values, units, and reference ranges actually present in the supplied report text.
2. NEVER invent, guess, or fabricate laboratory reference ranges or test values. If a test has no reference range printed in the report, set "reference_range" to "Not specified in report" and "status" to "unknown", and optionally note typical adult MedlinePlus educational guidance in the "explanation" field.
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
                "Cloud AI API key is not configured on the server."
            ),
        )
    return AsyncOpenAI(
        api_key=settings.effective_api_key,
        base_url=settings.effective_base_url,
    )


async def _resolve_ai_target(vision: bool = False) -> tuple[AsyncOpenAI | None, str, str]:
    """Return (client, model_name, mode) where mode is 'cloud_ai' | 'ollama_local' | 'built_in_offline'."""
    settings = get_settings()
    if settings.is_ai_configured:
        model = settings.effective_vision_model if vision else settings.effective_chat_model
        return _get_client(), model, "cloud_ai"

    ollama_base = (settings.ollama_base_url or OLLAMA_BASE_URL).rstrip("/")
    ollama_model = await detect_ollama_model(settings.ollama_model or None)
    if ollama_model:
        client = AsyncOpenAI(
            api_key="ollama",
            base_url=f"{ollama_base}/v1",
        )
        return client, ollama_model, "ollama_local"

    return None, "", "built_in_offline"


def _raise_provider_error(exc: Exception, fallback_detail: str) -> None:
    logger.exception("%s: %s", fallback_detail, exc)
    if isinstance(exc, AuthenticationError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider rejected the configured API key (401 Unauthorized). Check GEMINI_API_KEY / OPENAI_API_KEY.",
        ) from exc
    if isinstance(exc, RateLimitError):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI provider rate limit or quota exceeded (429). Please check billing/quota or try again shortly.",
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


async def _call_gemini_native(
    *,
    api_key: str,
    model_name: str,
    system_instruction: str,
    contents: List[Dict[str, Any]],
    response_mime_type: str | None = None,
    temperature: float = 0.2,
    max_output_tokens: int = 3072,
) -> tuple[str, str]:
    """Call native Google Gemini REST generateContent (supports inlineData PDF/image + JSON)."""
    models_to_try = [model_name]
    for fallback_m in ("gemini-2.5-flash", "gemini-3.5-flash-lite"):
        if fallback_m not in models_to_try:
            models_to_try.append(fallback_m)

    gen_config: Dict[str, Any] = {
        "temperature": temperature,
        "maxOutputTokens": max_output_tokens,
    }
    if response_mime_type:
        gen_config["responseMimeType"] = response_mime_type

    payload: Dict[str, Any] = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": contents,
        "generationConfig": gen_config,
    }

    last_err = ""
    last_status = 502
    async with httpx.AsyncClient(timeout=45.0) as client:
        for candidate_model in models_to_try:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{candidate_model}:generateContent?key={api_key}"
            )
            try:
                res = await client.post(url, json=payload)
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to connect to Google Gemini API: {exc}",
                ) from exc

            if res.status_code == 404:
                last_err = res.text[:300]
                last_status = 404
                continue
            if res.status_code == 429:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Google Gemini rate limit / quota exceeded: {res.text[:250]}",
                )
            if res.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Google Gemini API error ({res.status_code}): {res.text[:300]}",
                )

            data = res.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text = "\n".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
            if not text:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Google Gemini returned an empty response.",
                )
            return text, candidate_model

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Configured Gemini model unavailable ({last_status}): {last_err}",
    )


def _parse_json_response(raw_content: str) -> Dict[str, Any]:
    text = (raw_content or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _provider_extra_kwargs(settings: Any, mode: str = "cloud_ai") -> Dict[str, Any]:
    if mode == "cloud_ai" and (
        settings.effective_provider.lower() == "gemini"
        or "generativelanguage.googleapis.com" in settings.effective_base_url
    ):
        return {"reasoning_effort": "low"}
    return {}


async def generate_chat_reply(
    history: List[Dict[str, str]],
    user_message: str,
    emergency_detected: bool,
    language: str = "en",
) -> tuple[str, str]:
    settings = get_settings()
    lang = normalize_language(language)

    system_text = f"{CHAT_SYSTEM_PROMPT}\n\nLANGUAGE REQUIREMENT:\n{LANGUAGE_DIRECTIVES[lang]}"
    if emergency_detected:
        system_text += (
            "\n\nEMERGENCY NOTICE: The user's message triggered emergency warning detection. "
            "Begin your response immediately with a clear recommendation to call local emergency "
            "services or seek immediate emergency medical care."
        )

    if settings.is_ai_configured and settings._uses_gemini_key:
        contents: List[Dict[str, Any]] = []
        for item in history[-16:]:
            role = "model" if item.get("role") == "assistant" else "user"
            txt = (item.get("content") or "").strip()
            if txt:
                contents.append({"role": role, "parts": [{"text": txt}]})
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        content, used_model = await _call_gemini_native(
            api_key=settings.effective_api_key,
            model_name=settings.effective_chat_model,
            system_instruction=system_text,
            contents=contents,
            temperature=0.3,
            max_output_tokens=2048,
        )
        emergency_text = get_disclaimer("emergency", lang)
        if emergency_detected and "112" not in content and "emergency" not in content.lower():
            content = f"**{emergency_text}**\n\n{content}"
        return content, used_model

    client, model_name, mode = await _resolve_ai_target(vision=False)

    if mode == "built_in_offline" or client is None:
        return generate_rule_based_chat_reply(user_message, emergency_detected, lang)

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_text}]
    messages.extend(history[-16:])
    messages.append({"role": "user", "content": user_message})

    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,  # type: ignore[arg-type]
            temperature=0.2,
            max_tokens=2048,
            **_provider_extra_kwargs(settings, mode),
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            raise ValueError("Empty response from AI provider.")
        emergency_text = get_disclaimer("emergency", lang)
        if emergency_detected and "112" not in content and "emergency" not in content.lower():
            content = f"**{emergency_text}**\n\n{content}"
        return content, model_name
    except HTTPException:
        raise
    except Exception as exc:
        if mode == "ollama_local":
            logger.warning("Local Ollama chat failed (%s); falling back to built-in offline engine.", exc)
            return generate_rule_based_chat_reply(user_message, emergency_detected, lang)
        _raise_provider_error(
            exc,
            "Failed to generate response from the configured AI provider. Check your API key and model settings.",
        )


def _normalize_symptom_payload(
    parsed: Dict[str, Any],
    emergency_detected: bool,
    emergency_reasons: List[str],
    lang: str,
    severity_score: int | None = None,
) -> Dict[str, Any]:
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
    for list_key in ("recommended_next_steps", "warning_signs", "questions_for_doctor", "questions_for_doctor_en"):
        val = parsed.get(list_key)
        parsed[list_key] = [str(x) for x in val] if isinstance(val, list) else []
    if not parsed["questions_for_doctor_en"]:
        parsed["questions_for_doctor_en"] = list(parsed["questions_for_doctor"])
    parsed["when_to_consult_doctor"] = str(parsed.get("when_to_consult_doctor") or "")
    parsed["severity_score"] = severity_score
    parsed["emergency_detected"] = emergency_detected
    parsed["emergency_reasons"] = emergency_reasons
    if emergency_detected:
        parsed["emergency_banner"] = get_disclaimer("emergency", lang)
    parsed["disclaimer"] = get_disclaimer("general", lang)
    return parsed


async def generate_symptom_guidance(
    payload: Dict[str, Any],
    emergency_detected: bool,
    emergency_reasons: List[str],
    language: str = "en",
) -> tuple[Dict[str, Any], str]:
    settings = get_settings()
    lang = normalize_language(language)

    user_prompt = (
        f"Age: {payload['age']}\n"
        f"Gender (optional): {payload.get('gender') or 'Not specified'}\n"
        f"Main symptom: {payload['main_symptom']}\n"
        f"Duration: {payload['duration']}\n"
        f"Self-reported severity: {payload['severity']}"
        + (f" ({payload['severity_score']}/10)" if payload.get("severity_score") else "")
        + "\n"
        f"Additional symptoms: {payload.get('additional_symptoms') or 'None reported'}\n"
        f"Relevant context: {payload.get('relevant_context') or 'None provided'}\n"
    )
    if emergency_detected:
        user_prompt += (
            f"\nDetected potential urgent keywords: {', '.join(emergency_reasons)}. "
            "Emphasize immediate emergency care."
        )

    system_text = (
        f"{SYMPTOM_SYSTEM_PROMPT}\n\nLANGUAGE REQUIREMENT:\n"
        f"{LANGUAGE_DIRECTIVES[lang]} Keep all JSON keys strictly in English, "
        "and write all JSON string values in the requested language."
    )

    if settings.is_ai_configured and settings._uses_gemini_key:
        raw_text, used_model = await _call_gemini_native(
            api_key=settings.effective_api_key,
            model_name=settings.effective_chat_model,
            system_instruction=system_text,
            contents=[{"role": "user", "parts": [{"text": user_prompt}]}],
            response_mime_type="application/json",
            temperature=0.25,
            max_output_tokens=2500,
        )
        parsed = _parse_json_response(raw_text)
        return (
            _normalize_symptom_payload(
                parsed,
                emergency_detected,
                emergency_reasons,
                lang,
                severity_score=payload.get("severity_score"),
            ),
            used_model,
        )

    client, model_name, mode = await _resolve_ai_target(vision=False)

    if mode == "built_in_offline" or client is None:
        return generate_rule_based_symptom_guidance(payload, emergency_detected, emergency_reasons, lang)

    try:
        kwargs: Dict[str, Any] = dict(_provider_extra_kwargs(settings, mode))
        if mode == "cloud_ai":
            kwargs["response_format"] = {"type": "json_object"}
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=2500,
            **kwargs,
        )
        parsed = _parse_json_response(response.choices[0].message.content or "{}")
        return (
            _normalize_symptom_payload(
                parsed,
                emergency_detected,
                emergency_reasons,
                lang,
                severity_score=payload.get("severity_score"),
            ),
            model_name,
        )
    except HTTPException:
        raise
    except Exception as exc:
        if mode == "ollama_local":
            logger.warning("Local Ollama symptom check failed (%s); falling back to rules engine.", exc)
            return generate_rule_based_symptom_guidance(payload, emergency_detected, emergency_reasons, lang)
        _raise_provider_error(exc, "Unable to complete symptom educational analysis from AI provider.")


def _normalize_report_payload(parsed: Dict[str, Any], lang: str) -> Dict[str, Any]:
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
    parsed["disclaimer"] = get_disclaimer("report", lang)
    return parsed


async def generate_report_summary(
    extracted_text: str,
    deterministic_markers: List[Dict[str, Any]],
    language: str = "en",
    raw_bytes: bytes | None = None,
    mime_type: str | None = None,
) -> tuple[Dict[str, Any], str]:
    settings = get_settings()
    lang = normalize_language(language)

    system_text = (
        f"{REPORT_SUMMARY_SYSTEM_PROMPT}\n\n"
        "You may also include \"extracted_text\" in the JSON output with the verbatim report text when reading from an image or PDF.\n\n"
        f"LANGUAGE REQUIREMENT:\n{LANGUAGE_DIRECTIVES[lang]} Keep all JSON keys and marker status values "
        "('high', 'low', 'normal', 'unknown') strictly in English, and write "
        "plain_summary, explanations, medical_terms, questions_for_doctor, and warnings "
        "in the requested language."
    )

    if settings.is_ai_configured and settings._uses_gemini_key:
        parts: List[Dict[str, Any]] = []
        if raw_bytes and mime_type:
            b64 = base64.b64encode(raw_bytes).decode("utf-8")
            parts.append(
                {
                    "text": (
                        "Read EVERY visible laboratory test row, value, unit, and reference range directly from this medical report file. "
                        "If printed reference ranges are absent for a marker, clearly mark reference_range as 'Not specified in report' and note standard MedlinePlus educational adult reference guidance in explanation.\n\n"
                        + (f"Preliminary extracted text:\n{extracted_text[:8000]}\n" if extracted_text else "")
                    )
                }
            )
            parts.append({"inlineData": {"mimeType": mime_type, "data": b64}})
            model_to_use = settings.effective_vision_model
        else:
            parts.append(
                {
                    "text": (
                        "Here is the extracted text from an uploaded medical report:\n\n"
                        f"\"\"\"\n{extracted_text[:12000]}\n\"\"\"\n\n"
                        "Deterministic line-parser preliminary markers:\n"
                        f"{json.dumps(deterministic_markers, indent=2)}"
                    )
                }
            )
            model_to_use = settings.effective_chat_model

        raw_text, used_model = await _call_gemini_native(
            api_key=settings.effective_api_key,
            model_name=model_to_use,
            system_instruction=system_text,
            contents=[{"role": "user", "parts": parts}],
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=3500,
        )
        parsed = _parse_json_response(raw_text)
        extracted_from_ai = str(parsed.get("extracted_text") or "").strip()
        normalized = _normalize_report_payload(parsed, lang)
        if extracted_from_ai:
            normalized["extracted_text"] = extracted_from_ai
        return normalized, used_model

    if not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No embedded text was found in this scanned report. Set GEMINI_API_KEY in server environment variables to read scanned PDFs and lab images with Gemini Multimodal Vision."
            ),
        )

    client, model_name, mode = await _resolve_ai_target(vision=False)

    if mode == "built_in_offline" or client is None:
        return generate_rule_based_report_summary(extracted_text, deterministic_markers, lang)

    user_prompt = (
        "Here is the extracted text from an uploaded medical report:\n\n"
        f"\"\"\"\n{extracted_text[:12000]}\n\"\"\"\n\n"
        "Deterministic line-parser preliminary markers (verify strictly against the report text; "
        "NEVER invent missing reference ranges):\n"
        f"{json.dumps(deterministic_markers, indent=2)}"
    )

    try:
        kwargs: Dict[str, Any] = dict(_provider_extra_kwargs(settings, mode))
        if mode == "cloud_ai":
            kwargs["response_format"] = {"type": "json_object"}
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=3000,
            **kwargs,
        )
        parsed = _parse_json_response(response.choices[0].message.content or "{}")
        return _normalize_report_payload(parsed, lang), model_name
    except HTTPException:
        raise
    except Exception as exc:
        if mode == "ollama_local":
            logger.warning("Local Ollama report summary failed (%s); falling back to deterministic parser.", exc)
            return generate_rule_based_report_summary(extracted_text, deterministic_markers, lang)
        _raise_provider_error(exc, "AI report summarization failed. Verify your server AI configuration.")


async def analyze_medical_image_with_vision(
    raw_bytes: bytes,
    mime_type: str,
    image_context: str | None,
    language: str = "en",
) -> tuple[Dict[str, Any], str]:
    settings = get_settings()
    lang = normalize_language(language)
    context_line = f"User-provided context: {image_context}" if image_context else "No additional user context provided."
    system_text = (
        f"{IMAGE_VISION_SYSTEM_PROMPT}\n\nLANGUAGE REQUIREMENT:\n"
        f"{LANGUAGE_DIRECTIVES[lang]} Keep all JSON keys strictly in English, "
        "and write all JSON string values in the requested language."
    )

    if settings.is_ai_configured and settings._uses_gemini_key:
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        raw_text, used_model = await _call_gemini_native(
            api_key=settings.effective_api_key,
            model_name=settings.effective_vision_model,
            system_instruction=system_text,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                f"{context_line}\n\n"
                                "Provide detailed, neutral, non-diagnostic educational visual observations about this uploaded medical-related image, "
                                "explicitly noting limitations, uncertainty, and recommending professional medical review."
                            )
                        },
                        {"inlineData": {"mimeType": mime_type, "data": b64}},
                    ],
                }
            ],
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=2048,
        )
        parsed = _parse_json_response(raw_text)
        parsed["analysis_summary"] = str(parsed.get("analysis_summary") or "")
        obs = parsed.get("observations")
        parsed["observations"] = [str(x) for x in obs] if isinstance(obs, list) else []
        parsed["limitations"] = str(parsed.get("limitations") or "")
        parsed["recommended_next_steps"] = str(parsed.get("recommended_next_steps") or "")
        parsed["disclaimer"] = get_disclaimer("image", lang)
        return parsed, used_model

    client, model_name, mode = await _resolve_ai_target(vision=True)

    if mode == "built_in_offline" or client is None:
        return analyze_image_locally(raw_bytes, mime_type, image_context, lang)

    b64 = base64.b64encode(raw_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    try:
        kwargs: Dict[str, Any] = dict(_provider_extra_kwargs(settings, mode))
        if mode == "cloud_ai":
            kwargs["response_format"] = {"type": "json_object"}
        response = await client.chat.completions.create(
            model=model_name,
            temperature=0.2,
            max_tokens=2048,
            **kwargs,
            messages=[
                {"role": "system", "content": system_text},
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
        parsed["disclaimer"] = get_disclaimer("image", lang)
        return parsed, model_name
    except HTTPException:
        raise
    except Exception as exc:
        if mode == "ollama_local":
            logger.warning("Local Ollama image analysis failed (%s); falling back to local Pillow inspector.", exc)
            return analyze_image_locally(raw_bytes, mime_type, image_context, lang)
        _raise_provider_error(exc, "Vision AI analysis failed. Verify GEMINI_API_KEY and vision model settings.")
