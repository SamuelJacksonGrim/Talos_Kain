# rust/ — the escape hatch (dormant)

This directory exists from commit one and **nothing depends on it.** That is
the whole point.

The language decision for Talos_Kain is: a Python spine, and drop to Rust
(via [PyO3](https://pyo3.rs)) **only where the profiler says Python is the
wall** — never speculatively. Keeping an empty, un-wired Rust crate here means
that when profiling the SC2 agent eventually points at a hot path (the hot
retrieval cache, observation vectorization, nearest-neighbour lookup, or motor
scheduling), the seam already exists: you replace one implementation behind a
`talos.domain.ports` Protocol, and no service or domain code changes.

Until then, this stays empty and the build never touches it.

## When you wake it up

1. Add the real crate under `rust/hot_cache/` (or whatever the profiled
   component turns out to be — the name is a placeholder, not a commitment).
2. Build a Python extension module with PyO3 + maturin.
3. Have the infrastructure layer expose it as an implementation of the
   relevant port. The domain never learns Rust exists.
