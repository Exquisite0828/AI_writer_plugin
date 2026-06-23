# EPS Demo Interface Specification

Document status: project source for this demo fixture.

## External Interfaces (IF-xx)

| IF ID | Name | Type | Direction | Counterpart | Signal / Mechanical Description |
|---|---|---|---|---|---|
| IF-01 | Driver steering torque | Sensor input | Input → Item | Steering torque sensor | Analog/digital torque signal `STR_TORQUE_IN` |
| IF-02 | Vehicle speed | Bus input | Input → Item | Vehicle network (CAN) | Signal `VEH_SPEED` on powertrain CAN |
| IF-03 | Ignition state | Bus input | Input → Item | Body / gateway ECU | Signal `IGN_STATE` |
| IF-04 | EPS diagnostic state | Internal / bus | Input → Item | Vehicle diagnostic gateway | Signal `EPS_DIAG_STATE` |
| IF-05 | Commanded assist torque | Actuator output | Output ← Item | Motor driver | Command `ASSIST_TORQUE_CMD` |
| IF-06 | Diagnostic status | Bus output | Output ← Item | Instrument cluster / gateway | Signal `EPS_DIAG_STATUS` |
| IF-07 | Degraded mode indication | Bus output | Output ← Item | Instrument cluster / gateway | Signal `EPS_DEGRADED_MODE` |
| IF-08 | Rack assist torque (mechanical) | Mechanical output | Output ← Item | Steering rack / gear | Mechanical torque at assist interface |

## Interface Assumptions

- CAN signal naming and matrix version: Demo-Matrix-v0.1 (project source).
- Sensor failure detection is handled inside the item; sensor hardware design is outside item boundary except interface point.
