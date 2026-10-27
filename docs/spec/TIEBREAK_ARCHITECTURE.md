# Tie-break library boundary and Burstein integration contract

**Status (2026-10-27):** the independent `20kevit/tiebreak-core` library is
published at v1.2.0 (source commit
`61491321d7886ab4abe1b7c64686dfce48d2c3dd`). Pairing-Core does not depend on,
copy, or reimplement its algorithms. The inspected version exposes C.07
calculations; it has no C.04.4.2 Burstein Index calculator. This document
replaces the earlier proposal that implied an existing Pairing-Core →
tiebreak-core dependency.

## 1. Product boundary

- **Pairing-Core** owns one-round pairing decisions and pairing-specific
  ordering/procedures. It does not calculate tournament standings or tie-breaks.
- **tiebreak-core** owns the tie-break algorithms it explicitly implements
  and versions. It does not own pairing or tournament lifecycle.
- **The integrating application/caller** owns event records and composition
  between these libraries. It must select values whose semantics match the
  consuming ruleset; one library's output is not presumed interchangeable
  with another rules chapter's value.

## 2. Current Burstein input contract

After the Dutch seeding rounds, Pairing-Core's `pair_2026` requires a complete
`BursteinIndexSet`: for every entrant, caller-supplied Buchholz and
Sonneborn–Berger values plus a `BursteinIndexProvenance` declaration. The
engine consumes those values only to form C.04.4.2 pairing order and
pairing-specific bye/order decisions. It does not recompute or verify the
calculation. Missing or roster-mismatched values fail with a typed request
error; no rating, score, or C.07 fallback is substituted.

The provenance distinguishes `caller-supplied` from `library-calculated` and
can record producer, producer version, producer ruleset, and scope. This is a
caller declaration, not independent proof that the value is correct. A caller
that marks output from `tiebreak-core` must identify the C.07 ruleset actually
used and independently establish semantic equivalence to the required C.04
Index for the event data in question. In particular, do not assume equivalence
for unplayed rounds, consecutive zero-point byes, or acceleration virtual
points. If a semantically suitable C.04 calculator is unavailable, Burstein
pairing is unavailable for that request.

The legacy `P26Request.round_results` field is retained for compatibility
with old serialized requests. The public dispatcher rejects non-empty values
for Burstein requests, where the field might otherwise be mistaken for an
Index calculator input; other systems retain but ignore it. It is never an
algorithm input and never calculates the Burstein Index.

## 3. Direction of composition

```text
integrating application ──► Pairing-Core (pairing)
          │
          └───────────────► tiebreak-core (its supported tie-breaks)
```

There is no runtime dependency between the two libraries. The application
may pass an externally calculated value set to Pairing-Core after verifying
that the source system/version and event assumptions are suitable.

## 4. Anti-duplication rule

No Burstein Buchholz/SB formula is to be added to Pairing-Core. If the
separate library later implements C.04.4.2, the application may use it only
after its exact ruleset version, semantics, input assumptions, and error
behavior have been verified against the official C.04 text and independent
fixtures. Do not copy its implementation into Pairing-Core.

## 5. General tie-break scope

Pairing-Core does not provide a general standings/tie-break API. Any future
extension to `tiebreak-core` is owned by that project and requires its own
source review and verification. Pairing-Core remains a pairing-only library;
there is no shared "tournament-core" layer combining pairing, standings,
results, ratings, or tournament state.
