# ADR 0001 — Implementation language and milestone-zero skeleton

**Status:** accepted · **Date:** 2026-07-22

## Context

`aamsfc.md` (v7) is a design specification — nothing implemented or
test-validated. The first milestone in the README is a **StarCraft II agent
that measurably learns across games**, drawn from the minimal slice of the
spec: sensorium + motor loop + reward + episodic memory + skill neurogenesis.

The open question was which language to build in (Rust, C++, Python, Nim, …),
and how much of the v7 architecture to scaffold up front.

## Decision

**Language: a Python spine, with a Rust (PyO3) escape hatch reserved for
profiled hot paths only.**

- The forcing function is a Python problem: the mature SC2 learning
  environments (PySC2, python-sc2) are Python, and the §12 learning stack
  (PyTorch, DPO/RLHF/RLAIF) is Python. For an unvalidated spec, iteration
  speed against the milestone dominates raw CPU.
- C++ and Nim are rejected: C++ buys Rust's performance with worse safety and
  interop; Nim has too thin an ML/agent ecosystem. If we ever drop down, Rust
  + PyO3 is the safe modern answer — and memory safety is on-theme for a
  system whose thesis is "one audited gate."
- SQL is a **store behind the domain**, not the language the system is written
  in. SQLite now (split per store for bulkhead containment), upgradeable to
  Postgres + pgvector behind the same port.
- Bash / PowerShell / WSL / Ubuntu are environment and glue, not the
  application language.

**Architecture: hexagonal — `domain` / `services` / `infrastructure`.**
The domain (pure organism logic) never imports SQLite or PySC2. Swapping the
store or the environment is an infrastructure change behind a
`talos.domain.ports` Protocol.

**Scope: full tree, one live vertical slice.** The directory structure
reflects the long-term architecture, but only the milestone-zero loop is
implemented; every other organ is a typed stub. The rest of the v7 spec stays
dormant until gameplay exposes the need for it.

**Three invariants are non-negotiable from commit one** (they implement
spec invariants, not features):

1. **Hash-chained audit ledger.** Each row carries the previous row's digest;
   `verify()` recomputes the chain. Without this, "immutable" is a comment.
   The ledger is the trust root.
2. **Provenance-aware schema.** Every episode records `run_id` + `seed` +
   env version; every skill stores the episode lineage that grew it. This
   makes "this skill emerged from these games" a query, not a story — and the
   milestone's core claim falsifiable.
3. **One universal admission gate.** `gate.admit(candidate) ->
   ADMIT/REJECT/DEFER/ESCALATE`. Nothing writes to a behavior-shaping store
   directly. The §7 skill CI, §11 identity crucible, and §15 horizon gate
   plug into this seam instead of forcing a repo-wide refactor.

**Environment: MockEnv is primary, not a fallback.** If the loop can't show
improvement in a deterministic toy world, attaching StarCraft II only makes
debugging harder. SC2 becomes an adapter problem once the mock loop is proven.

## Milestone zero

> Build the full repository skeleton, but implement exactly one vertical
> slice — sensorium → policy → motor → reward → WAL → episodic store → skill
> extraction — running against a deterministic mock environment, with a
> hash-chained audit ledger, provenance-aware schema, and a universal
> admission gate already in place.

## Consequences

- First runnable artifact is `talos-mock`: it demonstrates a win rate rising
  across episodes and names the skills it grew. No game binary required.
- The Rust directory exists but is un-wired; the build never touches it.
- When SC2 attaches, no domain/service code changes — only a new
  `Environment` implementation.

## Provenance

Language recommendation: Claude. Repository shape: proposed by GPT, refined by
Claude (audit-chain, provenance schema, gate seam) and by GPT
(domain/services/infrastructure layering, MockEnv-as-primary). Review and
final authority: Samuel Grim.
