# Steering Assist Item Definition

Document status: project source for this demo fixture.

## Item Scope

The item is the electric steering assist control function for low-speed parking assist.
The function receives steering angle, vehicle speed, driver torque, and power supply status.
The function outputs an assist torque request to the steering actuator controller.

## Operational Context

The function is active below 30 km/h when parking assist mode is enabled by the driver.
The item is not responsible for autonomous path planning or braking.
The system shall transition to manual steering assist only when the parking assist control path is unavailable.

## Interfaces

- Steering angle sensor input: project source signal `SA_ANGLE`.
- Vehicle speed input: project source signal `VEH_SPEED`.
- Driver torque input: project source signal `DRV_TORQUE`.
- Assist torque output: project source signal `AST_TORQUE_REQ`.
- Degradation notification output: project source signal `PARK_ASSIST_DEGRADED`.

## Known Open Items

The source package does not confirm diagnostic coverage targets.
The source package does not confirm the controller hardware redundancy topology.
The source package does not confirm production release approval.
