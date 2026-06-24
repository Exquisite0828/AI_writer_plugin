# EPS Demo System Architecture Context

Document status: project source for this demo fixture (current project System Architecture).

## ECU Boundary

The software architecture scope is the EPS controller application and its interaction with RTE, selected BSW services, and OS scheduling on the target MCU.

## Operating Modes

| Mode | Description |
|---|---|
| Init | BSW and application initialization |
| Normal | Assist control active |
| Degraded | Reduced assist after fault detection |
| Sleep | Low-power state with wakeup monitoring |

## External Interface Context

| Interface | Direction from ECU software view |
|---|---|
| Steering torque input | In |
| Vehicle speed input | In |
| Assist command output | Out |
| Diagnostic status reporting | Out |
