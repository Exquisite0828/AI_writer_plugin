# EPS Demo Foreseeable Misuse Input

Document status: project source for this demo fixture.  
Purpose: ISO 26262-3 §5.4.4 b — reasonably foreseeable misuse scenarios.

## Foreseeable Misuse Scenarios

| MIS ID | Misuse Description | Related Function | Status |
|---|---|---|---|
| MIS-01 | Driver relies entirely on assist and releases steering wheel at highway speed expecting lane keeping (function not in item scope) | F-01, F-02 | Candidate — requires HITL confirmation |
| MIS-02 | Aftermarket modification bypasses torque sensor plausibility checks | F-02, F-03 | Candidate — requires HITL confirmation |
| MIS-03 | Continued driving with known EPS degraded indication ignored by driver | F-03, F-04 | Candidate — requires HITL confirmation |
| MIS-04 | Installation of non-OEM steering components altering sensor calibration without recalibration | F-01, F-02 | Candidate — requires HITL confirmation |

## Open Items

- Workshop service procedures for sensor replacement are not included in this source package.
- Fleet operator training materials are not included.

**Note:** Misuse scenarios support item definition and downstream HARA. They are not hazard events and do not include S/E/C or ASIL ratings.
