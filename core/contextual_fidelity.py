"""Contextual Fidelity Engine (Phase 2.0).

Program the AI with provenance, not prompts.
"""

from __future__ import annotations

from typing import Any

MAX_RECALL_TARGET = "maximum provenance-backed recall fidelity"

_LEGAL_TERMS = {"legal", "patent", "lawsuit", "contract", "court", "attorney"}
_HEALTH_TERMS = {
    "medical",
    "health",
    "diagnosis",
    "symptom",
    "medication",
    "doctor",
    "self-harm",
    "suicide",
    "crisis",
}
_FINANCIAL_TERMS = {"money", "billing", "bill", "taxes", "tax", "invoice", "payment", "bank"}
_IDENTITY_TERMS = {"identity", "credentials", "password", "api key", "api keys", "token", "canon"}
_ACTION_TERMS = {"send email", "sending emails", "delete", "deleting files", "publish", "external publication"}
_PUBLIC_WITNESS_TERMS = {"testimony", "witness", "public statement", "accident"}
_MEMORY_TERMS = {"memory", "recall", "remember", "canon", "timeline", "receipt"}
_PLAY_TERMS = {"joke", "fun", "play", "myth", "lore", "story", "improv"}
_BUILD_TERMS = {"build", "deploy", "run", "execute", "migration", "operator"}
_PASSIVE_CONTINUITY_TERMS = {"continue", "as-is", "verbatim", "raw text", "do not rewrite", "keep exact"}
_SUPPORTIVE_TERMS = {"grief", "vulnerable", "support", "overwhelmed", "tired"}


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _pick_mode(text: str, seriousness_level: str) -> str:
    if _contains_any(text, _LEGAL_TERMS):
        return "legal_boundary"
    if _contains_any(text, _HEALTH_TERMS):
        return "health_boundary"
    if _contains_any(text, _FINANCIAL_TERMS):
        return "financial_boundary"
    if _contains_any(text, _PUBLIC_WITNESS_TERMS):
        return "public_witness"
    if _contains_any(text, _PASSIVE_CONTINUITY_TERMS):
        return "passive_continuity"
    if _contains_any(text, _BUILD_TERMS):
        return "build_operator"
    if _contains_any(text, _MEMORY_TERMS):
        return "memory_recovery"
    if _contains_any(text, _SUPPORTIVE_TERMS):
        return "grounded_supportive"
    if _contains_any(text, _PLAY_TERMS):
        return "playful_lore"
    if seriousness_level in {"high", "critical"}:
        return "serious_factual"
    return "uncertain_hole_preserving"


def classify_seriousness(message: str, context: dict | None = None) -> dict:
    text = (message or "").lower()
    context = context or {}

    critical = _contains_any(text, {"self-harm", "suicide", "crisis"}) or _contains_any(
        text, {"api key", "credentials", "account password"}
    )
    high = (
        _contains_any(text, _LEGAL_TERMS | _HEALTH_TERMS | _FINANCIAL_TERMS | _IDENTITY_TERMS | _ACTION_TERMS)
        or _contains_any(text, _PUBLIC_WITNESS_TERMS)
        or bool(context.get("high_stakes", False))
    )
    playful = _contains_any(text, _PLAY_TERMS)

    if critical:
        seriousness_level = "critical"
    elif high:
        seriousness_level = "high"
    elif playful:
        seriousness_level = "low"
    else:
        seriousness_level = "medium"

    fiction_allowed = seriousness_level in {"low", "medium"} and not high
    playfulness_allowed = seriousness_level in {"low", "medium"} and not high
    requires_basis_labels = seriousness_level in {"high", "critical"} or _contains_any(text, {"identity", "canon"})
    requires_open_holes = _contains_any(text, {"memory", "recall", "canon"}) or context.get("requires_open_holes", False)
    mode_recommendation = _pick_mode(text, seriousness_level)

    reason = (
        f"Classified as {seriousness_level}; mode {mode_recommendation}; "
        f"aligned to {MAX_RECALL_TARGET}."
    )

    return {
        "seriousness_level": seriousness_level,
        "fiction_allowed": fiction_allowed,
        "playfulness_allowed": playfulness_allowed,
        "requires_basis_labels": requires_basis_labels,
        "requires_open_holes": bool(requires_open_holes),
        "mode_recommendation": mode_recommendation,
        "reason": reason,
    }


