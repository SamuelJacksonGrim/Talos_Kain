"""Metrics (DORMANT — spec §14 telemetry spine).

Counters, gauges, histograms for cost, latency, energy, uncertainty. Milestone
zero prints a win-rate summary at the end of a run and logs via
``logging.py``; structured metrics arrive with the glial layer.
"""

from __future__ import annotations


class Metrics:
    def incr(self, name: str, value: float = 1.0, **tags) -> None:
        raise NotImplementedError("dormant")

    def gauge(self, name: str, value: float, **tags) -> None:
        raise NotImplementedError("dormant")
