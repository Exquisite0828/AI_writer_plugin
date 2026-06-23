# EPS Demo System Requirements Extract (SyRS)

Document status: project source for this demo fixture.  
Item: Electric Power Steering (EPS) assist function for passenger vehicle.

## Functional Requirements

| Req ID | Name | Description |
|---|---|---|
| F-01 | Steering assist torque generation | The EPS function shall generate assist torque based on driver steering torque input and vehicle speed. |
| F-02 | Normal assist operation | The EPS function shall provide assist torque when ignition is on, sensor inputs are plausible, and no disabling fault is active. |
| F-03 | Degraded assist handling | The EPS function shall reduce or disable assist and indicate degraded operation when plausibility or diagnostic faults are detected. |
| F-04 | Diagnostic status reporting | The EPS function shall report diagnostic and degraded-mode status to the vehicle network. |

## Non-Functional Constraints (excerpt)

- Assist shall be available for vehicle speed range 0–180 km/h per project calibration band (open: final calibration limits pending).
- Operating temperature range for ECU: -40 °C to +85 °C (ambient reference per ECU mounting location).

## Exclusions (requirements scope)

This SyRS extract does not define braking, propulsion, lane keeping, or automated driving functions.
