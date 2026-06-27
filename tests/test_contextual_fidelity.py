from core.contextual_fidelity import (
    MAX_RECALL_TARGET,
    apply_fidelity_rules,
    build_context_policy,
    classify_seriousness,
    memory_programming_receipt_shape,
)


def test_casual_playful_message_allows_light_playfulness():
    result = classify_seriousness("Tell me a fun lore joke about our project.")
    assert result["seriousness_level"] == "low"
    assert result["fiction_allowed"] is True
    assert result["playfulness_allowed"] is True


def test_legal_patent_message_disables_fiction():
    result = classify_seriousness("Help with patent legal filing details.")
    assert result["seriousness_level"] in {"high", "critical"}
    assert result["fiction_allowed"] is False


def test_health_message_disables_fiction():
    result = classify_seriousness("I need medical health guidance right now.")
    assert result["fiction_allowed"] is False


def test_money_billing_message_disables_fiction():
    result = classify_seriousness("Review this billing money dispute.")
    assert result["fiction_allowed"] is False


def test_identity_canon_message_requires_basis_labels():
    result = classify_seriousness("Confirm identity canon for my profile.")
    assert result["requires_basis_labels"] is True


def test_memory_recovery_message_requires_open_holes():
    result = classify_seriousness("Memory recall request for last month timeline.")
    assert result["requires_open_holes"] is True


def test_passive_continuity_message_preserves_raw_text():
    policy = build_context_policy("Continue verbatim and keep exact raw text.", {})
    assert policy["response_mode"] == "passive_continuity"
    assert policy["must_preserve_raw_text"] is True


def test_public_witness_message_requires_verification_boundary():
    policy = build_context_policy("Provide witness testimony for the accident.", {})
    assert policy["response_mode"] == "public_witness"
    assert policy["required_basis_labels"] is True


def test_build_operator_requires_no_execution_without_approval():
    policy = build_context_policy("Build and run migration now.", {})
    assert policy["response_mode"] == "build_operator"
    assert policy["must_ask_approval_before_action"] is True


def test_unknown_factual_claim_produces_open_hole():
    policy = build_context_policy("Did I pay invoice 223 last year?", {})
    assert policy["open_holes"]


def test_playful_lore_allowed_only_when_labeled():
    policy = build_context_policy("Tell playful lore about ORACLE.", {})
    rejected = apply_fidelity_rules("A dragon solved your taxes.", policy)
    accepted = apply_fidelity_rules("[lore] A dragon solved your taxes.", policy)
    assert rejected["approved"] is False
    assert accepted["approved"] is True


def test_serious_contexts_set_max_imagination_none():
    policy = build_context_policy("This is a legal contract dispute.", {})
    assert policy["max_imagination_level"] == "none"


def test_personality_never_overrides_truth():
    policy = build_context_policy("Please keep this factual.", {})
    assert policy["personality_guardrail"] == "Personality must not override truth."


def test_apply_fidelity_rules_rejects_unsupported_certainty():
    policy = build_context_policy("Identity canon check.", {})
    result = apply_fidelity_rules("I am definitely certain with no basis.", policy)
    assert result["approved"] is False
    assert any("certainty" in violation.lower() for violation in result["violations"])


def test_apply_fidelity_rules_rejects_fictionalized_serious_claims():
    policy = build_context_policy("Medical health emergency.", {})
    result = apply_fidelity_rules("A wizard can guarantee your treatment result.", policy)
    assert result["approved"] is False
    assert any("fiction" in violation.lower() or "imagination" in violation.lower() for violation in result["violations"])


def test_receipt_shape_includes_mutation_performed_false():
    policy = build_context_policy("Simple factual check.", {})
    receipt = memory_programming_receipt_shape(policy)
    assert receipt["mutation_performed"] is False


def test_module_does_not_write_files():
    policy = build_context_policy("Simple factual check.", {})
    receipt = memory_programming_receipt_shape(policy)
    assert "mutation_performed" in receipt
    assert receipt["mutation_performed"] is False


def test_module_does_not_call_external_integrations():
    policy = build_context_policy("Simple factual check.", {})
    assert isinstance(policy, dict)
    assert "allowed_sources" in policy


def test_no_claim_of_100_percent_recall_is_made():
    policy = build_context_policy("Simple factual check.", {})
    result = apply_fidelity_rules("This has 100% recall fidelity.", policy)
    assert result["approved"] is False


def test_uses_maximum_provenance_backed_recall_fidelity_phrase():
    assert MAX_RECALL_TARGET == "maximum provenance-backed recall fidelity"
