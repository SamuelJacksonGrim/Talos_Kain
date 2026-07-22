# migrations/

Milestone zero declares each store's schema inline (a `CREATE TABLE IF NOT
EXISTS` in the store module) and creates it on first open. That is deliberate:
with four tiny, independent SQLite files and no production data, a migration
framework would be ceremony without payoff.

This directory is the seam for when that stops being true — the first time a
store's schema changes in a way that must preserve existing rows (most likely
the episodic archive, once trajectories go multi-step, or the semantic store
when embeddings arrive). At that point add ordered, forward-only migration
files here and a tiny runner that records applied versions per store.

Until then, intentionally empty.
