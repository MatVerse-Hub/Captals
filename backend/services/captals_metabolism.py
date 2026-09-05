"""Captals metabolic domain model.

This module fuses the legacy Ω-Capitals market/DeFi lineage with the
newer Captals role as a multidimensional metabolism of value and resources.

Important invariants:
- trust != value != price != capital;
- Ω-Score is a legacy market/risk signal, not a truth or authorization gate;
- dimensions are not collapsed into a scalar without an explicit instrument;
- Captals consumes external admissibility/evidence/replay states and does not
  decide scientific truth by itself.
"""

from __future__ import annotations

from enum import Enum
from math import isfinite
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class CapitalDimension(str, Enum):
    FINANCIAL = "financial"
    INFORMATIONAL = "informational"
    SCIENTIFIC = "scientific"
    TECHNOLOGICAL = "technological"
    HUMAN = "human"
    RELATIONAL = "relational"
    OPERATIONAL = "operational"


class CostDimension(str, Enum):
    COMPUTATIONAL = "computational"
    ENERGY = "energy"
    TIME = "time"
    MEMORY = "memory"
    RISK = "risk"
    HUMAN = "human"
    COGNITIVE = "cognitive"
    INSTITUTIONAL = "institutional"
    DEBT = "debt"


class MetricObservation(BaseModel):
    value: float
    unit: str = Field(min_length=1)
    instrument: str = Field(min_length=1)

    @field_validator("value")
    @classmethod
    def finite_value(cls, value: float) -> float:
        if not isfinite(value):
            raise ValueError("metric value must be finite")
        return value


class BudgetLimit(BaseModel):
    max_value: float = Field(ge=0)
    unit: str = Field(min_length=1)


