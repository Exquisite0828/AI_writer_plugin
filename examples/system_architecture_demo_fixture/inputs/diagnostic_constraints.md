# EPS Demo Diagnostic and Degradation Constraints

Document status: project source for this demo fixture.

## Diagnostic Constraints

| Diagnostic ID | Context | System-Level Requirement Intent |
|---|---|---|
| DIAG-001 | Sensor plausibility fault | The EPS controller shall detect unavailable or implausible required sensor inputs and enter degraded assist operation. |
| DIAG-002 | Vehicle speed input timeout | The EPS controller shall treat missing vehicle speed input as a degraded operation trigger when timeout criteria are met. |
| DIAG-003 | Diagnostic status reporting | The EPS controller shall report diagnostic status to the vehicle network. |

## Open Constraints

- Final DTC identifiers are not provided in this demo source.
- Fault reaction timing is not provided in this demo source.
- Detailed software diagnostic implementation is outside System Architecture scope.
