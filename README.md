# LOX/CH4 Propellant Consumption Baseline

This repository contains a small, reproducible baseline workflow for a
LOX/CH4 rocket-engine propellant-consumption model. It combines a
Simulink model, MATLAB simulation and export scripts, and Python
analysis and automated checks.

## Scope

The model supports two startup profiles: an instantaneous Step and
a linear ramp followed by constant nominal flow. Separate LOX, CH4,
and total-flow branches feed Simulink integrators that compute the
cumulative propellant mass consumed during the simulation.

This is an internal consistency baseline. It does not yet validate
the model against experimental data or represent a detailed physical
engine startup or shutdown process.

## Nominal parameters and Step reference case

| Parameter | Value |
|---|---:|
| Nominal thrust input | 100000 N |
| Specific impulse input | 350 s |
| Simulation start time | 0 s |
| Simulation stop time | 10 s |
| Flow activation time | 1 s |
| Ramp duration | 0.5 s |
| Total nominal propellant flow | 29.1347 kg/s |
| LOX nominal flow | 22.6604 kg/s |
| CH4 nominal flow | 6.4744 kg/s |
| Oxidizer-to-fuel mass ratio | 3.50 |
| Step final total mass consumed | 262.2127 kg |

Nominal mass-flow rates are derived from the thrust and specific-impulse
inputs in `scripts/matlab/setup_simulation.m`.

The plotted masses represent cumulative propellant consumption,
not propellant remaining in the tanks.

## Repository layout

```text
models/     Simulink model files
scripts/    MATLAB and Python scripts
src/        Reusable Python source code
tests/      Automated Python tests
results/    Exported data and generated figures
```

## Requirements

- MATLAB and Simulink compatible with the supplied model and scripts
- Python 3.10 or newer
- Python packages listed in `requirements.txt`

## Python setup

From the repository root, create and activate a local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Simulink initialization and profile selection

The model is stored at:

```text
models/simulink/propellant_consuption_baseline.slx
```

The model initializes its parameters through the `InitFcn` callback.
The callback resolves the project root from the model file location
and runs:

```text
scripts/matlab/setup_simulation.m
```

The setup script defines the engine inputs, nominal mass-flow rates,
startup time, ramp duration, and simulation stop time.

Each flow branch contains:

- a Step source for instantaneous startup;
- a Ramp source followed by a Saturation block for gradual startup;
- a Switch that selects the flow supplied to the mass integrator.

A common Constant block, `Profile selector`, controls all three
branches:

| Selector value | Selected profile |
|---|---|
| `0` | Instantaneous Step startup |
| `1` | Linear startup ramp |

The Switch blocks use the condition `u2 >= 0.5`.
The saturated ramp is connected to the first input and the Step
signal to the third input.

The export scripts explicitly select the required profile through
`Simulink.SimulationInput`, so manual switching is not required.

The shared setup currently prints analytical ramp masses for both
runs. For a Step simulation, refer to the final
`STEP simulation results` section printed by `export_step_case.m`.

## Regenerating both cases

From the repository root in MATLAB, run:

```matlab
run("scripts/matlab/export_step_case.m")
run("scripts/matlab/export_ramp_case.m")
```

Both scripts use the same Simulink model and save their results
relative to the project root.

| Script | Profile | Export |
|---|---|---|
| `scripts/matlab/export_step_case.m` | Step | `results/matlab_simulink/step_export.mat` |
| `scripts/matlab/export_ramp_case.m` | Ramp | `results/matlab_simulink/ramp_export.mat` |

The Step export script checks:

- the final simulation time;
- the final total, LOX, and CH4 masses against analytical expectations;
- the propellant mass balance across the exported series.

These checks run before the Step export is saved.

The historical `baseline_export.mat` is retained for the original
baseline analysis. It is not overwritten by the Step export script.

## Analytical expectations

For instantaneous startup, with zero initial consumed mass and
constant nominal flow after activation:

```text
Final consumed mass = nominal flow × (stop time − start time)
```

For a linear startup ramp that finishes before the simulation stops:

```text
Final consumed mass =
nominal flow × (stop time − start time − ramp duration / 2)
```

The ramp expression accounts for the triangular area under the
flow curve during startup, followed by constant nominal flow.

Both expressions are applied separately to total propellant,
LOX, and CH4.

## Startup ramp analysis

