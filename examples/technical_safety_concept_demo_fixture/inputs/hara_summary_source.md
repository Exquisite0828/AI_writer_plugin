# HARA Summary Extract (FTTI and Safe State)

Document status: project source for this demo fixture.

## Provided HARA Trace

Hazardous event HE-01: unintended steering assist torque during low-speed parking maneuver.
Associated safety goal: SG-01.
Provided ASIL: ASIL B.
Fault Tolerant Time Interval (FTTI) for HE-01: 300 ms.
Safe state for HE-01: remove automated parking assist torque request; manual steering assist remains available.

Hazardous event HE-02: parking assist continues after steering angle input becomes unavailable.
Associated safety goal: SG-02.
Provided ASIL: ASIL B.
Fault Tolerant Time Interval (FTTI) for HE-02: not provided in this extract.
Safe state for HE-02: degrade parking assist and notify the driver.

## Boundary

This extract is supplied as a trace and timing input for Technical Safety Concept writing only.
It is not a new HARA, not a HARA approval record, and not a Technical Safety Concept.
Only the FTTI and safe state values explicitly listed here may be used; values marked as not provided remain open.
