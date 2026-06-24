# EPS Demo System Requirements Extract (SyRS)

Document status: project source for this demo fixture.

## SYS-F Functional Requirements

| ID | Requirement |
|---|---|
| SYS-F-001 | The EPS controller shall provide steering assist based on driver steering torque and vehicle speed. |
| SYS-F-002 | The EPS controller shall provide assist when ignition is on and required inputs are plausible. |
| SYS-F-003 | The EPS controller shall reduce or disable assist when plausibility or diagnostic faults are detected. |
| SYS-F-004 | The EPS controller shall report diagnostic and degraded-mode status to the vehicle network. |

## SYS-IF Interface Requirements

| ID | Name | Direction | Counterpart |
|---|---|---|---|
| SYS-IF-001 | Steering torque input | In | Steering torque sensor |
| SYS-IF-002 | Vehicle speed input | In | Vehicle network gateway |
| SYS-IF-003 | Assist command output | Out | Assist actuator |
| SYS-IF-004 | Diagnostic status output | Out | Vehicle network gateway |

## Trace Anchor

Upstream stakeholder IDs SWRS-001 .. SWRS-004 map to SYS-F-001 .. SYS-F-004 in this demo extract.
