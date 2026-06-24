# EPS Demo Diagnostic Software Constraints

Document status: project source for this demo fixture.

## Diagnostic Chain (Software Layer)

1. Sensor fault detected in sensor abstraction component.
2. Degraded mode manager notified.
3. Dem event status updated via BSW service interface.
4. Dcm exposes diagnostic status to external tester when requested.

## Degraded Behavior

When critical sensor fault is active, assist command shall be limited per SWR-F-002 (see SwRS source).
