"""SC2 curriculum (DORMANT — spec / README first milestone).

The forcing function's curriculum: beat the built-in AI on Easy, then
re-baseline at Medium and watch the second learning curve. This module will
define the ladder of opponents/difficulties and the re-baselining protocol
that turns "did it win once" into "did it measurably learn."

Dormant until SC2Env is implemented. The mock world's contexts are the
stand-in for this ladder in milestone zero.
"""

from __future__ import annotations

# Difficulty ladder, in order. Present as data now so the wiring is obvious
# later; nothing consumes it yet.
DIFFICULTY_LADDER = ("VeryEasy", "Easy", "Medium", "MediumHard", "Hard")

FIRST_MILESTONE = "Easy"      # beat built-in AI here first
REBASELINE_AT = "Medium"      # then re-baseline and watch the second curve
