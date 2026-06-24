# EPS Demo Interface Specification

Document status: project source for this demo fixture.

## Interface Summary

| Interface ID | Name | Type | Direction | Counterpart | Description |
|---|---|---|---|---|---|
| IF-SIG-001 | Driver steering torque input | Sensor signal | In | Steering torque sensor | Provides driver steering torque value to the EPS controller. |
| IF-SIG-002 | Vehicle speed input | Vehicle network signal | In | Vehicle network gateway | Provides vehicle speed value to the EPS controller. |
| IF-SIG-003 | Assist command output | Actuator command | Out | Assist actuator | Provides assist command from the EPS controller to the assist actuator. |
| IF-SIG-004 | Diagnostic status output | Vehicle network signal | Out | Vehicle network gateway | Reports diagnostic and degraded-mode status. |

## Interface Notes

- Timeout behavior for vehicle speed input is pending project confirmation.
- Detailed signal scaling is outside this demo source and should remain an open item.
