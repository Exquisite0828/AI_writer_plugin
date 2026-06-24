# EPS Demo System Architecture Context

Document status: project source for this demo fixture.

## ECU Boundary

The System Requirement document scope is the EPS controller product, including steering torque input handling, vehicle speed input handling, assist command generation, degraded operation coordination, and diagnostic status reporting.

## In Scope

| Element | Description |
|---|---|
| EPS controller ECU | Receives steering torque and vehicle speed information, computes assist command, and reports status. |
| Steering torque sensor interface | Provides driver steering torque information to the EPS controller. |
| Vehicle network interface | Provides vehicle speed information and receives diagnostic status messages. |
| Assist actuator command interface | Receives assist command from the EPS controller. |

## Out of Scope

| Element | Description |
|---|---|
| Braking controller | Not controlled by the EPS controller. |
| Propulsion controller | Not controlled by the EPS controller. |
| Lane keeping function | Not defined by this SyRS demo. |
| Automated driving function | Not defined by this SyRS demo. |
