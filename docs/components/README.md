# Component-Level Modelling — Equivalent Hydraulic Restrictions

[Project overview](../../README.md) | [Prescribed-flow baseline](../baseline/README.md)

## Purpose

This part of the project introduces pressure-driven component modelling using Simscape Fluids.

The current models are standalone isothermal-liquid test benches with prescribed upstream and downstream pressures.

They represent equivalent hydraulic restrictions, not detailed injector elements or a complete propulsion system.

Python scripts support preliminary area sizing and fluid-property calculations.

## Current status

| Activity | Status |
|---|---|
| Initial water restriction test | Completed at displayed precision |
| Preliminary LOX equivalent-area sizing | Implemented |
| Oxygen-property calculations | Implemented using CoolProp 8.0.0 |
| Updated-area LOX simulation | Displayed mass flow of 22.66 kg/s |
| Initial LOX operating-point consistency check | Completed at displayed precision |
| Higher-precision numerical export | Not yet implemented |
| Automated component checks | Not yet implemented |
| Coupling to baseline or dynamic chamber | Not yet implemented |

## Files

| File | Role |
|---|---|
| `models/simulink/injector_component_test.slx` | Initial restriction test using water properties |
| `models/simulink/lox_injector_test.slx` | LOX equivalent-restriction test |
| `scripts/python/size_lox_injector.py` | Preliminary LOX equivalent-area sizing |
| `scripts/python/lox_properties.py` | Oxygen-property calculations |

Paths and commands in this document refer to the repository root unless explicitly stated otherwise.

## Requirements

- MATLAB
- Simulink
- Simscape
- Simscape Fluids
- Python dependencies from the root `requirements.txt`

The component models were developed using MATLAB/Simulink R2026a.

The documented property calculations used CoolProp 8.0.0.

