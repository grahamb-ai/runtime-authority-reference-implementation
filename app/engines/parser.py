## @file parser.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Document parsing: turn an uploaded policy file (PDF, DOCX, or TXT) into raw text.
#
"""Document parsing -> turn an uploaded policy file into raw text.

This module isolates every file-format concern behind a single "'extract_text'
function. The extractor downstream only ever sees a plain string, so it never
needs to know whether the text came from a PDF, a Word document, or a .txt file.

Supported formats:
  - .pdf  -> pdfplumber   (text extraction, page by page)
  - .docx -> python-docx  (reads paragraph text)
  - .txt  -> plain read   (POC convenience: makes local testing and the
             acceptance fixtures trivial, with no binary files to generate)
"""

from __future__ import annotations

from pathlib import Path

# Single source of truth for what the API is allowed to accept.
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class UnsupportedFileType(ValueError):
    """Raised when an uploaded file has an unsupported extension."""

## @fn extract_text(path)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Return the concatenated raw text of the document at the given path.
#  @param path Filesystem path to the uploaded policy document.
#  @return The document's full text content, as a single string.
#
def extract_text(path: str | Path) -> str:
    """Return the concatenated raw text of the document at 'path'.

    Dispatches on the file extension. Raises 'UnsupportedFileType' for
    anything outside 'SUPPORTED_EXTENSIONS' so callers can map it to an HTTP
    400 rather than crashing.
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")

    raise UnsupportedFileType(
        f"Unsupported file type '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}"
    )

## @fn _extract_pdf(path)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Extract text from a PDF file, one page at a time.
#  @param path Filesystem path to the PDF document.
#  @return The concatenated text of every page, joined by newlines.
#
def _extract_pdf(path: Path) -> str:
    """Extract text from a PDF, one page at a time, joined by newlines.

    pdfplumber is imported lazily so that installing/​using the .txt and
    .docx paths does not require the PDF stack to be importable.
    """
    import pdfplumber

    parts: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            # extract_text() returns None for an empty/image-only page; guard it.
            parts.append(page.extract_text() or "")
    return "\n".join(parts)

## @fn _extract_docx(path)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Extract text from a Word (.docx) file.
#  @param path Filesystem path to the DOCX document.
#  @return The concatenated text of every paragraph, joined by newlines.
#
def _extract_docx(path: Path) -> str:
    """Extract text from a .docx by joining every paragraph with a newline."""
    import docx  # python-docx; imported lazily (see _extract_pdf)

    document = docx.Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)
