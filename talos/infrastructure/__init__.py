"""Infrastructure layer: adapters.

Concrete implementations of the domain ports — SQLite stores, environments
(mock and, later, StarCraft II), logging. This is the only layer allowed to
import ``sqlite3``, ``pysc2``, and friends. The dependency arrow points
inward: infrastructure knows about the domain; the domain knows nothing about
infrastructure.
"""
