"""F2 ruleset-identity tests: ids, constraint sets, resolution, known table."""

import pytest

from pairing_core.errors import PairingError, UnsupportedRulesetError
from pairing_core.rulesets import (
    ALIASES,
    DUTCH_TILL2026_COMPAT,
    KNOWN_RULESETS,
    ConstraintSet,
    RulesetId,
    describe_known_rulesets,
    resolve_ruleset,
)


def test_ruleset_id_value_semantics():
    a = RulesetId(system="dutch", effective_date="2026-01-31")
    b = RulesetId(system="dutch", effective_date="2026-01-31")
    assert a == b and hash(a) == hash(b)
    assert a != RulesetId(system="dutch", effective_date="2026-02-01")
    assert a != RulesetId(system="dutch", effective_date="2026-01-31",
                          acceleration="baku")


def test_compat_alias_resolves():
    rid = resolve_ruleset(DUTCH_TILL2026_COMPAT)
    assert rid == RulesetId(system="dutch", effective_date="2026-01-31")
    assert resolve_ruleset(rid) is not None


def test_unknown_systems_rejected_explicitly():
    for bad in ("dutch-2026",
                RulesetId(system="dutch", effective_date="2026-02-01"),
                RulesetId(system="dubov", effective_date="2026-02-01"),
                RulesetId(system="dutch", effective_date="2026-01-31",
                          acceleration="baku"),
                RulesetId(system="dutch", effective_date="2026-01-31",
                          pab_value=1.0),
                "lim", "", None, 42):
        with pytest.raises(UnsupportedRulesetError):
            resolve_ruleset(bad)


def test_unsupported_is_typed_and_mentions_known():
    with pytest.raises(UnsupportedRulesetError) as exc:
        resolve_ruleset("dubov")
    assert DUTCH_TILL2026_COMPAT in str(exc.value)
    assert isinstance(exc.value, PairingError)


def test_known_table_pins_compat_kernel():
    assert len(KNOWN_RULESETS) == 1
    meta = next(iter(KNOWN_RULESETS.values()))
    assert meta["engine"] == "native-dutch"
    assert DUTCH_TILL2026_COMPAT in ALIASES


def test_constraint_set_defaults_and_normalization():
    cs = ConstraintSet()
    assert cs.forced_pairs == () and cs.forbidden_pairs == ()
    assert cs.bye_directive is None
    cs2 = ConstraintSet(forced_pairs=[[1, 2]], forbidden_pairs=[[3, 4]])
    assert cs2.forced_pairs == ((1, 2),)
    assert cs2.forbidden_pairs == ((3, 4),)


def test_describe_table_for_versions_reporting():
    table = describe_known_rulesets()
    assert "dutch@2026-01-31" in table
    assert table["dutch@2026-01-31"]["engine"] == "native-dutch"
