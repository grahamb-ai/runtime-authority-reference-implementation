## @file specs.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Specs router: upload a policy document, extract its rules, and persist them.
#
"""Specs router : upload, parse, and extract supported policy documents.

Exposes POST /api/v1/specs/upload. This is the composition point for the
ingestion flow: it wires the transport (FastAPI upload) to the engines (parser +
extractor) and the database (persist the rules), and returns a summary of what
was extracted.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, delete

from app.database import get_session
from app.engines.extractor import extract_rules
from app.engines.parser import SUPPORTED_EXTENSIONS, UnsupportedFileType, extract_text
from app.enums import RuleType
from app.models.rule import Rule
from app.models.schemas import ExtractedRule, UploadSummary

router = APIRouter(prefix="/api/v1/specs", tags=["specs"])


@router.post("/upload", response_model=UploadSummary, summary="Upload and parse a policy document")
## @fn upload_spec(file, session)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Parse an uploaded PDF/DOCX/TXT policy file, extract its rules, and persist them.
#  @param file The uploaded policy document.
#  @param session The active database session.
#  @return An UploadSummary reporting how many rules were extracted, by type.
#
def upload_spec(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> UploadSummary:
    """Parse a PDF/DOCX/TXT policy file, extract its rules, and persist them."""
    # Reject unsupported extensions up front with a clear 400.
    filename = file.filename or "uploaded"
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    # The parsers work on file paths, so stream the upload to a temporary file.
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path)
    except UnsupportedFileType as exc:
        # Defensive: extract_text re-validates the extension.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        # Always clean up the temp file, even if parsing raised.
        Path(tmp_path).unlink(missing_ok=True)

    # Deterministic extraction.
    extracted = extract_rules(text, source_document=filename)

    # De-duplicate the incoming batch: a policy document may repeat a rule, and
    # identical rules would otherwise produce identical duplicate checks at
    # evaluation time. Two rules are "the same" if they match on the fields that
    # drive a decision.
    seen: set = set()
    unique = []
    for r in extracted:
        value_key = tuple(r.value) if isinstance(r.value, list) else r.value
        key = (r.rule_type, r.action, r.attribute, value_key, r.subject, r.threshold)
        if key not in seen:
            seen.add(key)
            unique.append(r)

    # Replace semantics: binding a policy REPLACES the active rule set rather
    # than appending to it. This matches the console's "one policy bound at a
    # time" model and prevents rules from accumulating across repeated uploads.
    session.exec(delete(Rule))

    rows = [Rule.from_data(r) for r in unique]
    for row in rows:
        session.add(row)
    session.commit()
    for row in rows:
        session.refresh(row)  # reload server-assigned ids

    # Build the summary counts and echo the extracted rules back to the caller.
    authority_count = sum(1 for r in rows if r.rule_type == RuleType.AUTHORITY.value)
    admissibility_count = sum(1 for r in rows if r.rule_type == RuleType.ADMISSIBILITY.value)

    return UploadSummary(
        source_document=filename,
        authority_rules=authority_count,
        admissibility_rules=admissibility_count,
        total_rules=len(rows),
        rules=[
            ExtractedRule(
                rule_type=r.rule_type,
                action=r.action,
                attribute=r.attribute,
                operator=r.operator,
                value=r.value,
                subject=r.subject,
                threshold=r.threshold,
                source_excerpt=r.source_excerpt,
            )
            for r in rows
        ],
    )
