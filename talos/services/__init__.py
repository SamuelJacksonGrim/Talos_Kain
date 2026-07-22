"""Services layer: orchestration.

These modules wire domain logic to ports and drive the live cycle — the
sensorium, the policy, the motor executor, skill extraction/publishing, and
the organism loop itself. They depend on ``talos.domain`` and on the port
interfaces, never on concrete infrastructure classes.
"""
