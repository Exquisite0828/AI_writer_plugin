# EPS Demo System Notes

## Architecture Context

The EPS ECU receives steering torque sensor input and vehicle speed input.

The EPS ECU calculates assist torque and commands the motor driver.

The assist motor applies torque to the steering mechanism through the EPS gear interface.

The diagnostic monitor can request degraded operation when sensor plausibility checks fail.

## Operating Modes

Normal assist mode:

- EPS assist is enabled.
- steering torque sensor input is plausible.
- vehicle speed input is available.
- motor driver diagnostics report no active fault.

Degraded assist mode:

- assist may be reduced or disabled.
- manual steering remains possible with increased effort.
- a diagnostic indication may be reported.

## Candidate Malfunction Context

The source materials mention the following malfunction contexts for analysis:

- no assist torque when assist is expected
- excessive assist torque compared with driver demand
- assist torque in the wrong direction
- intermittent assist torque during steering input

These entries are candidate malfunction contexts for analysis. They are not confirmed hazards or final hazardous events.

## Evidence Limitations

The demo inputs do not contain confirmed operational scenario frequency.

The demo inputs do not contain confirmed severity, exposure, controllability, ASIL, or safety goal approval.

Those judgments require qualified human confirmation.
