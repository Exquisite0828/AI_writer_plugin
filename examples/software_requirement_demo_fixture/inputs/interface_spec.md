# EPS Demo Interface Specification

Document status: project source for this demo fixture.

| Interface ID | Name | Direction | Counterpart | Notes |
|---|---|---|---|---|
| IF-SIG-001 | Steering torque input | In | Steering torque sensor | Cyclic sampling context 5 ms |
| IF-SIG-002 | Vehicle speed input | In | Vehicle network gateway | Timeout behavior pending confirmation |
| IF-SIG-003 | Assist command output | Out | Assist actuator | Cyclic output context 5 ms |
| IF-SIG-004 | Diagnostic status output | Out | Vehicle network gateway | On event and on request |

Open: detailed signal scaling and timeout values are not in this demo source.
