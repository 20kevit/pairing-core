"""v0.1.0 behavioral golden harness (F1 checkpoint).

Compares the live kernel against ``tests/data/v010_goldens.json`` — frozen
outputs recorded from the UNMODIFIED v0.1.0 kernel (see tests/v010_cases.py).
Any failure here means observable behavior changed and requires deliberate
review per O08 (never silent golden updates).

Coverage contract (O08): pairing ordering, board numbering, colour allocation,
bye selection, float tags, validation verdicts/rule codes, error type+message.
"""

import json
import os

import pytest

from pairing_core import (
    PairingCard,
    PlayerData,
    RoundResult,
    pair_round,
    validate_round,
)

DATA = os.path.join(os.path.dirname(__file__), "data", "v010_goldens.json")


def _load():
    with open(DATA, encoding="utf-8") as fh:
        return json.load(fh)


DOC = _load()


def _player(p):
    return PlayerData(
        id=p["id"], pairing_no=p["pairing_no"], rating=p["rating"],
        points=p["points"], color_hist=p["color_hist"],
        opponents=frozenset(p["opponents"]),
        received_bye=p["received_bye"], float_hist=p["float_hist"])


def _summary(rep):
    return {"valid": rep.is_valid,
            "errors": sorted(f.rule for f in rep.errors),
            "warnings": sorted(f.rule for f in rep.warnings),
            "infos": sorted(f.rule for f in rep.findings
                            if f.level == "INFO")}


def _engine_cases():
    return [c for c in DOC["cases"] if c["kind"] == "engine"]


def _validator_cases():
    return [c for c in DOC["cases"] if c["kind"] == "validator"]


def _error_cases():
    return [c for c in DOC["cases"] if c["kind"] == "error"]


def test_corpus_meta():
    assert DOC["meta"]["kernel_version"] == "0.1.0"
    assert DOC["meta"]["ruleset_label"] == "dutch-till2026-compat"
    assert len(DOC["cases"]) == 40


@pytest.mark.parametrize("case", _engine_cases(), ids=lambda c: c["id"])
def test_engine_golden(case):
    players = [_player(p) for p in case["players"]]
    result = pair_round(players, round_number=case["round"],
                        locked_pairs=[tuple(x) for x in case["locked"]]
                        if case["locked"] else None)
    exp = case["expected"]
    assert result.bye_player_id == exp["bye_player_id"]
    assert len(result.pairings) == len(exp["pairings"])
    for card, want in zip(result.pairings, exp["pairings"]):
        assert card.board == want["board"]
        assert card.white_id == want["white"]
        assert card.black_id == want["black"]
        assert card.is_bye == want["bye"]
        assert card.white_float == want["white_float"]
        assert card.black_float == want["black_float"]
    assert _summary(validate_round(result, players)) == exp["validation"]


@pytest.mark.parametrize("case", _validator_cases(), ids=lambda c: c["id"])
def test_validator_golden(case):
    players = [_player(p) for p in case["players"]]
    cards = [PairingCard(board=c["board"], white_id=c["white"],
                         black_id=c.get("black"),
                         is_bye=c.get("bye", False),
                         white_float=c.get("wfloat", ""),
                         black_float=c.get("bfloat", ""))
             for c in case["cards"]]
    rep = validate_round(RoundResult(round_number=case["round"],
                                     pairings=cards), players)
    assert _summary(rep) == case["expected"]["validation"]


@pytest.mark.parametrize("case", _error_cases(), ids=lambda c: c["id"])
def test_error_golden(case):
    players = [_player(p) for p in case["players"]]
    with pytest.raises(eval(case["expected"]["error"]["type"])) as exc:
        pair_round(players, round_number=case["round"],
                   locked_pairs=[tuple(x) for x in case["locked"]]
                   if case["locked"] else None)
    assert str(exc.value) == case["expected"]["error"]["message"]
