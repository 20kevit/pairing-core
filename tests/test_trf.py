"""W2 TRF-subset tests: round-trip, lenient parse, output format, bridge."""

import pytest

from pairing_core.adapters.trf import (
    TournamentInput,
    TrfPlayer,
    TrfRound,
    build_trf,
    from_engine_request,
    parse_pairing_output,
    parse_trf,
)
from pairing_core import ConstraintSet, EngineRequest, PlayerData
from pairing_core.errors import InternalError, InvalidRequestError


def _sample():
    return TournamentInput(
        players=(
            TrfPlayer(pairing_id=1, name="Alpha", rating=2000, points=1.0,
                      rounds=(TrfRound(opponent=2, color="w", result="1"),)),
            TrfPlayer(pairing_id=2, name="Beta", rating=1900, points=0.0,
                      rounds=(TrfRound(opponent=1, color="b", result="0"),)),
            TrfPlayer(pairing_id=3, name="Gamma", rating=1800, points=1.0,
                      rounds=(TrfRound(opponent=None, color="-",
                                       result="F"),)),
        ),
        rounds_total=2, name="Sample", absent_ids=(3,),
        forbidden_pairs=((1, 2),))


def test_round_trip():
    t = _sample()
    back = parse_trf(build_trf(t))
    assert back.name == "Sample" and back.rounds_total == 2
    assert back.absent_ids == (3,) and back.forbidden_pairs == ((1, 2),)
    assert [(p.pairing_id, p.name, p.rating, p.points,
             [(r.opponent, r.color, r.result) for r in p.rounds])
            for p in back.players] == \
           [(p.pairing_id, p.name, p.rating, p.points,
             [(r.opponent, r.color, r.result) for r in p.rounds])
            for p in t.players]


def test_rank_tolerant_parse():
    text = ("012 T\nXXR 2\n"
            "001 1 Alpha 2000 XXX 0 0 1.0 1 2 w 1\n"
            "001 2 Beta 1900 XXX 0 0 0.0 2 1 b 0\n")
    back = parse_trf(text)
    assert [p.pairing_id for p in back.players] == [1, 2]
    assert back.players[0].rounds[0].opponent == 2


def test_writer_shape_spot_checks():
    text = build_trf(_sample())
    assert text.startswith("012 Sample\n062 3\nXXR 2\nXXZ 3\nXXP 1 2\n")
    assert "001 1 - - Alpha 2000 XXX 0 0 1.0 2 w 1" in text
    assert "0000 - F" in text  # PAB assumption, see module docstring


def test_output_parser_and_bye():
    pairs = parse_pairing_output("2\n1 2\n3 0\n")
    assert pairs == [(1, 2), (3, None)]
    with pytest.raises(InternalError):
        parse_pairing_output("2\n1 2\n")
    with pytest.raises(InternalError):
        parse_pairing_output("")
    with pytest.raises(InternalError):
        parse_pairing_output("many\n1 2\n")


def test_malformed_trf_rejected():
    with pytest.raises(InvalidRequestError):
        parse_trf("001 1\n")
    with pytest.raises(InvalidRequestError):
        parse_trf("001 1 A 1500 XXX 0 0 0.0 2 x 1\n")
    with pytest.raises(InvalidRequestError):
        parse_trf("001 1 A 1500 XXX 0 0 0.0 2 w 9\n")
    with pytest.raises(InvalidRequestError):
        parse_trf("001 1 A 1500 XXX 0 0 0.0 1 2\n")


def test_bridge_from_engine_request():
    players = [PlayerData(id=1, pairing_no=1, rating=2000, points=1.0),
               PlayerData(id=2, pairing_no=2, rating=1900, points=0.0)]
    req = EngineRequest(players=players, ruleset="dutch-till2026-compat",
                        round_number=2, constraints=ConstraintSet())
    t = from_engine_request(req, {1: [TrfRound(2, "w", "1")],
                                  2: [TrfRound(1, "b", "0")]},
                            absent_ids=())
    text = build_trf(t)
    assert "XXR 2" in text
    assert parse_trf(text).rounds_total == 2
    with pytest.raises(InvalidRequestError):
        from_engine_request(object(), {})


def test_core_does_not_import_adapters():
    import pairing_core.api
    import pairing_core.engine
    import pairing_core.envelope
    import pairing_core.provider
    import pairing_core.registry
    import sys
    for mod in ("pairing_core.api", "pairing_core.engine",
                "pairing_core.envelope", "pairing_core.provider",
                "pairing_core.registry", "pairing_core.rulesets",
                "pairing_core.models", "pairing_core.validator"):
        src = sys.modules[mod].__file__
        with open(src, encoding="utf-8") as fh:
            lines = fh.readlines()
        imports = [ln for ln in lines
                   if ln.lstrip().startswith(("import ", "from "))]
        assert not any("pairing_core.adapters" in ln or
                        "pairing_core import adapters" in ln
                        for ln in imports), mod
