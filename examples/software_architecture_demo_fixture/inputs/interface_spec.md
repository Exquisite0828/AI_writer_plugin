# EPS Demo Software Interface Specification

Document status: project source for this demo fixture.

## RTE Ports (Application View)

| Port name | Type | Direction | Data / service | Counterpart |
|---|---|---|---|---|
| PpSteerTorque | Receiver | Consumer | SteerTorque_degNm | Sensor abstraction SWC |
| PpVehSpeed | Receiver | Consumer | VehSpeed_kph | Network abstraction SWC |
| PpAssistCmd | Sender | Provider | AssistCmd_Nm | Actuator abstraction SWC |
| PpDiagStatus | Sender | Provider | DiagEventStatus | Dcm interaction |

## Service Interfaces

| Service | Direction | Notes |
|---|---|---|
| Dem_SetEventStatus | Consumer | Report DTC-related events from App layer |
