"""Text extraction for uploaded contracts: PDF (pypdf) and DOCX (python-docx).

Contracts in Nepal are often produced in legacy Nepali fonts (Preeti, Kantipur)
whose PDF text layer is Latin gibberish ("s'g", "df]", "{"), or are scanned
images with no text layer at all. Auditing either would produce confident
nonsense, so both are rejected with a clear, bilingual error instead. OCR is
out of scope.
"""
from __future__ import annotations

import io
import re
import zipfile

from .. import text_norm
from .segment import normalize_text

MAX_PDF_PAGES = 300
MAX_DOCX_XML_BYTES = 40 * 1024 * 1024  # uncompressed word/document.xml (zip-bomb guard)
MIN_TEXT_CHARS = 40                     # below this a PDF is treated as having no text layer


class DocumentError(Exception):
    """A document we can't audit. `code` is stable for the frontend; the
    message is bilingual and safe to show to the user."""

    code = "document_error"
    message_en = "This document could not be read."
    message_ne = "यो कागजात पढ्न सकिएन।"

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.message_en)
        self.detail = detail

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message_en, "message_ne": self.message_ne}


class UnsupportedFormat(DocumentError):
    code = "unsupported_format"
    message_en = "Unsupported file type. Upload a PDF or a Word (.docx) file."
    message_ne = "यो फाइल प्रकार समर्थित छैन। PDF वा Word (.docx) फाइल अपलोड गर्नुहोस्।"


class LegacyFontError(DocumentError):
    code = "legacy_font"
    message_en = ("This PDF appears to use a legacy Nepali font (such as Preeti), so its text can't be read "
                  "reliably. Upload a Unicode PDF or a DOCX instead.")
    message_ne = ("यो PDF मा पुरानो नेपाली फन्ट (जस्तै प्रीति) प्रयोग भएको देखिन्छ, त्यसैले यसको पाठ भरपर्दो रूपमा "
                  "पढ्न सकिँदैन। युनिकोड PDF वा DOCX फाइल अपलोड गर्नुहोस्।")


class ScannedPdfError(DocumentError):
    code = "scanned_pdf"
    message_en = ("This PDF has no text layer (it looks like a scanned image). OCR isn't supported yet - "
                  "upload a text-based PDF or a DOCX.")
    message_ne = ("यो PDF मा पाठ तह छैन (स्क्यान गरिएको तस्बिर जस्तो देखिन्छ)। OCR अहिले समर्थित छैन - "
                  "पाठ भएको PDF वा DOCX अपलोड गर्नुहोस्।")


class EmptyDocumentError(DocumentError):
    code = "empty_document"
    message_en = "No readable text was found in this document."
    message_ne = "यो कागजातमा पढ्न सकिने पाठ भेटिएन।"


class CorruptDocumentError(DocumentError):
    code = "corrupt_document"
    message_en = "This file is damaged, password-protected or not a valid PDF/DOCX."
    message_ne = "यो फाइल बिग्रिएको, पासवर्डले सुरक्षित वा मान्य PDF/DOCX होइन।"


class ExtractedDocument:
    def __init__(self, text: str, kind: str, pages: int | None = None):
        self.text = text
        self.kind = kind          # "pdf" | "docx"
        self.pages = pages

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"ExtractedDocument(kind={self.kind!r}, chars={len(self.text)})"


# ------------------------------------------------------ legacy-font detection --

# Function words of English: real English contracts are full of them; Preeti
# gibberish ("d]/f] gfd xf]") has almost none.
_EN_FUNCTION = {
    "the", "of", "and", "to", "in", "a", "shall", "is", "be", "by", "for", "or", "this", "that", "with", "as",
    "on", "any", "at", "are", "from", "an", "not", "will", "party", "parties", "agreement", "such", "which",
    "its", "has", "have", "if", "may", "under", "other", "all", "it", "each", "upon", "than", "were", "was",
}
# ASCII symbols that Preeti-style fonts use for Devanagari letters/matras
# ( ] } { [ / ; ' \ | ~ ` ^ < > ), which almost never occur inside real words.
_PREETI_SYMBOLS = set("]}{[/;\\|~`^<>")
# Preeti digraphs that are extremely common in Nepali-in-Preeti and rare in English
_PREETI_DIGRAPH_RE = re.compile(r"[a-zA-Z]\]|[a-zA-Z]\}|f\]|cf|sf|df|gf|kf|nf|zf|xf|/[a-z]|[a-z]/[a-z]")
_CID_RE = re.compile(r"\(cid:\d+\)")