The ramp profile starts at 1 s, increases linearly until 1.5 s,
and then remains at the nominal flow rate until the simulation
stops at 10 s.

To analyze the ramp export, run from the repository root:

```powershell
python scripts/python/analyze_simulink_ramp.py
```

The script reads:

```text
results/matlab_simulink/ramp_export.mat
```

It checks the propellant mass balance, verifies the final masses
against the analytical ramp result, and creates:

```text
results/figures/propellant_mass_ramp_python.png
```

## Step vs startup ramp comparison

After generating both exports, run:

```powershell
python scripts/python/compare_step_and_ramp.py
```

The comparison script reads:

```text
results/matlab_simulink/step_export.mat
results/matlab_simulink/ramp_export.mat
```

It checks the mass balance for both datasets, prints the final
consumed masses, and saves:

```text
results/figures/step_vs_ramp_mass_comparison.png
```

The script reads existing exports. It does not run MATLAB or
Simulink and does not regenerate the simulations.

### Reference results

| Consumed propellant | Step case | 0.5 s startup ramp |
|---|---:|---:|
| Total | 262.2127 kg | 254.9291 kg |
| LOX | 203.9432 kg | 198.2782 kg |
| CH4 | 58.2695 kg | 56.6509 kg |

The total consumption difference is approximately 7.2837 kg,
calculated from the unrounded exported values. Subtracting only
the displayed rounded totals may differ in the last decimal place.

Both cases activate at 1 s and stop at 10 s. The ramp reaches
nominal flow at 1.5 s, so it consumes less propellant during startup.

This difference reflects the different flow histories over the same
simulation interval; it does not demonstrate improved propellant
efficiency.

## Automated verification

From the repository root, with the Python environment activated, run:

```powershell
python -m pytest tests
```

To run only the ramp-export tests:

```powershell
python -m pytest tests/test_ramp_case.py -v
```

The suite includes configuration, performance, mass-balance, and
ramp-export checks.

The dedicated ramp-export tests check that:

- the MAT-file contains all required variables;
- time and mass series have consistent lengths;
- cumulative consumed masses do not decrease beyond the test tolerance;
- LOX mass plus CH4 mass matches total propellant mass;
- final total, LOX, and CH4 masses match analytical ramp expectations;
- the nominal LOX/CH4 flow ratio is 3.5;
- the ramp duration is 0.5 s.

The latest recorded full-suite run passed 22 tests.

Dedicated Python tests for `step_export.mat` are not yet included.
The Step export is currently checked by assertions in
`export_step_case.m`.

Python tests read the available exports; they do not run Simulink.
After changing the model or its parameters, regenerate the relevant
exports before running the tests.

These checks establish internal consistency. They do not constitute
experimental validation of the engine model.

## Legacy baseline analysis

The original baseline analysis uses the retained historical export:

```text
results/matlab_simulink/baseline_export.mat
```

To analyze that dataset, run:

```powershell
python scripts/python/analyze_simulink_baseline.py
```

The script checks the propellant mass balance and creates:

```text
results/figures/propellant_mass_balance_python.png
```

The current Step-vs-ramp comparison uses `step_export.mat`, not
this historical export.

### Historical Step baseline results

| Quantity | Value |
|---|---:|
| Final LOX mass consumed | 203.9432 kg |
| Final CH4 mass consumed | 58.2695 kg |
| Final total mass consumed | 262.2127 kg |
| Mass balance | Passed within numerical tolerance |

## Limitations

- Startup profiles are prescribed inputs, not predictions of engine
  startup dynamics.
- The model does not yet represent a detailed shutdown process.
- Mass-balance and analytical checks do not validate the engine-level
  assumptions against measurements.
- The comparison script checks each dataset's mass balance but does
  not yet automatically enforce matching nominal parameters and
  simulation intervals between the two cases.
- Some tests intentionally require the reference configuration,
  including O/F = 3.5 and a ramp duration of 0.5 s. Intentional changes
  to that configuration require corresponding test updates.

## Future work

- Add dedicated Python tests for the regenerated Step export.
- Check matching nominal parameters and simulation intervals before
  comparing the two cases.
- Separate shared parameter initialization from profile-specific
  analytical calculations and console output.
- Add a single entry point for regenerating and comparing both cases.
- Add independent references for validating engine-level assumptions.
- Extend the baseline toward engine-cycle and vehicle-level dynamics.
- Add CAD and structural-analysis cases only where they support a
  specific engineering question.