"""Baku Acceleration Method 2026 (C.04.7 Art.1, F-0117, FULL_TEXT).

Pure functions: GA/GB split (1.2), virtual-point schedule (1.4), pairing
score (1.5). No 1-½-0 hardcoding: win/draw/loss values are parameters
subject to the premise win = 2 draws, loss = 0 (1.1).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class BakuGroups:
    ga: Tuple[int, ...]  # TPNs in GA (by TPN order)
    gb: Tuple[int, ...]


def split_groups(tpns: List[int]) -> BakuGroups:
    """C.04.7 Art.1.2: GA = first half rounded UP to the nearest even number.

    Formula: 2 * ceil(N/4); that number is also the last GA participant's TPN
    position (161 -> 82 verified against the official note).
    """
    ordered = sorted(tpns)
    n = len(ordered)
    ga_size = 2 * int(math.ceil(n / 4.0))
    return BakuGroups(ga=tuple(ordered[:ga_size]), gb=tuple(ordered[ga_size:]))


def accelerated_rounds(total_rounds: int) -> int:
    """C.04.7 Art.1.4.1: accelerated rounds = first half (rounded up)."""
    return int(math.ceil(total_rounds / 2.0))


def virtual_points(is_ga: bool, round_number: int, total_rounds: int,
                   *, win_value: float = 1.0) -> float:
    """C.04.7 Art.1.4.2-1.4.3: GA gets win-value for the first half (rounded
    up) of the accelerated rounds, halved for the rest; GB/post get none.

    Verified: 9R individual -> 1.0 x3 then 0.5 x2; 11R team MP -> 2 x3 + 1 x3.
    """
    if not is_ga:
        return 0.0
    accel = accelerated_rounds(total_rounds)
    if round_number > accel:
        return 0.0
    first_half = int(math.ceil(accel / 2.0))
    if round_number <= first_half:
        return win_value
    return win_value / 2.0


def pairing_scores(standings: Dict[int, float], groups: BakuGroups,
                   round_number: int, total_rounds: int,
                   *, win_value: float = 1.0) -> Dict[int, float]:
    """C.04.7 Art.1.5: pairing score = standings + virtual points."""
    ga = set(groups.ga)
    return {pid: pts + virtual_points(pid in ga, round_number, total_rounds,
                                      win_value=win_value)
            for pid, pts in standings.items()}
