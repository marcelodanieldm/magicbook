"""Global context processors injected into every template render."""

import re


# Maps browser Accept-Language prefixes to one of our three supported codes.
_LANG_MAP = {
    'pt': 'pt',
    'en': 'en',
}
_DEFAULT_LANG = 'es'


def ui_language(request):
    """
    Detects the visitor's preferred UI language from the Accept-Language header
    and returns it as the ``ui_lang`` template variable ('es', 'en', or 'pt').

    Detection rules:
      - pt-* or pt → Portuguese
      - en-* or en  → English
      - anything else (es-*, es, or unknown) → Spanish (default)
    """
    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    first = re.split(r'[,;]', accept)[0].strip().lower()
    prefix = first.split('-')[0]
    lang = _LANG_MAP.get(prefix, _DEFAULT_LANG)
    return {'ui_lang': lang}
