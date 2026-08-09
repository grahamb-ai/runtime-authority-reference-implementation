## @file extractor.py
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Deterministic, regex-based extraction of policy rules from raw text (not an LLM).
#
"""Deterministic rule extraction from raw policy text.

This is NOT an LLM. Every rule is produced by matching one of a defined
catalogue of sentence patterns with regular expressions. Any sentence that does
not match a known pattern is simply ignored.

POC assumption (documented in the README)
-----------------------------------------
Policy documents are expected to use these recognisable phrasings. Arbitrary
prose is not understood. Widening the catalogue — or, later, swapping in an
LLM-assisted extractor behind this same ``extract_rules`` signature — is the
natural Phase-2 upgrade. The rest of the system depends only on the function
signature, not on how the rules are obtained.

Pattern catalogue
-----------------
Authority
  A1  Authorized roles for <action>: <role>, <role>, ...
  A2  The <role> (is authorized to | may) (approve|release|sign off on)
      <action> up to <amount>.
Admissibility
  B1  (Any|All) <action> (above|over|exceeding) <amount>
      (must be accompanied by | requires) <doc>, <doc> and <doc>.
  B2  <action> requires <doc>, <doc>.        (unconditional; threshold = 0)
"""

from __future__ import annotations

import re

from app.enums import RuleType
from app.engines.types import RuleData

# --------------------------------------------------------------------------- #
# Reusable sub-patterns
# --------------------------------------------------------------------------- #
# An action or dotted identifier, e.g. "payment.release". The dot is allowed
# INSIDE the token; the sentence splitter (below) makes sure we never break on it.
_ACTION = r"[A-Za-z][\w.]*"
# A number possibly containing thousands separators, e.g. "1,000,000".
_AMOUNT = r"[\d][\d,]*"
# A free-text run up to the next period/newline: a roles list or a docs list.
_DOCS = r"[^.\n]+"

# --------------------------------------------------------------------------- #
# Compiled patterns (case-insensitive). Order of application is A1, A2, B1, B2.
# --------------------------------------------------------------------------- #
A1 = re.compile(  # "Authorized roles for <action>: <roles>"
    rf"authorized roles(?:\s+for\s+(?P<action>{_ACTION}))?\s*:\s*(?P<roles>{_DOCS})",
    re.IGNORECASE,
)
A2 = re.compile(  # "The <role> may approve <action> up to <amount>"
    rf"the\s+(?P<role>\w+)\s+(?:is authorized to|may)\s+"
    rf"(?:approve|release|sign off on)\s+(?P<action>{_ACTION})\s+"
    rf"up to\s+[$€£]?\s?(?P<amount>{_AMOUNT})",
    re.IGNORECASE,
)
B1 = re.compile(  # "Any <action> above <amount> must be accompanied by <docs>"
    rf"(?:any|all)\s+(?P<action>{_ACTION})\s+(?:above|over|exceeding)\s+"
    rf"[$€£]?\s?(?P<amount>{_AMOUNT})(?:\s*(?:eur|usd|gbp|euros?|dollars?|pounds?))?\s+"
    rf"(?:must be accompanied by|requires?)\s+(?P<docs>{_DOCS})",
    re.IGNORECASE,
)
B2 = re.compile(  # "<action> requires <docs>" (unconditional)
    rf"(?P<action>{_ACTION})\s+requires?\s+(?P<docs>{_DOCS})",
    re.IGNORECASE,
)

## @fn _to_amount(raw)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Parse a formatted amount string into a plain float.
#  @param raw The amount as written in the policy text, e.g. '100,000'.
#  @return The numeric value with thousands separators removed.
#
def _to_amount(raw: str) -> float:
    """Parse '100,000' -> 100000.0 (strip thousands separators)."""
    return float(raw.replace(",", "").strip())

## @fn _split_tokens(raw)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Split a comma / 'and' / '&' separated list into clean lowercase tokens.
#  @param raw The raw list text, e.g. 'invoice and purchase_order'.
#  @return A list of individual, trimmed, lowercased tokens.
#
def _split_tokens(raw: str) -> list[str]:
    """Split a comma / 'and' / '&' separated list into clean lowercase tokens.

    Used for both roles ("a, b and c") and document lists
    ("invoice and purchase_order").
    """
    # Normalise the separators: turn the word "and" and "&" into commas...
    cleaned = re.sub(r"\b(and)\b", ",", raw, flags=re.IGNORECASE).replace("&", ",")
    # ...then split, trim surrounding punctuation/whitespace, and lowercase.
    tokens = [t.strip(" .\t").lower() for t in cleaned.split(",")]
    return [t for t in tokens if t]