See the [project overview](../../README.md#python-setup) for Python setup.

## Test-bench structure

The initial network contains:

- an upstream reservoir;
- a constant-area `Orifice (IL)`;
- a `Flow Rate Sensor (IL)`;
- a downstream reservoir;
- an `Isothermal Liquid Properties (IL)` block;
- a `Solver Configuration` block;
- physical-signal conversion and Simulink visualisation.

The reservoirs impose constant pressure boundary conditions.

They do not represent finite propellant inventories or a dynamic combustion chamber.

## Initial water restriction check

Model:

```text
models/simulink/injector_component_test.slx
```

### Parameters

| Parameter | Value |
|---|---:|
| Upstream absolute pressure | 1 MPa |
| Downstream absolute pressure | 0.5 MPa |
| Restriction area | 1e-5 m² |
| Discharge coefficient | 0.64 |
| Port cross-sectional area | `inf` |
| Pressure recovery | Disabled |
| Entrained-air fraction | 0 |
| Reference liquid density | 998.21 kg/m³ |

### Simplified reference

```text
Mass flow =
Cd × area × sqrt(2 × density × pressure drop)
```

### Recorded results

| Method | Mass flow |
|---|---:|
| Simplified Python reference | 0.202205 kg/s |
| Simscape display | Approximately 0.2022 kg/s |

The results agree at the displayed precision.

This is a single operating-point consistency check, not complete component characterisation or experimental validation.

## Preliminary LOX sizing

Script:

```text
scripts/python/size_lox_injector.py
```

Run from the repository root:

```powershell
python scripts/python/size_lox_injector.py
```

The target is the nominal LOX flow from the prescribed-flow baseline.

### Assumptions

| Parameter | Value |
|---|---:|
| Target mass flow | 22.660360 kg/s |
| Assumed temperature | 90 K |
| Upstream absolute pressure | 6 MPa |
| Downstream absolute pressure | 5 MPa |
| Pressure drop | 1 MPa |
| Pressure-drop / downstream-pressure ratio | 0.20 |
| Discharge coefficient | 0.64 |

These values are preliminary assumptions, not an optimised design.

The downstream pressure is a prescribed boundary, not a calculated chamber pressure.

The upstream pressure is immediately before the restriction. It is not automatically a tank-pressure requirement.

### Area calculation

```text
Equivalent area =
target mass flow / (Cd × sqrt(2 × density × pressure drop))
```

The equivalent area describes aggregate hydraulic flow capacity. It does not define the number, diameter or arrangement of individual injection elements.

The equivalent circular diameter is only the diameter of a circle having the same area.

## Oxygen properties

Script:

```text
scripts/python/lox_properties.py
```

Run:

```powershell
python scripts/python/lox_properties.py
```

The script evaluates oxygen properties at 90 K using CoolProp.

### Recorded results

| Property | Reference | Restriction outlet | Restriction inlet |
|---|---:|---:|---:|
| Absolute pressure | 1.01325 bar | 50 bar | 60 bar |
| Density | 1142.108492 kg/m³ | 1152.617849 kg/m³ | 1154.672179 kg/m³ |
| Dynamic viscosity | 1.95647258e-4 Pa·s | 2.05326366e-4 Pa·s | 2.07288990e-4 Pa·s |
| Kinematic viscosity | 1.71303567e-7 m²/s | 1.78139152e-7 m²/s | 1.79521940e-7 m²/s |
| Isothermal bulk modulus | 5.12866481e8 Pa | 5.57136372e8 Pa | 5.66013155e8 Pa |

These are numerical property-model outputs, not experimental measurements made in this project.

## Fluid-property approximation in Simscape

The LOX test bench uses:

- reference properties at atmospheric pressure and an assumed temperature of 90 K;
- zero entrained air;
- constant isothermal bulk modulus.

The corresponding density approximation is:

```text
density(p) =
reference density × exp((p − reference pressure) / bulk modulus)
```

The updated Python sizing calculation uses the mean inlet and outlet densities obtained with this approximation.

This differs from evaluating the full CoolProp equation of state at every operating pressure.

The assumed temperature enters through the selected fluid properties. The isothermal test bench does not solve an energy balance.

## LOX sizing iterations

Model:

```text
models/simulink/lox_injector_test.slx
```

| Stage | Sizing density | Equivalent area | Recorded Simscape result |
|---|---|---:|---|
| Initial | Constant 1141 kg/m³ | 741.189 mm² | Approximately 22.79 kg/s |
| Updated | Mean operating density of approximately 1154.2 kg/m³ using the constant-bulk-modulus approximation | 736.940 mm² | 22.66 kg/s at displayed precision |

The initial displayed flow exceeded the target by approximately 0.57%.

The area was updated to align the sizing assumptions more closely with the Simscape fluid configuration. The discharge coefficient was not adjusted to force agreement.

## Updated LOX operating point

The area entered in the orifice block is:

```text
7.36940222e-4 m²
```

The equivalent circular diameter is:

```text
30.632 mm
```

### Recorded result

| Quantity | Value |
|---|---:|
| Python sizing target | 22.660360 kg/s |
| Simscape displayed mass flow | 22.66 kg/s |
| Upstream absolute pressure | 6 MPa |
| Downstream absolute pressure | 5 MPa |
| Assumed temperature | 90 K |
| Discharge coefficient | 0.64 |

The simulated flow is consistent with the sizing target at the displayed precision.

This completes the initial updated-area operating-point check.

The displayed result does not establish exact numerical agreement beyond its shown digits. A higher-precision numerical export is needed to quantify the residual difference and apply a documented tolerance.

This is numerical consistency checking under stated assumptions, not experimental validation of an injector.

## Running the Simscape models

1. Open the required model from `models/simulink/`.
2. Review reservoir pressures, restriction parameters and fluid properties.
3. Confirm that the PS–Simulink Converter output unit is `kg/s`.
4. Run the simulation.
5. Read the mass flow from the Scope or Display.
6. Compare against a reference calculated using consistent assumptions.

The current test benches use a simulation stop time of 1 s.

The boundary pressures are constant. These tests do not represent a commanded ignition sequence.

Parameters are currently transferred manually from Python outputs to Simscape block dialogs.

The Python scripts do not automatically configure or run the models.

## Verification scope

Completed:

- Initial water operating-point comparison at displayed precision.
- Execution of oxygen-property and LOX-sizing scripts.
- Initial updated-area LOX operating-point comparison at displayed precision.

Not yet implemented:

- Higher-precision exported component results.
- Automated tolerance-based component checks.
- Automated parameter transfer.
- A documented multi-point verification campaign.
- Experimental validation.

The baseline pytest suite does not verify these component models.

## Limitations

- Equivalent hydraulic restriction rather than detailed injector geometry.
- Prescribed pressure boundaries.
- Isothermal properties at an assumed temperature.
- Constant bulk-modulus approximation.
- Assumed discharge coefficient.
- No finite tank inventories.
- No selected coupled feed-system architecture.
- No atomisation, mixing, combustion, cavitation or heat-transfer model.
- No dynamic combustion chamber.
- No coupled nozzle.
- No demonstrated physical-engine thrust or specific impulse.

## Relationship to the baseline

The baseline provides the nominal LOX mass-flow target.

The component test bench calculates flow from prescribed pressures and restriction parameters.

The two models remain separate. The restriction does not yet supply a time-dependent flow signal to the baseline, and the baseline ramp is not a prediction of component dynamics.

## Next steps

- Export LOX flow with sufficient numerical precision.
- Define a comparison tolerance and quantify the residual difference.
- Add reproducible component parameter initialization.
- Automate result export and checks.
- Investigate pressure-drop and discharge-coefficient sensitivity.
- Extend the equivalent-restriction approach to the CH4 branch.
- Define the scope and interfaces for future coupling.

The longer-term objective is a progressively coupled propulsion-system model. This objective should remain distinct from the capabilities of the current standalone test benches.