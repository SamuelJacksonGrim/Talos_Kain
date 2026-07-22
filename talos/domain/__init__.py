"""Domain layer: pure organism logic.

Nothing in this package may import from ``talos.infrastructure`` or from any
third-party I/O library. It defines *what the organism is* — its types, its
ports (interfaces the outer layers implement), its admission gate, and its
reward calculus — independently of *how* any of it is stored or actuated.
"""
