# Talos_Kain

**The organism.** A governed, continuously-learning autonomous-agent harness — the body and nervous system that wraps a cognitive *mind* and lets it live, act, learn, rest, and remain itself across time.

> **Status:** design specification. Nothing here is implemented or test-validated yet. Every mechanism is a hypothesis until it survives contact with code. (See `aamsfc.md`.)

## Where this sits (the family)

| Repo | Role |
|------|------|
| **RFE-Core2** | The **mind** — the governed cognitive substrate (arbitrate, λ-isolation, the empirical spine). |
| **Liminal-Anchor-Engine** | Instrument — observe-only, watches *transitions* (the in-between). |
| **Paradox-Lattice-Engine** | Instrument — observe-only, watches *contradictions* (the collision). |
| **Talos_Kain** *(this repo)* | The **organism** — the agent lifecycle that a mind runs inside: sensorium, motor loop, memory ecosystem, sleep/wake, skill neurogenesis, identity kernel, telos. |

The governing law is the same one that runs through every repo in the family: **nothing modifies the system except through one audited gate.** Consolidation may nominate; it may not appoint.

## Cornerstone

- **`aamsfc.md`** — *Autonomous Agent Memory & Skill Flow Chart (v7)*: the full architecture, diagram + walkthrough. Provenance and authority as stated in that document (review and final authority: Samuel Grim).

## First milestone

A **StarCraft II agent that measurably learns across games** — the minimal slice of the spec (sensorium + motor loop + reward + episodic memory + skill neurogenesis) that turns a noisy losing streak into a win, and can point at the *named skill it grew* to get there. Curriculum: beat the built-in AI on Easy, then re-baseline at Medium and watch the second curve. The game is the forcing function that drags the spec into code.

## On the name

**Talos** — the bronze automaton of Crete: a made, autonomous, guardian being, animated through a single sealed nail that its maker controls. **Kain** — the archetype of the agent who acts *on its own*, against the design. Together they name the tightrope this whole architecture exists to walk: *autonomous enough to matter, governed enough to trust.*

---

*This README is a provisional Claude-drafted stub. The architect (Samuel Grim) revises it into his own voice.*