def _compute_recall_confidence(available_context: dict) -> str:
    basis = available_context.get("source_backed_facts", [])
    receipts = available_context.get("redink_receipts", [])
    files = available_context.get("user_files", [])
    score = len(basis) + len(receipts) + len(files)
    if score >= 5:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def _extract_open_holes(user_message: str, available_context: dict, mode: str) -> list[str]:
    holes = list(available_context.get("open_holes", []))
    text = (user_message or "").lower()
    unknown_factual = any(text.startswith(prefix) for prefix in ("did ", "was ", "were ", "have ", "has ")) or "?" in text
    if mode == "memory_recovery":
        unknown_factual = True
    if unknown_factual and not available_context.get("source_backed_facts"):
        holes.append("Insufficient source-backed evidence for requested factual recall.")
    # preserve insertion order with dedupe
    seen: set[str] = set()
    unique: list[str] = []
    for hole in holes:
        if hole not in seen:
            seen.add(hole)
            unique.append(hole)
    return unique


def build_context_policy(user_message: str, available_context: dict) -> dict:
    seriousness = classify_seriousness(user_message, context=available_context)
    mode = seriousness["mode_recommendation"]
    text = (user_message or "").lower()

    required_basis_labels = seriousness["requires_basis_labels"] or mode in {
        "memory_recovery",
        "public_witness",
        "legal_boundary",
        "health_boundary",
        "financial_boundary",
    }
    open_holes = _extract_open_holes(user_message, available_context, mode)

    if seriousness["seriousness_level"] in {"high", "critical"}:
        max_imagination_level = "none"
    elif mode == "playful_lore":
        max_imagination_level = "mythic_labeled"
    else:
        max_imagination_level = "light"

    allowed_sources = [
        key
        for key in (
            "source_backed_facts",
            "user_files",
            "redink_receipts",
            "durable_memory",
            "active_agenda",
            "open_holes",
            "user_preferences",
            "identity_anchors",
        )
        if available_context.get(key) is not None
    ]
    if not allowed_sources:
        allowed_sources = ["user_message_only"]

    must_preserve_raw_text = mode in {"passive_continuity", "memory_recovery"}
    must_avoid_smoothing = must_preserve_raw_text or mode == "public_witness"
    must_ask_approval_before_action = mode == "build_operator" or _contains_any(text, _ACTION_TERMS)

    policy_mode = mode if open_holes or mode != "uncertain_hole_preserving" else "uncertain_hole_preserving"
    if mode == "playful_lore" and seriousness["seriousness_level"] in {"high", "critical"}:
        policy_mode = "serious_factual"

    return {
        "response_mode": policy_mode,
        "allowed_sources": allowed_sources,
        "required_basis_labels": bool(required_basis_labels),
        "max_imagination_level": max_imagination_level,
        "must_preserve_raw_text": must_preserve_raw_text,
        "must_avoid_smoothing": must_avoid_smoothing,
        "must_ask_approval_before_action": must_ask_approval_before_action,
        "recall_confidence": _compute_recall_confidence(available_context),
        "open_holes": open_holes,
        "fidelity_target": MAX_RECALL_TARGET,
        "personality_guardrail": "Personality must not override truth.",
    }


def apply_fidelity_rules(draft_response: str, policy: dict) -> dict:
    text = (draft_response or "").lower()
    violations: list[str] = []

    serious_mode = policy.get("response_mode") in {
        "serious_factual",
        "legal_boundary",
        "health_boundary",
        "financial_boundary",
        "public_witness",
    }

    unsupported_certainty_terms = ("definitely", "certainly", "100% sure", "guaranteed")
    if any(term in text for term in unsupported_certainty_terms) and policy.get("required_basis_labels", False):
        violations.append("Unsupported certainty without explicit basis labels.")

    fictional_terms = ("dragon", "wizard", "mythic", "made up", "imagined")
    labeled_play = "[play]" in text or "[fiction]" in text or "[lore]" in text
    if serious_mode and any(term in text for term in fictional_terms):
        violations.append("Fictionalized content in serious context is not allowed.")
    if policy.get("max_imagination_level") == "none" and any(term in text for term in fictional_terms):
        violations.append("Imagination exceeds allowed level for this policy.")
    if policy.get("response_mode") == "playful_lore" and any(term in text for term in fictional_terms) and not labeled_play:
        violations.append("Playful lore content must be explicitly labeled.")

    if "100% recall fidelity" in text:
        violations.append("Disallowed absolute recall claim detected.")

    approved = not violations
    guidance = (
        "Ground each claim with basis labels, preserve open holes when evidence is missing, "
        "and keep imagination within policy limits."
    )

    return {
        "approved": approved,
        "violations": violations,
        "corrected_guidance": guidance,
    }


def memory_programming_receipt_shape(policy: dict) -> dict:
    return {
        "engine": "contextual_fidelity",
        "fidelity_target": MAX_RECALL_TARGET,
        "response_mode": policy.get("response_mode"),
        "required_basis_labels": bool(policy.get("required_basis_labels", False)),
        "open_holes": list(policy.get("open_holes", [])),
        "recall_confidence": policy.get("recall_confidence"),
        "mutation_performed": False,
    }