def looks_garbled(text: str) -> str | None:
    """None if `text` looks like ordinary text; otherwise the reason it looks
    like a legacy-font/undecodable extraction ("legacy_font" | "cid")."""
    if not text:
        return None
    compact = re.sub(r"\s+", "", text)
    if len(compact) < 60:
        return None
    if len(_CID_RE.findall(text)) >= 10 or text.count("\ufffd") / len(compact) > 0.10:
        return "cid"
    dev = len(text_norm.DEVANAGARI_RE.findall(text))
    letters = sum(ch.isalpha() for ch in compact)
    if letters and dev / letters > 0.30:
        return None  # real Unicode Devanagari dominates: fine
    words = re.findall(r"\S+", text)
    if len(words) < 12:
        return None
    lowered = [re.sub(r"[^a-z]", "", w.lower()) for w in words]
    en_share = sum(w in _EN_FUNCTION for w in lowered) / len(words)
    sym_share = sum(ch in _PREETI_SYMBOLS for ch in compact) / len(compact)
    words_with_sym = sum(any(ch in _PREETI_SYMBOLS for ch in w) and any(c.isalpha() for c in w) for w in words) / len(words)
    digraphs = len(_PREETI_DIGRAPH_RE.findall(text)) / len(words)
    # English prose: en_share is typically 0.25-0.45 and symbol share <1%.
    # Preeti Nepali: en_share ~0-0.05, lots of symbol-bearing "words".
    if en_share < 0.08 and (sym_share >= 0.04 or words_with_sym >= 0.25) and digraphs >= 0.3:
        return "legacy_font"
    return None


# ---------------------------------------------------------------- PDF -----

def _extract_pdf(data: bytes) -> ExtractedDocument:
    from pypdf import PdfReader
    from pypdf.errors import PyPdfError

    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            try:
                if not reader.decrypt(""):
                    raise CorruptDocumentError("password-protected PDF")
            except CorruptDocumentError:
                raise
            except Exception as exc:  # noqa: BLE001 - pypdf raises assorted crypto errors
                raise CorruptDocumentError(str(exc)[:120]) from exc
        n_pages = len(reader.pages)
        if n_pages > MAX_PDF_PAGES:
            raise DocumentError(f"too many pages ({n_pages}); the limit is {MAX_PDF_PAGES}")
        page_texts = []
        for page in reader.pages:
            try:
                page_texts.append(page.extract_text() or "")
            except Exception:  # noqa: BLE001 - one bad page shouldn't sink the document
                page_texts.append("")
    except DocumentError:
        raise
    except (PyPdfError, ValueError, KeyError, TypeError, OSError, RecursionError) as exc:
        raise CorruptDocumentError(str(exc)[:120]) from exc

    text = normalize_text("\n\n".join(page_texts))
    if len(re.sub(r"\s+", "", text)) < MIN_TEXT_CHARS:
        raise ScannedPdfError()
    if looks_garbled(text):
        raise LegacyFontError()
    return ExtractedDocument(text, "pdf", n_pages)


# --------------------------------------------------------------- DOCX -----

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _numbering_formats(doc) -> dict[tuple[str, str], str]:
    """(numId, ilvl) -> numFmt ("decimal", "bullet", "lowerLetter", ...)."""
    try:
        root = doc.part.numbering_part.element
    except Exception:  # noqa: BLE001 - no numbering part
        return {}
    abstract: dict[str, dict[str, str]] = {}
    for an in root.findall(f"{_W}abstractNum"):
        aid = an.get(f"{_W}abstractNumId")
        levels = {}
        for lvl in an.findall(f"{_W}lvl"):
            fmt = lvl.find(f"{_W}numFmt")
            levels[lvl.get(f"{_W}ilvl")] = fmt.get(f"{_W}val") if fmt is not None else "decimal"
        abstract[aid] = levels
    out: dict[tuple[str, str], str] = {}
    for num in root.findall(f"{_W}num"):
        nid = num.get(f"{_W}numId")
        ref = num.find(f"{_W}abstractNumId")
        levels = abstract.get(ref.get(f"{_W}val")) if ref is not None else None
        for ilvl, fmt in (levels or {}).items():
            out[(nid, ilvl)] = fmt
    return out


def _style_num_pr(styles_el, style_id: str | None):
    """numPr inherited from a paragraph style (Word's built-in "List Number"
    carries its numbering there, not on the paragraph), following basedOn."""
    for _ in range(5):
        if not style_id:
            return None
        style = next((st for st in styles_el.findall(f"{_W}style") if st.get(f"{_W}styleId") == style_id), None)
        if style is None:
            return None
        ppr = style.find(f"{_W}pPr")
        num_pr = ppr.find(f"{_W}numPr") if ppr is not None else None
        if num_pr is not None:
            return num_pr
        based = style.find(f"{_W}basedOn")
        style_id = based.get(f"{_W}val") if based is not None else None
    return None


