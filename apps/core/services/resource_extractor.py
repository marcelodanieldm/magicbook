"""
Resource Extractor Service
Extracts readable text from PDF files and web URLs for injection
into the Chapter Writer prompt as author knowledge base.
"""
import re


# ── PDF Extraction ────────────────────────────────────────────────────────────

def extract_from_pdf(file_path: str, max_chars: int = 12_000) -> str:
    """
    Extract text from a PDF file.
    Requires: pip install pypdf
    Returns up to max_chars characters of clean text.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError(
            "El paquete 'pypdf' no está instalado. "
            "Ejecuta: pip install pypdf"
        )

    reader = PdfReader(file_path)
    pages_text = []
    total = 0

    for page in reader.pages:
        text = page.extract_text() or ''
        text = _clean_text(text)
        if text:
            pages_text.append(text)
            total += len(text)
        if total >= max_chars:
            break

    raw = '\n\n'.join(pages_text)
    return raw[:max_chars]


# ── URL Extraction ────────────────────────────────────────────────────────────

def extract_from_url(url: str, max_chars: int = 12_000,
                     timeout: int = 15) -> str:
    """
    Fetch a web page and extract its main text content.
    Requires: pip install requests beautifulsoup4
    Returns up to max_chars characters of clean text.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "Los paquetes 'requests' y 'beautifulsoup4' no están instalados. "
            "Ejecuta: pip install requests beautifulsoup4"
        )

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0 Safari/537.36'
        )
    }

    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Remove non-content tags
    for tag in soup(['script', 'style', 'nav', 'header', 'footer',
                     'aside', 'noscript', 'form', 'button']):
        tag.decompose()

    # Prefer <article> or <main> if present, otherwise use <body>
    container = (
        soup.find('article')
        or soup.find('main')
        or soup.find('body')
        or soup
    )

    paragraphs = [
        _clean_text(el.get_text(separator=' '))
        for el in container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
        if el.get_text(strip=True)
    ]

    raw = '\n\n'.join(paragraphs)
    return raw[:max_chars]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Collapse whitespace, remove control characters."""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
