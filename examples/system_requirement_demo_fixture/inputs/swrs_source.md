# EPS Demo Stakeholder Requirements Extract

Document status: project source for this demo fixture.
Product scope: Electric Power Steering (EPS) controller product for passenger vehicle steering assist.

## Stakeholder Requirements

| Upstream ID | Name | Requirement |
|---|---|---|
| SWRS-001 | Steering assist torque | The EPS controller shall provide steering assist torque based on driver steering torque input and vehicle speed. |
| SWRS-002 | Normal operation availability | The EPS controller shall provide assist torque when ignition is on, sensor inputs are plausible, and no disabling fault is active. |
| SWRS-003 | Degraded assist operation | The EPS controller shall reduce or disable assist when plausibility or diagnostic faults are detected. |
| SWRS-004 | Diagnostic status reporting | The EPS controller shall report diagnostic and degraded-mode status to the vehicle network. |

## Performance and Environmental Constraints

- Assist function operating speed range: 0-180 km/h (open: final calibration limits pending).
- ECU ambient operating temperature range: -40 degC to +85 degC.
- Nominal supply voltage: 12 V vehicle electrical system (open: detailed voltage range pending).

## Scope Exclusions

This extract does not define braking, propulsion, lane keeping, automated driving, or detailed software requirements.
