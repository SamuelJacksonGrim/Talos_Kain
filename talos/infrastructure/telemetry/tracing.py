"""Tracing (DORMANT — spec §14 telemetry spine).

Spans and traces across the agent mesh, replayable by the forensics agent via
audit pointers. Milestone zero is a single synchronous loop with nothing to
trace across. This is the seam for distributed tracing when the mesh wakes.
"""

from __future__ import annotations

from contextlib import contextmanager


class Tracer:
    @contextmanager
    def span(self, name: str, **attrs):
        raise NotImplementedError("dormant")
        yield  # pragma: no cover