## @fn _sentences(text)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Split raw text into candidate sentences for pattern matching.
#  @param text The raw policy text to split.
#  @return A list of sentence strings, without breaking dotted identifiers such as 'payment.release'.
#
def _sentences(text: str) -> list[str]:
    """Split text into candidate sentences.

    Splits on newlines and on sentence-ending periods (a period followed by
    whitespace or end-of-line), but NOT on periods inside dotted identifiers
    such as 'payment.release' (which would otherwise be broken in two).
    """
    sentences: list[str] = []
    for line in text.split("\n"):
        # (?=\s|$) = period is a sentence end only if followed by space or EOL.
        for part in re.split(r"\.(?=\s|$)", line):
            part = part.strip()
            if part:
                sentences.append(part)
    return sentences

## @fn extract_rules(text, source_document)
#  @author FlowSignal Dev Team
#  @version 0.1
#  @date 25 July 2026
#  @brief Extract structured rules from raw policy text using deterministic patterns.
#  @param text The raw policy text to scan for recognizable rule sentences.
#  @param source_document Name of the source document, recorded on each extracted rule for traceability.
#  @return A list of RuleData extracted from the text (empty if nothing matched).
#
def extract_rules(text: str, source_document: str = "") -> list[RuleData]:
    """Extract a list of :class:`RuleData` from raw policy ``text``.

    Each sentence is tested against the patterns in priority order A1, A2, B1,
    B2; the first pattern that matches a sentence wins (``continue``). This
    priority guarantees a conditional "above X requires ..." (B1) is never also
    captured as an unconditional "requires ..." (B2).

    Note: 'RuleData.id' is left blank here -> ids are assigned when the rows are
    written to the database (or, in tests, injected manually).
    """
    rules: list[RuleData] = []

    for sentence in _sentences(text):
        # Preserve a tidy excerpt (with a trailing period) for the audit trail.
        excerpt = sentence if sentence.endswith(".") else sentence + "."

        # --- A1: authorized roles list -> one authority rule per role ------- #
        m = A1.search(sentence)
        if m:
            # An "Authorized roles" sentence without an explicit "for <action>"
            # is ambiguous: we cannot know which action it governs. Rather than
            # emit a dangerous wildcard rule that would authorize a role for
            # ANY action, we skip it — consistent with "when in doubt, don't
            # extract". The coverage guard in the evaluator then ensures such
            # uncovered actions REFUSE instead of silently passing.
            if m.group("action"):
                action = m.group("action").lower()
                for role in _split_tokens(m.group("roles")):
                    rules.append(
                        RuleData(
                            id="",
                            rule_type=RuleType.AUTHORITY.value,
                            action=action,
                            attribute="authorized_role",
                            operator="in",
                            value=role,
                            subject=role,
                            source_document=source_document,
                            source_excerpt=excerpt,
                        )
                    )
            continue

        # --- A2: per-role monetary ceiling ---------------------------------- #
        m = A2.search(sentence)
        if m:
            rules.append(
                RuleData(
                    id="",
                    rule_type=RuleType.AUTHORITY.value,
                    action=m.group("action").lower(),
                    attribute="max_amount",
                    operator="<=",
                    value=_to_amount(m.group("amount")),
                    subject=m.group("role").lower(),
                    source_document=source_document,
                    source_excerpt=excerpt,
                )
            )
            continue

        # --- B1: conditional evidence requirement (above a threshold) ------- #
        m = B1.search(sentence)
        if m:
            rules.append(
                RuleData(
                    id="",
                    rule_type=RuleType.ADMISSIBILITY.value,
                    action=m.group("action").lower(),
                    attribute="required_evidence",
                    operator="requires",
                    value=_split_tokens(m.group("docs")),
                    threshold=_to_amount(m.group("amount")),
                    source_document=source_document,
                    source_excerpt=excerpt,
                )
            )
            continue

        # --- B2: unconditional evidence requirement (threshold 0) ----------- #
        m = B2.search(sentence)
        if m:
            rules.append(
                RuleData(
                    id="",
                    rule_type=RuleType.ADMISSIBILITY.value,
                    action=m.group("action").lower(),
                    attribute="required_evidence",
                    operator="requires",
                    value=_split_tokens(m.group("docs")),
                    threshold=0.0,
                    source_document=source_document,
                    source_excerpt=excerpt,
                )
            )
            continue

    return rules
