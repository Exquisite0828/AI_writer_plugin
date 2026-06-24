# EPS Demo Software Requirements Extract (SwRS)

Document status: project source for this demo fixture.

## SWR-F-001 Steering Assist Control

The EPS application software shall compute an assist command from steering torque and vehicle speed inputs.

## SWR-F-002 Degraded Operation

The EPS application software shall enter a degraded assist mode when a critical sensor fault is detected and report the condition via diagnostic services.

## SWR-IF-001 Steering Torque Input

| Field | Value |
|---|---|
| Direction | Consumer |
| Counterpart | Steering torque sensor interface (system layer) |
| Trigger | Cyclic, 5 ms task context |

## SWR-IF-002 Vehicle Speed Input

| Field | Value |
|---|---|
| Direction | Consumer |
| Counterpart | Vehicle network interface (system layer) |
| Trigger | Received via CAN signal update |

## SWR-IF-003 Assist Command Output

| Field | Value |
|---|---|
| Direction | Provider |
| Counterpart | Assist actuator command interface (system layer) |
| Trigger | Cyclic, 5 ms task context |
