from typing import Optional

SUPPORTED_LANGS = {"ru", "en", "kz"}


def normalize_lang(x_lang: Optional[str], accept_language: Optional[str], default: str = "ru") -> str:
    if x_lang:
        lang = x_lang.strip().lower()
        if lang in SUPPORTED_LANGS:
            return lang

    if accept_language:
        parts = [p.strip().lower() for p in accept_language.split(",") if p.strip()]
        for part in parts:
            code = part.split(";", 1)[0].split("-", 1)[0]
            if code in SUPPORTED_LANGS:
                return code

    return default


def normalize_i18n_map(raw: Optional[dict], fallback_text: Optional[str] = None, default_lang: str = "ru") -> dict:
    result: dict[str, str] = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            if not isinstance(key, str):
                continue
            norm_key = key.strip().lower()
            if norm_key in SUPPORTED_LANGS and isinstance(value, str) and value.strip():
                result[norm_key] = value.strip()

    if fallback_text and fallback_text.strip() and default_lang not in result:
        result[default_lang] = fallback_text.strip()

    return result


def localize_text(i18n_map: Optional[dict], fallback_text: Optional[str], lang: str) -> str:
    if isinstance(i18n_map, dict):
        value = i18n_map.get(lang) or i18n_map.get("ru") or i18n_map.get("en") or i18n_map.get("kz")
        if isinstance(value, str) and value.strip():
            return value.strip()

    if isinstance(fallback_text, str) and fallback_text.strip():
        return fallback_text.strip()

    return ""
