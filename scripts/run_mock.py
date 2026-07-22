#!/usr/bin/env python3
"""Convenience launcher for the mock organism.

Equivalent to the ``talos-mock`` console script; kept here so the repo has an
obvious runnable entry point without installing the package.

    python scripts/run_mock.py --episodes 400
"""

from talos.services.organism import main

if __name__ == "__main__":
    main()
