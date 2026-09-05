"""Captals metabolism API.

Keeps the legacy Ω-Capitals market surface intact while exposing the newer
Captals metabolic model as a separate, governed layer.
"""

from fastapi import APIRouter

from services.captals_metabolism import (
    CapitalDimension,
    CostDimension,
    LegacyOmegaNormalization,
    LegacyOmegaSnapshot,
    MetabolicEvaluation,
    MetabolicEvent,
    evaluate_metabolism,
    normalize_legacy_omega,
)

router = APIRouter()


@router.get("/schema")
async def get_captals_schema():
    """Return the canonical dimensions without collapsing them into one score."""
    return {
        "canonical_name": "Captals",
        "role": "multidimensional value/resource metabolism",
        "legacy_surface": "Omega Capitals (Ω-Capitals)",
        "capital_dimensions": [dimension.value for dimension in CapitalDimension],
        "cost_dimensions": [dimension.value for dimension in CostDimension],
        "invariants": [
            "trust != value != price != capital",
            "omega_score_is_legacy_market_context_only",
            "captals_does_not_decide_scientific_truth",
            "no_cross_dimension_scalarization_without_explicit_instrument",
            "gate_evidence_and_replay_are_external_inputs",
        ],
    }


@router.post("/evaluate", response_model=MetabolicEvaluation)
async def evaluate_captals_event(event: MetabolicEvent):
    """Evaluate an instrumented capital/resource transition."""
    return evaluate_metabolism(event)


@router.post("/legacy/omega", response_model=LegacyOmegaNormalization)
async def normalize_omega_snapshot(snapshot: LegacyOmegaSnapshot):
    """Normalize a legacy Ω-Capitals signal without promoting it to trust/gate."""
    return normalize_legacy_omega(snapshot)
