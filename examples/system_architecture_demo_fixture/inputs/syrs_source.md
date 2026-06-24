# EPS Demo System Requirements Extract

Document status: project source for this demo fixture.
Product scope: Electric Power Steering (EPS) controller product for passenger vehicle steering assist.

## Functional System Requirements

| SYS-F ID | Requirement statement | Linked upstream ID | Priority | Verification method |
|---|---|---|---|---|
| SYS-F-001 | The EPS controller shall compute steering assist command from driver steering torque input and vehicle speed input. | SWRS-001 | High | Integration test |
| SYS-F-002 | The EPS controller shall provide assist command output when ignition is on, required sensor inputs are plausible, and no disabling fault is active. | SWRS-002 | High | Integration test |
| SYS-F-003 | The EPS controller shall reduce or disable assist command output when plausibility or diagnostic faults are detected. | SWRS-003 | High | Integration test |
| SYS-F-004 | The EPS controller shall report diagnostic and degraded-mode status to the vehicle network. | SWRS-004 | Medium | Integration test |

## Interface System Requirements

| SYS-IF ID | Interface name | Type | Direction | Counterpart | Requirement statement | Linked upstream ID |
|---|---|---|---|---|---|---|
| SYS-IF-001 | Driver steering torque input | Sensor signal | In | Steering torque sensor | The EPS controller shall receive driver steering torque input for assist computation. | SWRS-001 |
| SYS-IF-002 | Vehicle speed input | Vehicle network signal | In | Vehicle network gateway | The EPS controller shall receive vehicle speed input for assist computation. | SWRS-001 |
| SYS-IF-003 | Assist command output | Actuator command | Out | Assist actuator | The EPS controller shall output assist command to the assist actuator. | SWRS-001 |
| SYS-IF-004 | Diagnostic status output | Vehicle network signal | Out | Vehicle network gateway | The EPS controller shall report diagnostic and degraded-mode status on the vehicle network. | SWRS-004 |

## Performance and Environmental Constraints

| Constraint ID | Statement | Source |
|---|---|---|
| SYS-PERF-001 | Assist function operating speed range: 0-180 km/h (open: final calibration limits pending). | Stakeholder extract |
| SYS-ENV-001 | ECU ambient operating temperature range: -40 degC to +85 degC. | Stakeholder extract |
| SYS-ENV-002 | Nominal supply voltage: 12 V vehicle electrical system (open: detailed voltage range pending). | Stakeholder extract |

## Scope Exclusions

This extract does not define braking, propulsion, lane keeping, automated driving, software architecture, or hardware component-level design.
