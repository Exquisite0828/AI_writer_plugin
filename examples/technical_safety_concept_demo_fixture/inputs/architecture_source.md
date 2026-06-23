# Preliminary System Architecture

Document status: project source for this demo fixture.

## Safety-Relevant Architecture Elements

- `EPS_ECU`: electric steering assist controller hosting the parking assist control path.
- `SA_SENSOR`: steering angle sensor providing `SA_ANGLE`.
- `STEER_ACTUATOR`: steering actuator controller receiving `AST_TORQUE_REQ`.
- `MONITOR_CORE`: monitoring function inside `EPS_ECU` for plausibility checks.
- `HMI_CLUSTER`: instrument cluster receiving `PARK_ASSIST_DEGRADED` for driver notification.
- `PWR_SUPPLY`: power supply monitoring input.

## Allocation Notes

The plausibility and monitoring concept is allocated to `MONITOR_CORE` within `EPS_ECU`.
Driver notification is allocated to `HMI_CLUSTER` via signal `PARK_ASSIST_DEGRADED`.
The safe torque removal path is allocated to `EPS_ECU` control of `AST_TORQUE_REQ`.

## Known Open Items

The source does not confirm whether `MONITOR_CORE` runs on an independent core or watchdog.
The source does not confirm the communication integrity mechanism (for example end-to-end protection) on `AST_TORQUE_REQ`.
The source does not confirm redundancy for `SA_SENSOR`.
