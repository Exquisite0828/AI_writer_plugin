# EPS Demo Item Definition

## Item Boundary

The demo item is an electric power steering function for a passenger vehicle.

The item boundary includes:

- steering torque sensor
- vehicle speed signal input
- EPS electronic control unit
- motor driver
- assist motor
- steering rack torque assistance output

The item boundary excludes braking control, propulsion control, lane keeping, automated driving, and road wheel mechanical design.

## Intended Function

The EPS function provides steering assist torque based on driver steering input and vehicle speed.

The driver remains responsible for steering direction and steering effort.

The function is intended to reduce driver steering effort during normal driving and low-speed maneuvering.

## Inputs and Outputs

Inputs:

- driver steering torque signal
- vehicle speed signal
- ignition state
- EPS diagnostic state

Outputs:

- commanded assist torque
- diagnostic status indication
- degraded mode indication

## Operating Assumptions

The vehicle is operated by a licensed driver on public roads.

The driver can apply steering torque to override an unintended assist torque command.

Manual steering remains mechanically possible if power assist is unavailable, but steering effort may increase.

The item definition does not provide confirmed HARA severity, exposure, controllability, ASIL, or safety goal conclusions.
