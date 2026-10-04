"""Custom provider example (public API only).

Shows how a third party adds an engine WITHOUT touching pairing-core:
implement EngineProvider, declare honest Capability, register in a
Registry, select explicitly via pair_via. No auto-discovery, no fallback,
no core changes.

The example provider delegates execution to the native kernel (the way
an external-engine adapter would delegate to its binary) but refuses
bye directives it cannot honour — declared limits are enforced, never
silently ignored.

Usage: python3 examples/custom_provider.py
"""

from pairing_core import (
    Capability,
    EngineMetadata,
    EngineProvider,
    EngineRequest,
    PlayerData,
    Registry,
    RoundPairing,
    create_default_registry,
    pair_detailed,
    pair_via,
)
from pairing_core.errors import UnsupportedCapabilityError
from pairing_core.rulesets import (
    DUTCH_TILL2026_COMPAT,
    ConstraintSet,
    resolve_ruleset,
)


class DelegatingProvider(EngineProvider):
    """Minimal external provider: honest capability, delegated execution."""

    def __init__(self) -> None:
        self._meta = EngineMetadata(provider_id="demo-delegating",
                                    engine_version="0.1")
        self._caps = Capability(
            rulesets=(resolve_ruleset(DUTCH_TILL2026_COMPAT),),
            supports_forced_pairs=True,
            supports_forbidden_pairs=True,
            supports_bye_directives=False,  # refused, never ignored
            deterministic=True,
        )

    @property
    def metadata(self) -> EngineMetadata:
        return self._meta

    @property
    def capabilities(self) -> Capability:
        return self._caps

    def pair(self, request: EngineRequest) -> RoundPairing:
        resolved = resolve_ruleset(request.ruleset)
        constraints = request.constraints or ConstraintSet()
        if not self.supports(resolved, constraints):
            raise UnsupportedCapabilityError(
                "demo-delegating cannot honour these constraints "
                "(refusing, not ignoring).")
        return pair_detailed(request)


def main() -> None:
    players = [PlayerData(id=i, pairing_no=i, rating=2000 - i * 10,
                          points=0.0) for i in range(1, 7)]
    request = EngineRequest(players=players,
                            ruleset=DUTCH_TILL2026_COMPAT,
                            round_number=1,
                            constraints=ConstraintSet())

    registry = create_default_registry()
    registry.register(DelegatingProvider())

    result = pair_via("demo-delegating", request, registry)
    print(f"engine: {result.engine_id} (requested demo-delegating)")
    for board in result.pairings:
        print(f"board {board.board}: {board.white_id} (white)"
              f" vs {board.black_id} (black)")

    # Unknown provider ids fail loudly — substitution is unrepresentable.
    try:
        pair_via("no-such-provider", request, registry)
    except Exception as exc:  # InvalidRequestError
        print(f"typed error (expected): {type(exc).__name__}: {exc}")

    # A registry contains exactly what was registered — nothing hidden.
    print(f"registry holds: {list(registry.providers())}")


if __name__ == "__main__":
    main()
