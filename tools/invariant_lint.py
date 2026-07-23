"""Assert the aamsfc.md invariants against the diagram, mechanically.

The document states that the diagram is the normative artifact and that an
invariant you cannot test is a vibe. This is the test. It runs against the
mermaid source itself, so it is checkable today, with no part of the system
implemented.

Exit code 0 if every structural invariant holds, 1 otherwise.

    python3 tools/invariant_lint.py aamsfc.md
    python3 tools/invariant_lint.py aamsfc.md --audit
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mermaid_graph import Graph, parse  # noqa: E402

# --- The trust root -------------------------------------------------------
# The signed, out-of-band architect hand. v5 put it in the diagram precisely so
# it would be a named exception rather than an unlogged one, which is exactly
# what lets a linter tell it apart from an autonomous write.
ARCHITECT = "ARCH"

# --- Protected objects and their single autonomous door (I10) --------------
# domain -> (store node, {permitted writers})
GATES: dict[str, tuple[str, set[str]]] = {
    "identity":      ("IDK",   {"ANNEAL", ARCHITECT}),
    "capability":    ("PROC",  {"PUBLISH"}),
    "control-plane": ("CTRL",  {"META", "HOTSWAP"}),
    "purpose":       ("TELOS", {"HORIZON", ARCHITECT}),
}

# --- I4: the only two ways the world reaches cognition ---------------------
ATTENTION = "ATT"
HYGIENE = {"FASTSAFE", "DEEPIMMUNE"}
WORLD_INPUTS = {"IN", "FB", "USER"}
NORMALIZER = "NORM"

# --- I2: the crucible chain, in the order the walkthrough declares ---------
CRUCIBLE_CHAIN = ["LINEAGE", "POISON", "RESONANCE", "CRUCIBLE", "CONTINUITY", "ANNEAL"]
IDENTITY_TAGS = {"SUPPRESS", "DISSONANCE", "CAND", "SELFMOD"}
CRUCIBLE_QUEUE = "REFLECTQ"

# --- I12: proposals route to the human lane and stop there -----------------
PROPOSAL = "ARCHPROP"
HUMAN = "HUMAN"


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.lines: list[str] = []

    def check(self, tag: str, name: str, ok: bool, detail: str = "") -> None:
        mark = "PASS" if ok else "FAIL"
        self.lines.append(f"  [{mark}] {tag:<4} {name}")
        if detail:
            for d in detail.splitlines():
                self.lines.append(f"          {d}")
        if not ok:
            self.failures.append(f"{tag}: {name}")

    def note(self, text: str) -> None:
        self.lines.append(f"  [ -- ] {text}")


def reaches(g: Graph, start: str, goal: str) -> bool:
    seen, q = {start}, deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            return True
        for e in g.out_of(cur):
            if e.dst not in seen:
                seen.add(e.dst)
                q.append(e.dst)
    return False


def run(g: Graph) -> Report:
    r = Report()

    # I1 / I10 — one autonomous door per self-modification domain.
    for domain, (store, allowed) in GATES.items():
        if store not in g.nodes:
            r.check("I10", f"{domain}: store {store} missing from diagram", False)
            continue
        writers = {e.src for e in g.into(store)}
        rogue = writers - allowed
        tag = "I1" if domain == "identity" else "I10"
        detail = f"{store} <- {sorted(writers) or ['(nothing)']}"
        if rogue:
            detail += f"\nungated writers: {sorted(rogue)}"
        r.check(tag, f"{domain} writes only through {sorted(allowed)}", not rogue, detail)

    # I2 — one crucible, and the chain runs in the declared order.
    present = [n for n in CRUCIBLE_CHAIN if n in g.nodes]
    missing = [n for n in CRUCIBLE_CHAIN if n not in g.nodes]
    ordered = all(
        any(e.dst == b for e in g.out_of(a))
        for a, b in zip(present, present[1:])
    )
    r.check(
        "I2", "crucible chain is a single ordered path", ordered and not missing,
        f"declared: {' -> '.join(CRUCIBLE_CHAIN)}\n"
        f"in graph: {' -> '.join(present)}"
        + (f"\nmissing:  {missing}" if missing else ""),
    )

    for tag_node in sorted(IDENTITY_TAGS & g.nodes):
        r.check(
            "I2", f"{tag_node} reaches the crucible queue",
            reaches(g, tag_node, CRUCIBLE_QUEUE),
        )

    # I4 — nothing reaches attention without passing the hygiene gates.
    if ATTENTION in g.nodes:
        feeders = {e.src for e in g.into(ATTENTION)}
        bypass = feeders - HYGIENE
        r.check(
            "I4", "attention is fed only by the hygiene gates", not bypass,
            f"{ATTENTION} <- {sorted(feeders)}"
            + (f"\nbypassing: {sorted(bypass)}" if bypass else ""),
        )
    for src in sorted(WORLD_INPUTS & g.nodes):
        r.check("I4", f"{src} enters through {NORMALIZER}", reaches(g, src, NORMALIZER))

    # I8 — no silent removal: every terminal sink must be an explicit record.
    RECORDS = {"HUMAN", "AUDIT", "SHIELD", "EPI", "MICROBATCH", "CLEARTAG"}
    sinks = {n for n in g.nodes if not g.out_of(n)}
    unrecorded = sinks - RECORDS
    r.check(
        "I8", "every terminal sink is an explicit record", not unrecorded,
        f"sinks: {sorted(sinks)}"
        + (f"\nunaccounted: {sorted(unrecorded)}" if unrecorded else ""),
    )

    # I11 / I12 — the system gets a voice, never the pen.
    if PROPOSAL in g.nodes:
        dests = {e.dst for e in g.out_of(PROPOSAL)}
        r.check(
            "I12", f"{PROPOSAL} terminates in the human lane", HUMAN in dests,
            f"{PROPOSAL} -> {sorted(dests)}",
        )
    if HUMAN in g.nodes:
        r.check(
            "I12", f"{HUMAN} is terminal (no self-executing return path)",
            not g.out_of(HUMAN),
            f"{HUMAN} -> {sorted(e.dst for e in g.out_of(HUMAN)) or ['(terminal)']}",
        )

    # Honest about scope.
    r.note("I3, I5, I6, I7, I9 are not structurally checkable from the diagram:")
    r.note("  they constrain payloads, timing, and staging, not topology.")

    return r


def audit(g: Graph) -> None:
    """The v5/v6 method, automated: for every protected object, the ratio of
    gated to total write paths. This is the check that found both bug classes."""
    print("\nWrite-path audit")
    print("-" * 60)
    for domain, (store, allowed) in GATES.items():
        if store not in g.nodes:
            continue
        ins = g.into(store)
        gated = [e for e in ins if e.src in allowed]
        print(f"\n  {store}  ({domain})  {len(gated)} of {len(ins)} gated")
        for e in ins:
            mark = "ok " if e.src in allowed else "ROGUE"
            lab = f'  "{e.label}"' if e.label else ""
            print(f"      {mark:<6}{e.src:<12} -> {store}{lab}   (line {e.line})")


# --- Growth audit ---------------------------------------------------------
# The dual of the v5/v6 write-path method. That audit asked how many paths
# write into a protected store and how many are gated. This asks the opposite
# question: what takes state *out*. A store with no removal path grows without
# bound, and unbounded growth in a store the system reads from is a slow
# failure that no write-path audit can see.

STORES = [
    "ARTSTORE", "WM", "HOTCACHE", "WAL", "EPI", "SEM", "HG", "PROC", "IDK",
    "CRYSTAL", "ERRLOG", "DATASET", "EVALSET", "AUDIT", "QUAR", "TOMB",
    "SELFSTORE", "TELOS",
]

# Mechanisms that bound a store's growth, each leaving a receipt (I8).
REMOVAL = {"EVICT", "DISTILLMEM", "DISTILL", "TOMB", "SHIELD", "SHATTER",
           "QUARHG", "LOCALPATCHMEM", "CLEARTAG"}


def growth(g: Graph) -> list[str]:
    """Report which stores have a bounded-growth story and which do not."""
    print("\nGrowth audit — what takes state out of each store")
    print("-" * 60)
    unbounded = []
    for store in STORES:
        if store not in g.nodes:
            continue
        outs = g.out_of(store)
        drains = [e for e in outs if e.dst in REMOVAL]
        if drains:
            how = ", ".join(sorted({e.dst for e in drains}))
            print(f"  [bounded  ] {store:<12} -> {how}")
        else:
            reads = sorted({e.dst for e in outs}) or ["(nothing)"]
            print(f"  [UNBOUNDED] {store:<12} reads only: {', '.join(reads)}")
            unbounded.append(store)
    return unbounded


def main() -> int:
    doc = Path(sys.argv[1] if len(sys.argv) > 1 else "aamsfc.md")
    g = parse(doc)
    print(f"aamsfc invariant lint — {doc}")
    print(f"{len(g.nodes)} nodes, {len(g.edges)} edges\n")

    r = run(g)
    print("\n".join(r.lines))

    if "--audit" in sys.argv:
        audit(g)
    if "--growth" in sys.argv:
        growth(g)

    print()
    if r.failures:
        print(f"FAILED — {len(r.failures)} invariant violation(s):")
        for f in r.failures:
            print(f"  - {f}")
        return 1
    print("All structurally checkable invariants hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
