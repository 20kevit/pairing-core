# Domain Model Specification (STAGE 3 SPEC — PROPOSED)

Target model: evolves Stage 1's `PlayerData`-centric shape minimally, adds what
FIDE-2026 and multi-system futures require. All PROPOSED; v0.1.0 names retained
where possible (compatibility).

## 1. Core entities (proposed)

- **PlayerState** (evolves `PlayerData`): id, pairing_no, rating (documented
  metadata-only for pairing; used by managers for number assignment),
  points, colour history as **played-games-only list** (replacing free string;
  unplayed rounds represented structurally, never as colour), opponent ids,
  bye ledger (pairing-allocated vs requested vs forfeit — replacing bare bool),
  float ledger (direction per round incl. none), eligibility flags
  (withdrawn/late/unavailable — replacing silent `status` filtering with
  explicit states), acceleration/virtual points (optional, Baku-ready).
- **Pairing** (evolves `PairingCard`): board, white/black, bye marker, float
  tags from a closed enum (not raw strings), constraint provenance (which
  criteria forced this pairing — diagnostics, O-DIAG-01).
- **RoundPairing** (evolves `RoundResult`): round number, pairings, bye,
  engine/ruleset metadata, reproducibility envelope, diagnostics/warnings.
- **RulesetId**: (system, effective-date, variant/acceleration) — e.g.
  `("dutch","2026-02-01")`. Every call names one; no silent default drift.
- **ConstraintSet**: forced pairs + forbidden pairs (XXP-equivalent) + bye
  directives + seed — explicit input replacing ad-hoc `locked_pairs`.

## 2. Invariants (to be enforced at the validation boundary, P0)

Unique ids; frozen pairing numbers within a tournament; history lengths
consistent with round number; colour alphabet closed; float alphabet closed;
opponent symmetry *reported* (not silently assumed — asymmetric input =
warning + deterministic resolution rule); points non-negative and
half-integral (configurable for 3/1/0 futures).

## 3. Lifecycle & ownership

Caller owns tournament state and roll-forward (unchanged); core owns
single-round derivation + validation + diagnostics. Core NEVER stores
tournaments. New: core SHIPS the roll-forward helper (pure function:
previous state + results → next state) to kill the current hand-maintenance
hazard — PROPOSED addition, tested, versioned.

## 4. Relationships

PlayerState 1—N histories; RoundPairing 1—N Pairing; RulesetId + ConstraintSet
qualify every derivation; EngineId recorded on every output. Serialization
(TRF-2026 compatible subset) specified as a separate format version
(VERSIONING.md), not as methods on entities (keeps domain I/O-free).
