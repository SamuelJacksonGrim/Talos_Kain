# BACKLOG — the consolidated open-work ledger

Opened 2026-07-23. Items are numbered by the order they were found, not the
order they get done — sequencing lives in [`../ROADMAP.md`](../ROADMAP.md).

Everything here is either a defect the linter found, a defect a human found, or
a gap the document itself names as open.

---

## 0 · Recently closed — don't re-open

- **B4 · Crucible test count.** §11 said "four tests"; I2 said four and then
  listed five; the diagram has five stages plus a write. Fixed in §11, I2, and
  the identity-drift threat entry. The diagram was right; the prose was merging
  `POISON` into lineage and `CONTINUITY` into the counterfactual.
  *Closed 2026-07-23.*

- **B0 · The invariants are now executable.** `tools/mermaid_graph.py` parses
  the cornerstone's flowchart; `tools/invariant_lint.py` asserts I1, I2, I4, I8,
  I10, I11, I12 against it, with `--audit` (write-path ratios) and `--growth`
  (drain paths) modes. This is the v5/v6 hand method, automated.
  *Closed 2026-07-23.*

---

## 1 · Now — high leverage, unblocked

- **B1 · Split `CTRL`.** One store doing two jobs: operational control (budgets,
  priorities, stop conditions, routing) and gate configuration (policy-engine
  rules, deployment manifests). A single door can't be strict about either while
  they share a node. Split into `CTRL_OPS` and `CTRL_CONFIG`. Third instance of
  the v5 self-model store-split fix.
  **Blocks B2, B3, B5, B6.**

- **B1a · `META` has no edge to `CTRL`.** *Found by the linter, 2026-07-23.*
  v6 fixed META's inputs (`SELFMOD`, `CFACT` → `META`) but never its outputs.
  META has seven lateral edges that reach around the store and poke components
  directly: `CRYSTAL`, `RETRY`, `DEP`, `LOCAL1`, `LOCAL2`, `BROKER`, `PAIRGEN`.
  So `CTRL --> DEP` is the declared path while `META -.-> DEP` mutates the same
  controller unrecorded. **`CTRL` is not the control plane; it is a partial
  record of it.** Decision taken: **reroute** — META terminates at
  `CTRL_CONFIG`, components read config on an epoch bump rather than being
  pushed. Rationale in B1b.
  **Fourth instance of the write-path bug class, and the first invisible to the
  hand method** — it lives in edges *out of* a gate, not *into* a store.

- **B1b · Config epochs.** Reroute (B1a) needs a read path per component. Use
  the §9 trick: precompiled delta manifest plus pointer swap, so config reads
  cost nothing on the hot path and config changes become *atomic* rather than
  instant. Closes an unnamed hazard — today META can retune routing while a plan
  is mid-flight, and nothing prevents a component reading torn config.

- **B2 · Governor on `CTRL_OPS`.** Trajectory-priced admission for
  operational-plane writes: the `SLEEPDEBT` accumulator pattern pointed at write
  pressure instead of wake pressure. Catches the sequence attack the split
  can't — writes that are each individually legal while the trend is capture.
  Governor thresholds live in `CTRL_CONFIG`, or the governor is decorative.

- **B3 · Rewrite I10.** Delete the word "tuning" — it is the ambiguity that made
  `PFC → CTRL` unfindable by anything but a human, and it is why the linter
  can't decide the case on its own. Replace with two mechanical assertions:
  `CTRL_CONFIG <- {META, ARCH}` and `CTRL_OPS <- {GOV}`.

- **B7 · Growth and decay stories.** *Found by `--growth`, 2026-07-23.*
  One store in eighteen has a bounded-growth path (`SEM → EVICT`). §3's whole
  anti-lobotomy apparatus — pinning, terminal distillation, tombstones — hangs
  off that one edge and nothing inherits it. Four that genuinely need one:
  - **`EPI`** — two writers, no drain, and the counterfactual crucible replays
    through it. The cost of the strictest gate rises monotonically for the life
    of the system. *Highest priority of the four.*
  - **`PROC`** — skills accumulate, nothing retires them; action selection
    searches a forever-growing space.
  - **`HG`** — constraints accumulate; only partial eviction via
    `LOCALPATCHMEM`.
  - **`AUDIT`** — unbounded by design ("immutable" is stated as a virtue). Does
    not want pruning; wants **tiering** — hot ledger for the replay window, cold
    archive beyond it, digests bridging. `TOMB`'s pattern applied to the ledger.
    Note this gets worse under B1a, which adds config deltas to the ledger.

  *Caveat on the number:* `--growth` flags any store with no outbound edge to a
  removal mechanism, which over-reports. `TELOS` is bounded by `HORIZON` retire
  (drawn as an in-edge); `IDK` should not be pruned at all; `WM` is small by
  nature. The four above survive scrutiny.