class MetabolicEvent(BaseModel):
    event_id: str = Field(min_length=1)
    track_id: str = Field(min_length=1)
    milestone_id: Optional[str] = None
    m_bit_ref: Optional[str] = None
    source: str = Field(min_length=1)

    gate_decision: Literal["PASS", "HOLD", "BLOCK"]
    evidence_status: Literal["VERIFIED", "PENDING", "UNVERIFIED"]
    replay_status: Literal["EXACT_MATCH", "DIVERGENT", "NOT_AVAILABLE"]

    capital_delta: Dict[CapitalDimension, MetricObservation] = Field(default_factory=dict)
    costs: Dict[CostDimension, MetricObservation] = Field(default_factory=dict)
    budget_limits: Dict[CostDimension, BudgetLimit] = Field(default_factory=dict)

    provenance_ref: Optional[str] = None
    receipt_ref: Optional[str] = None
    legacy_omega_score: Optional[float] = None

    @field_validator("legacy_omega_score")
    @classmethod
    def finite_omega(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not isfinite(value):
            raise ValueError("legacy_omega_score must be finite")
        return value

    @model_validator(mode="after")
    def validate_budget_units(self) -> "MetabolicEvent":
        for dimension, limit in self.budget_limits.items():
            observation = self.costs.get(dimension)
            if observation is not None and observation.unit != limit.unit:
                raise ValueError(
                    f"budget unit mismatch for {dimension.value}: "
                    f"{observation.unit!r} != {limit.unit!r}"
                )
        return self


class BudgetViolation(BaseModel):
    dimension: CostDimension
    observed: float
    maximum: float
    unit: str


class MetabolicEvaluation(BaseModel):
    event_id: str
    state: Literal["ACCUMULATING", "DEGRADING", "TRADEOFF", "NEUTRAL"]
    allocation_status: Literal["ELIGIBLE", "HOLD", "INELIGIBLE"]
    reasons: List[str]
    positive_capitals: List[CapitalDimension]
    negative_capitals: List[CapitalDimension]
    budget_violations: List[BudgetViolation]
    legacy_omega_interpretation: Optional[str] = None


class LegacyOmegaSnapshot(BaseModel):
    omega_score: float
    tvl: Optional[float] = Field(default=None, ge=0)
    volume_24h: Optional[float] = Field(default=None, ge=0)
    fees_24h: Optional[float] = Field(default=None, ge=0)
    apr: Optional[float] = None
    asset_or_pool: Optional[str] = None

    @field_validator("omega_score", "apr")
    @classmethod
    def finite_optional(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not isfinite(value):
            raise ValueError("numeric value must be finite")
        return value


class LegacyOmegaNormalization(BaseModel):
    classification: Literal["LEGACY_MARKET_SIGNAL"] = "LEGACY_MARKET_SIGNAL"
    omega_score: float
    market_context: Dict[str, float]
    trust_implication: Literal["NONE"] = "NONE"
    authorization_implication: Literal["NONE"] = "NONE"
    canonical_use: Literal["CAPTALS_MARKET_CONTEXT"] = "CAPTALS_MARKET_CONTEXT"
    requires_for_allocation: List[str] = [
        "explicit_gate_decision",
        "verified_evidence",
        "replay_status",
        "instrumented_capital_delta",
    ]


def _capital_state(event: MetabolicEvent):
    positive = [d for d, obs in event.capital_delta.items() if obs.value > 0]
    negative = [d for d, obs in event.capital_delta.items() if obs.value < 0]

    if positive and not negative:
        state = "ACCUMULATING"
    elif negative and not positive:
        state = "DEGRADING"
    elif positive and negative:
        state = "TRADEOFF"
    else:
        state = "NEUTRAL"
    return state, positive, negative


def _budget_violations(event: MetabolicEvent) -> List[BudgetViolation]:
    violations: List[BudgetViolation] = []
    for dimension, limit in event.budget_limits.items():
        observation = event.costs.get(dimension)
        if observation is not None and observation.value > limit.max_value:
            violations.append(
                BudgetViolation(
                    dimension=dimension,
                    observed=observation.value,
                    maximum=limit.max_value,
                    unit=observation.unit,
                )
            )
    return violations


def evaluate_metabolism(event: MetabolicEvent) -> MetabolicEvaluation:
    state, positive, negative = _capital_state(event)
    violations = _budget_violations(event)
    reasons: List[str] = []

    if event.gate_decision == "BLOCK":
        allocation_status = "INELIGIBLE"
        reasons.append("external_gate_block")
    elif event.gate_decision == "HOLD":
        allocation_status = "HOLD"
        reasons.append("external_gate_hold")
    elif event.evidence_status != "VERIFIED":
        allocation_status = "HOLD"
        reasons.append("evidence_not_verified")
    elif event.replay_status != "EXACT_MATCH":
        allocation_status = "HOLD"
        reasons.append("replay_not_exact")
    elif violations:
        allocation_status = "INELIGIBLE"
        reasons.append("resource_budget_exceeded")
    elif state == "DEGRADING":
        allocation_status = "INELIGIBLE"
        reasons.append("capital_degradation_without_compensating_dimension")
    elif state == "NEUTRAL":
        allocation_status = "HOLD"
        reasons.append("no_instrumented_capital_change")
    else:
        allocation_status = "ELIGIBLE"
        reasons.append("admissible_instrumented_capital_change")

    legacy_interpretation = None
    if event.legacy_omega_score is not None:
        legacy_interpretation = (
            "legacy Ω-Score retained as market/risk context only; "
            "it does not imply truth, evidence, replay, or authorization"
        )

    return MetabolicEvaluation(
        event_id=event.event_id,
        state=state,
        allocation_status=allocation_status,
        reasons=reasons,
        positive_capitals=positive,
        negative_capitals=negative,
        budget_violations=violations,
        legacy_omega_interpretation=legacy_interpretation,
    )


def normalize_legacy_omega(snapshot: LegacyOmegaSnapshot) -> LegacyOmegaNormalization:
    context: Dict[str, float] = {}
    for field in ("tvl", "volume_24h", "fees_24h", "apr"):
        value = getattr(snapshot, field)
        if value is not None:
            context[field] = value

    return LegacyOmegaNormalization(
        omega_score=snapshot.omega_score,
        market_context=context,
    )
