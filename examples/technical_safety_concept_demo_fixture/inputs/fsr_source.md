# Confirmed Functional Safety Requirements

Document status: project source for this demo fixture.
This source provides the upstream functional safety requirements for technical safety concept derivation.
It is not a blanket Technical Safety Concept approval.

## Functional Safety Requirement Table

| FSR ID | Requirement statement | Linked safety goal | ASIL |
| --- | --- | --- | --- |
| FSR-01 | The steering assist function shall detect an implausible assist torque request and stop applying automated parking assist torque. | SG-01 | ASIL B |
| FSR-02 | The steering assist function shall detect unavailable or implausible steering angle input and stop automated parking assist operation. | SG-02 | ASIL B |
| FSR-03 | The steering assist function shall notify the driver when automated parking assist is degraded or deactivated. | SG-01, SG-02 | ASIL B |

## Boundary

This source defines functional-level requirements only.
It does not define technical safety mechanisms, architecture allocation, fault tolerance time values, or technical safety requirements.
Those are to be derived in the Technical Safety Concept under human confirmation.