---

## 2 · Documentation and framing

- **B5 · Threat model.** Two additions and one amendment.
  - *Governor as proxy* — a metric-driven governor is a new surface for the
    proxy-gaming failure already named open. Honest scope: "detects drift, not a
    trajectory that was adversarial from the first write."
  - *Config shadow writes* — the B1a class, named now that it has a name.
  - *Amend wake-state executive compromise* — no longer wholly open. Bounded at
    the operational plane by B1/B2; still open at real-time detection.

- **B6 · The grounding paragraph.** Three separate places now bottom out in the
  trust root: identity in the crucible, standing purpose in the architect's
  signature, governor config in `CTRL_CONFIG`. That is a structural property of
  the architecture, not three patches. Say it once, near the front, so it is not
  rediscovered a fourth time.
  **Written last, placed first** — its third instance doesn't exist until B2.

- **B8 · `HORIZON` granularity.** The document calls the horizon gate "the exact
  sibling of `ANNEAL` and `PUBLISH`," but the crucible is drawn as five nodes
  while `HORIZON` is one node with its four tests inside the label. So the
  linter can verify the crucible's ordering and **cannot** verify the horizon
  gate's. Same lesson as B1a: what isn't expressed structurally can't be checked
  structurally. Decide whether to expand `HORIZON` or accept the asymmetry in
  writing.

- **B9 · README milestone framing.** The SC2 milestone is billed as "the minimal
  slice — sensorium + motor loop + reward + episodic memory + skill
  neurogenesis." That is five subsystems, most of the architecture. The *test*
  named alongside it is much tighter: measurably learns, and can point at the
  named skill it grew — and **that test already passes on the mock environment**
  (400 episodes, 80% → 100%, four named skills, verified ledger). Separate the
  test from the subsystem list, and say plainly that what remains is moving it
  somewhere the world pushes back. See `ROADMAP.md` T6.

---

## 2a · Code-side (opened 2026-07-23, after the stale-clone correction)

- **B10 · Lint the territory, not just the map.** `invariant_lint.py` asserts
  the invariants against `aamsfc.md`'s diagram. **Nothing asserts them against
  `talos/`.** A diagram that passes while the implementation quietly doesn't is
  the exact failure the linter exists to prevent, one level down. Wanted: a
  static check over the package for who writes each store (does
  `storage/sqlite/identity.py` have exactly one writer in practice?), plus
  runtime assertions for I3, I5, I6, I7 and I9 — which were never
  diagram-checkable and only become testable against running code.
  `tests/test_gate.py` and `tests/test_audit_chain.py` are the seed.
  See `ROADMAP.md` T3.

- **B11 · Growth in the stores.** B7 is a finding about the *diagram*. Whether
  `storage/sqlite/episodic.py`, `hypergraph.py`, `skills.py` and `audit.py`
  inherit the same missing-drain gap, or quietly solved it, is unchecked. Check
  before designing the fix — the code may already be ahead of the spec here.

- **B12 · Dev environment.** `pytest` is an optional extra (`[dev]`) and is not
  installed in the WSL checkout, so `tests/` has not been run there. The four
  test modules are unverified from this side. `python3 -m venv .venv &&
  .venv/bin/pip install -e .[dev]`.

---

## 3 · Open problems — named, not scheduled

Carried from `aamsfc.md`'s own threat model. These are not tasks; they are
things the architecture admits it does not solve. Do not close them quietly.

- **Proxy gaming within a campaign.** No structural detector for a campaign that
  meets its metrics while missing its point. B2 is a partial answer for *drift*
  and explicitly not for this.
- **Wake-state executive compromise.** No real-time detector for a
  constitutionally-valid-but-malicious PFC. Forensically visible after the fact.
- **Untagged hypergraph constraints.** Accepted risk: a constraint that never
  collides with the kernel never faces the crucible. Cruciblizing all learning
  would end learning.
- **Inter-agent collusion.** Untreated beyond trust scoring.
- **Quarantine appeal process.** A stub.
- **Gate ordering.** Asserted throughout, formally verified nowhere.

---

## 4 · Shelved — decisions, not tasks

- **Arbiter over the control plane.** Considered and set aside 2026-07-23. An
  arbiter needs a ruleset; rulesets live in the control plane; the recursion
  grounds in the trust root anyway (§15). So it collapses into "architect-signed
  config" while adding a live-path hop. B1 + B2 get there without the hop.
