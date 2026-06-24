# EPS Demo System Architecture Context

Document status: project source for this demo fixture (current project System Architecture).

## ECU Boundary

The SwRS scope is the EPS controller application software interacting with RTE/BSW on the target MCU.

## Operating Modes

| Mode | Software-relevant behavior |
|---|---|
| Init | Application and BSW bring-up |
| Normal | Full assist control active |
| Degraded | Limited assist after fault |
| Sleep | Low-power with wakeup monitoring |

## Interface Context for Software

| System interface | Software consumer / provider hint |
|---|---|
| Steering torque input | Sampled in 5 ms task context |
| Vehicle speed input | Received via Com stack |
| Assist command output | Provided in 5 ms task context |
| Diagnostic status | Reported via Dcm/Dem path |
