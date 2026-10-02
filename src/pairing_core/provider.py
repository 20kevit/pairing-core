"""Engine provider contract (F4 foundation).

PUBLIC. Rules (O01/O03, ENGINE_ABSTRACTION.md, blueprint D):

- One interface for native and future external engines. No BBP/JaVaFo/TRF/
  subprocess structures here — those belong to future adapters (F4 forbids
  them). This module imports errors/rulesets/envelope only (stdlib otherwise).
- EngineProvider is an ABC: identity (provider_id/engine_version), capability
  declaration, support check, and pair(). supports() is a pure deterministic
  predicate; pair() runs the engine and returns an F3 RoundPairing success
  value (O02 applies to every implementor).
- Capability fields are minimal and justified: supported rulesets (routing),
  forced/forbidden/bye constraint flags (O03 honesty about what an engine
  honours), deterministic flag (reproducibility contract). No seeds, budgets,
  modes, TRF dialects, or team/RR flags — those arrive with the engines and
  phases that need them (F4 rule 4: no speculative matrix).
- No fallback lives here: selection is the registry's explicit job (F4-S3);
  providers never substitute each other.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

from pairing_core.envelope import RoundPairing
from pairing_core.rulesets import ConstraintSet, RulesetId


@dataclass(frozen=True)
class EngineMetadata:
    """PUBLIC. Stable provider identity (NOT a capability, NOT a version
    of anything else — see VERSIONING.md five axes)."""
    provider_id: str
    engine_version: str


@dataclass(frozen=True)
class Capability:
    """PUBLIC. Explicit, deterministic capability declaration.

    rulesets: exact RulesetIds the engine implements (routing basis).
    supports_forced_pairs / supports_forbidden_pairs /
    supports_bye_directives: which ConstraintSet dimensions are honoured
        (anything else must raise UnsupportedCapabilityError, never ignore).
    deterministic: same request -> byte-identical result (contract term).
    """
    rulesets: Tuple[RulesetId, ...] = ()
    supports_forced_pairs: bool = False
    supports_forbidden_pairs: bool = False
    supports_bye_directives: bool = False
    deterministic: bool = True


class EngineProvider(ABC):
    """PUBLIC. Stable engine interface: identity + capabilities + pair."""

    @property
    @abstractmethod
    def metadata(self) -> EngineMetadata:
        """Stable identity. Must be constant for the provider's lifetime."""
        raise NotImplementedError

    @property
    def provider_id(self) -> str:
        """Convenience: metadata().provider_id."""
        return self.metadata.provider_id

    @property
    def engine_version(self) -> str:
        """Convenience: metadata().engine_version."""
        return self.metadata.engine_version

    @property
    @abstractmethod
    def capabilities(self) -> Capability:
        """Declared capabilities. Must be constant for the provider's
        lifetime (registry decisions depend on it)."""
        raise NotImplementedError

    def supports(self, ruleset: RulesetId,
                 constraints: ConstraintSet) -> bool:
        """Pure deterministic predicate: can this provider honour this
        (ruleset, constraints) combination? Default implementation checks
        the declared capability; providers with narrower real limits MUST
        override (never claim-and-ignore)."""
        caps = self.capabilities
        if ruleset not in caps.rulesets:
            return False
        if constraints.forced_pairs and not caps.supports_forced_pairs:
            return False
        if constraints.forbidden_pairs and not caps.supports_forbidden_pairs:
            return False
        if constraints.bye_directive is not None and \
                not caps.supports_bye_directives:
            return False
        return True

    @abstractmethod
    def pair(self, request: object) -> RoundPairing:
        """Run the engine for request (EngineRequest) -> RoundPairing.

        Contract: validate (F2 typed errors), execute, return complete
        success value (O02 — partials unrepresentable). Failures use the
        F2 taxonomy; providers MUST NOT substitute other engines/rulesets.
        """
        raise NotImplementedError


class NativeDutchProvider(EngineProvider):
    """PUBLIC. The frozen v0.1.0 kernel as an EngineProvider (F4-S2).

    A thin guarded wrapper — NOT a second pairing implementation (F4 rule 2):
    support-gating here, execution delegated to the F3 seam (pair_detailed),
    which runs the unmodified kernel. Ruleset identity stays honest:
    dutch-till2026-compat only, never relabelled (F4 boundary).
    """

    @property
    def metadata(self) -> EngineMetadata:
        from pairing_core import __version__ as lib_version

        return EngineMetadata(provider_id="native-dutch",
                              engine_version=lib_version)

    @property
    def capabilities(self) -> Capability:
        from pairing_core.rulesets import (
            DUTCH_TILL2026_COMPAT,
            resolve_ruleset,
        )

        return Capability(
            rulesets=(resolve_ruleset(DUTCH_TILL2026_COMPAT),),
            supports_forced_pairs=True,
            supports_forbidden_pairs=True,
            supports_bye_directives=False,
            deterministic=True,
        )

    def pair(self, request: object) -> RoundPairing:
        from pairing_core.api import EngineRequest, pair_detailed
        from pairing_core.errors import UnsupportedCapabilityError
        from pairing_core.rulesets import ConstraintSet, resolve_ruleset

        if not isinstance(request, EngineRequest):
            # Delegate: F2 boundary raises the precise InvalidRequestError.
            return pair_detailed(request)
        constraints = request.constraints
        if constraints is None:
            constraints = ConstraintSet()
        if isinstance(constraints, ConstraintSet):
            resolved = resolve_ruleset(request.ruleset)
            if not self.supports(resolved, constraints):
                raise UnsupportedCapabilityError(
                    "native-dutch cannot honour these constraints "
                    "(refusing, not ignoring).")
        return pair_detailed(request)
