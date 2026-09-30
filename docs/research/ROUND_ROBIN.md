# Round Robin Research (STAGE 2, §2.9)

## 1. Single round robin

Every player meets every other exactly once; N players → N-1 rounds (even N).
FIDE RULE (PRIMARY: Handbook C.05 Annex 1 Berger tables, full tables to 16
retrieved): fixed schedules by pairing number; odd N → highest number = bye;
standard tables VERIFIED for 3–16 players. Algorithm (SECONDARY, Berger
Explained — constructive circle method VERIFIED by inspection): round 1 =
1-N, 2-(N-1)…; subsequent rounds rotate list 1..N-1 (white-before-black sort)
with N alternating colour. Double RR: second cycle swaps colours; FIDE
recommends reversing the last two rounds of the first cycle to avoid 3× colour
(SECONDARY: ECU Berger doc, consistent).

## 2. Colours / home-away balance

Berger tables encode colours per round (first-named = white, PRIMARY tables).
Balance is structural, not searched — unlike Swiss. Odd N: bye rounds carry no
colour (consistent with 2026 played-only colour rule).

## 3. What RR needs that pairing-core lacks

Nothing algorithmic is hard (schedule generation is O(N²) table lookup), but
the domain needs: pairing-number assignment policy (currently caller-owned and
frozen — RR needs initial lot + async? no), bye-as-round bookkeeping distinct
from Swiss PAB (bye rotates; no "lowest score" logic), double-cycle colour
swap, and a rounds-schedule result type (current `RoundResult` is single-round).
All PROPOSED for Stage 3 taxonomy; RR is the cheapest future system
complexity-wise. No engine choice needed (no search).
