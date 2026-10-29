# LOX/CH4 Propulsion Modelling and Verification

A personal engineering project exploring LOX/CH4 propulsion modelling using MATLAB/Simulink, Simscape Fluids and Python.

The repository currently contains two separate modelling activities:

1. A prescribed-flow baseline for propellant consumption, thrust and accumulated impulse.
2. Standalone component test benches for pressure-driven flow through equivalent hydraulic restrictions.

The focus is on explicit assumptions, analytical references, numerical consistency checks and reproducible documentation.

This is a work-in-progress numerical project, not a complete or experimentally validated rocket-engine design.

## Documentation

| Project area | Description | Documentation |
|---|---|---|
| Prescribed-flow baseline | Step and startup-ramp profiles, consumption analysis, thrust and impulse calculations, analytical checks and automated tests | [Baseline README](docs/baseline/README.md) |
| Component-level modelling | Water restriction test, preliminary LOX equivalent-area sizing, fluid properties and Simscape operating-point checks | [Components README](docs/components/README.md) |

## Relationship between the models

In the baseline, mass flow is prescribed and its consequences are calculated.

In the component test benches, mass flow is calculated from prescribed pressure boundaries, fluid properties and restriction parameters.

The baseline LOX nominal flow of 22.660360 kg/s provides the target for the preliminary LOX restriction sizing.

The two modelling activities are not yet dynamically coupled. The component test benches do not currently generate the baseline startup profiles.

## Current status

### Prescribed-flow baseline

- Selectable Step and linear startup-ramp profiles.
- MATLAB simulation and data-export scripts.
- Python analysis of cumulative propellant consumption.
- Thrust and accumulated-impulse comparison.
- Analytical and mass-balance checks.
- Automated tests using saved simulation exports.

### Component-level modelling

- Initial isothermal-liquid restriction test using water properties.
- Python sizing of a preliminary LOX equivalent flow area.
- Oxygen-property calculations using CoolProp.
- LOX Simscape test with fixed upstream and downstream pressures.
- Updated-area result of 22.66 kg/s, consistent with the sizing target at the displayed precision.

Higher-precision component exports and automated component checks remain future work.

## Repository layout

```text
docs/        Detailed baseline and component documentation
models/      Simulink and Simscape model files
scripts/     MATLAB and Python scripts
src/         Reusable Python source code
tests/       Automated Python tests
results/     Saved simulation exports and generated figures
```

## Software requirements

### Baseline

- MATLAB
- Simulink

### Component test benches

- MATLAB
- Simulink
- Simscape
- Simscape Fluids

The component models were developed using MATLAB/Simulink R2026a.

### Python

Python 3.10 or newer, subject to dependency compatibility.

Direct dependencies are listed in `requirements.txt`:

- NumPy
- SciPy
- Matplotlib
- pytest
- CoolProp 8.0.0

## Python setup

Run the following commands from the repository root.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The local virtual environment should not be committed.

Run the existing automated tests with:

```powershell
python -m pytest tests
```

The tests use saved datasets and do not automatically run MATLAB or Simulink. They do not currently verify the component test benches.

See the detailed documentation for simulation, analysis and component-sizing commands.

## Modelling boundaries

- The baseline uses prescribed startup profiles and constant specific impulse.
- The component models use equivalent hydraulic restrictions and prescribed pressure boundaries.
- No coupled feed-system, combustion-chamber or nozzle model is currently implemented.
- No experimental validation is claimed.
- The 100 kN thrust and 350 s specific impulse are baseline inputs, not demonstrated outputs of a physical engine model.

The longer-term direction is to investigate progressively coupled propulsion-system models for a launch-vehicle first-stage application. This remains a development objective rather than a description of the current model capability.