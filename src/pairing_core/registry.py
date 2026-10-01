"""Explicit provider registry (F4 foundation).

PUBLIC. Rules (O01/O03, blueprint D, F4 registry requirements):

- Explicit registration, explicit lookup, deterministic behavior. NO
  auto-discovery (no filesystem scans, package imports, executable probes),
  NO defaults, NO fallback, NO ranking/best-provider policy. If no
  registered provider satisfies a request, resolution fails with a typed
  error — substitution is architecturally unrepresentable here.
- Duplicate registration: same object re-registered is a no-op (idempotent);
  a DIFFERENT object under an existing id raises InvalidRequestError
  (silent overwrite would break stable provider identity).
- Resolution ladder (deterministic, precise errors): unknown provider id ->
  InvalidRequestError; unresolvable ruleset -> UnsupportedRulesetError;
  ruleset known but not implemented by the provider ->
  UnsupportedRulesetError; constraints the provider cannot honour ->
  UnsupportedCapabilityError. Non-EngineRequest input -> InvalidRequestError.
- create_default_registry() is an explicit factory (call it; nothing
  registers at import time) containing exactly the native provider.
"""

from __future__ import annotations

from typing import Dict, Tuple

from pairing_core.errors import (
    InvalidRequestError,
    UnsupportedCapabilityError,
    UnsupportedRulesetError,
)
from pairing_core.provider import EngineProvider


class Registry:
    """PUBLIC. Explicit, deterministic provider registry."""

    def __init__(self) -> None:
        self._providers: Dict[str, EngineProvider] = {}

    def register(self, provider: EngineProvider) -> None:
        """Register a provider. Same object twice: no-op. Different object
        under a taken id: InvalidRequestError (no silent overwrite)."""
        if not isinstance(provider, EngineProvider):
            raise InvalidRequestError(
                "only EngineProvider instances can be registered.")
        pid = provider.provider_id
        existing = self._providers.get(pid)
        if existing is not None:
            if existing is not provider:
                raise InvalidRequestError(
                    f"provider id {pid!r} is already registered by another "
                    f"object; refusing silent overwrite.")
            return
        self._providers[pid] = provider

    def get(self, provider_id: str) -> EngineProvider:
        """Explicit lookup. Unknown id -> InvalidRequestError (never a
        guess at another provider)."""
        try:
            return self._providers[provider_id]
        except KeyError:
            raise InvalidRequestError(
                f"unknown provider {provider_id!r}; registered: "
                f"{', '.join(self.providers()) or '(none)'}.") from None

    def providers(self) -> Tuple[str, ...]:
        """Registered ids, sorted (deterministic iteration order)."""
        return tuple(sorted(self._providers))

    def resolve(self, request: object, provider_id: str) -> EngineProvider:
        """Explicit resolution for request + provider id.

        Returns the provider iff it supports the request's (ruleset,
        constraints). No defaults, no fallback, no ranking.
        """
        from pairing_core.api import EngineRequest
        from pairing_core.rulesets import ConstraintSet, resolve_ruleset

        provider = self.get(provider_id)
        if not isinstance(request, EngineRequest):
            raise InvalidRequestError(
                "EngineRequest required for resolution.")
        constraints = request.constraints
        if constraints is None:
            constraints = ConstraintSet()
        if not isinstance(constraints, ConstraintSet):
            raise InvalidRequestError(
                "constraints must be a ConstraintSet.")
        resolved = resolve_ruleset(request.ruleset)
        caps = provider.capabilities
        if resolved not in caps.rulesets:
            raise UnsupportedRulesetError(
                f"provider {provider_id!r} does not implement "
                f"{resolved.system}@{resolved.effective_date}.")
        if not provider.supports(resolved, constraints):
            raise UnsupportedCapabilityError(
                f"provider {provider_id!r} cannot honour these constraints "
                f"(refusing, not ignoring).")
        return provider


def create_default_registry() -> Registry:
    """PUBLIC factory: registry with exactly the native provider.

    Explicit call, deterministic content, no import-time side effects.
    """
    from pairing_core.provider import NativeDutchProvider

    registry = Registry()
    registry.register(NativeDutchProvider())
    return registry
