# EPS Demo System Architecture

Document status: project source for this demo fixture.

## Item Identification

| Field | Value |
|---|---|
| Item name | EPS Steering Assist |
| Item version | Demo-0.1 |
| Variant | Passenger vehicle EPS rack-assist |

## In Scope

The following are **inside** the item boundary:

| Subsystem / Element | Description |
|---|---|
| Steering torque sensor interface | Receives driver steering torque signal |
| Vehicle speed input interface | Receives vehicle speed signal |
| EPS electronic control unit (ECU) | Computes assist torque request |
| Motor driver | Drives assist motor per ECU command |
| Assist motor | Applies torque to steering mechanism |
| Steering rack torque assistance output | Mechanical assist at rack/gear interface |
| Ignition and diagnostic state inputs | Mode and fault context for assist logic |

## Out of Scope

The following are **outside** the item boundary:

| Element | Reason |
|---|---|
| Braking control | Separate vehicle item |
| Propulsion / traction control | Separate vehicle item |
| Lane keeping / ADAS path control | Separate vehicle item |
| Road wheel and tire mechanical design | Vehicle mechanical domain |
| Steering column mechanical design (beyond sensor interface) | Upstream mechanical domain |
| HARA hazard ratings and safety goals | Downstream safety analysis activity |

## Architecture Notes

The EPS ECU receives sensor inputs, calculates assist torque, and commands the motor driver. Manual steering remains mechanically possible if assist is unavailable, with increased driver effort.
