# EPS Demo ODD and Operational Scenarios

Document status: project source for this demo fixture.

## Operating Environment

| Parameter | Range / Value | Notes |
|---|---|---|
| Vehicle type | Passenger car | Demo project |
| Road type | Public roads | Licensed driver operation |
| Speed range (assist active) | 0–180 km/h | Calibration band; upper limit open pending sign-off |
| Ambient temperature (ECU) | -40 °C to +85 °C | Per ECU mounting location specification |
| Supply voltage | 9–16 V (nominal 12 V) | Vehicle electrical system |

## Operational Situations (OS-xx)

| OS ID | Description | Mode |
|---|---|---|
| OS-01 | Normal driving on dry public road | Normal assist |
| OS-02 | Low-speed maneuvering (parking lot) | Normal assist |
| OS-03 | Highway cruising | Normal assist |
| OS-04 | Sensor plausibility fault detected | Degraded assist |
| OS-05 | Motor driver fault detected | Degraded assist / assist disabled |
| OS-06 | Ignition off | Assist disabled |

## Operating Modes

| Mode | Description |
|---|---|
| Normal assist | Assist enabled; inputs plausible; no active disabling fault |
| Degraded assist | Assist reduced or disabled; diagnostic indication may be active |
| Off | No assist; ignition or enable conditions not met |

**Note:** This document describes operational context for item definition and HARA input. It does not assign exposure (E) ratings or hazard conclusions.