def _paragraph_number(p_el, fmts, counters: dict[str, list[int]], styles_el=None) -> str | None:
    """The auto-number Word would show for a numbered paragraph ("1.", "1.2"),
    or None. Word stores the number as list metadata, not in the text, so
    without this an auto-numbered contract would lose every clause number."""
    ppr = p_el.find(f"{_W}pPr")
    num_pr = ppr.find(f"{_W}numPr") if ppr is not None else None
    if num_pr is None and ppr is not None and styles_el is not None:
        pstyle = ppr.find(f"{_W}pStyle")
        num_pr = _style_num_pr(styles_el, pstyle.get(f"{_W}val") if pstyle is not None else None)
    if num_pr is None:
        return None
    ilvl_el, id_el = num_pr.find(f"{_W}ilvl"), num_pr.find(f"{_W}numId")
    if id_el is None:
        return None
    nid = id_el.get(f"{_W}val")
    ilvl = ilvl_el.get(f"{_W}val") if ilvl_el is not None else "0"
    if nid == "0":
        return None
    fmt = fmts.get((nid, ilvl), "decimal")
    if fmt in ("bullet", "none"):
        return None
    lvl = int(ilvl)
    stack = counters.setdefault(nid, [])
    while len(stack) <= lvl:
        stack.append(0)
    stack[lvl] += 1
    del stack[lvl + 1:]
    if fmt != "decimal" and lvl > 0:
        return None  # (a) (i) sub-items belong to their parent clause
    return ".".join(str(n) for n in stack[: lvl + 1] if n) + ("." if lvl == 0 else "")


def _extract_docx(data: bytes) -> ExtractedDocument:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            try:
                info = zf.getinfo("word/document.xml")
            except KeyError:
                raise UnsupportedFormat() from None  # a zip, but not a Word document
            if info.file_size > MAX_DOCX_XML_BYTES:
                raise CorruptDocumentError("document.xml is implausibly large")
        document = docx.Document(io.BytesIO(data))
    except DocumentError:
        raise
    except Exception as exc:  # noqa: BLE001 - BadZipFile, XML/package errors, ...
        raise CorruptDocumentError(str(exc)[:120]) from exc

    fmts = _numbering_formats(document)
    styles_el = document.styles.element
    counters: dict[str, list[int]] = {}
    lines: list[str] = []
    body = document.element.body
    for child in body.iterchildren():
        if child.tag == f"{_W}p":
            para = Paragraph(child, document)
            txt = para.text.strip()
            if not txt:
                lines.append("")
                continue
            number = _paragraph_number(child, fmts, counters, styles_el)
            if number and not re.match(r"^\s*(?:[0-9०-९]{1,3}[.)]|[0-9०-९]+\.[0-9०-९]+|clause|दफा|बुँदा)", txt, re.I):
                txt = f"{number} {txt}"
            lines.append(txt)
        elif child.tag == f"{_W}tbl":
            table = Table(child, document)
            for row in table.rows:
                seen, cells = set(), []
                for cell in row.cells:
                    if id(cell._tc) in seen:  # merged cells repeat
                        continue
                    seen.add(id(cell._tc))
                    t = " ".join(cell.text.split())
                    if t:
                        cells.append(t)
                if cells:
                    lines.append(" | ".join(cells))
            lines.append("")
    text = normalize_text("\n".join(lines))
    if len(re.sub(r"\s+", "", text)) < 20:
        raise EmptyDocumentError()
    if looks_garbled(text):
        raise LegacyFontError()
    return ExtractedDocument(text, "docx")


# ------------------------------------------------------------------ entry --

def extract_text(filename: str, data: bytes) -> ExtractedDocument:
    """Extract clean text from a PDF or DOCX. Raises a DocumentError subclass
    (UnsupportedFormat, LegacyFontError, ScannedPdfError, EmptyDocumentError,
    CorruptDocumentError) for anything we can't audit. The format is decided
    by the file's magic bytes; the extension is only a fallback hint."""
    if not data:
        raise EmptyDocumentError()
    head = data[:8]
    if head.startswith(b"%PDF") or b"%PDF" in data[:1024]:
        return _extract_pdf(data)
    if head.startswith(b"PK\x03\x04"):
        name = (filename or "").lower()
        if name.endswith((".doc", ".xlsx", ".pptx")):
            raise UnsupportedFormat()
        return _extract_docx(data)
    raise UnsupportedFormat()
