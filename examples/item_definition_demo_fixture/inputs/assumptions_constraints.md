# EPS Demo Assumptions and Constraints

Document status: project source for this demo fixture.

## Assumptions

| ID | Assumption | Dependency |
|---|---|---|
| A-01 | The vehicle is operated by a licensed driver on public roads. | Driver / regulatory context |
| A-02 | The driver can apply steering torque to override unintended assist. | Human-machine interaction |
| A-03 | Manual steering remains mechanically possible if power assist is unavailable (with increased effort). | Mechanical steering path |
| A-04 | Vehicle speed signal on CAN is provided by a qualified upstream ECU with project-agreed integrity. | Powertrain / gateway ECU |
| A-05 | Steering torque sensor is installed and calibrated per supplier specification. | Sensor supplier |

## Dependencies

| ID | Dependency | Description |
|---|---|---|
| D-01 | Vehicle electrical system | Stable supply within specified voltage range |
| D-02 | CAN network availability | Required signals delivered per matrix Demo-Matrix-v0.1 |
| D-03 | Mechanical steering linkage | Transmits driver and assist torque to road wheels |

## Constraints

- The item does not perform autonomous steering path planning.
- The item does not control braking or propulsion.
- Diagnostic coverage targets and timing limits for fault detection are **not confirmed** in this source package (open item).
