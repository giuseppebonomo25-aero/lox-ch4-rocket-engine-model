# LOX/CH4 Propellant Consumption — Modelling and Verification

A personal engineering project combining MATLAB/Simulink modelling, automated simulation-data exports, and Python analysis and verification of LOX/CH4 propellant consumption.

The workflow compares instantaneous-step and linear-ramp startup inputs using mass-balance checks and analytical reference solutions.

## Project highlights

- A single Simulink model with selectable Step and startup-ramp mass-flow profiles.
- MATLAB scripts for reproducible simulation and data exports.
- Python post-processing for mass-consumption analysis and profile comparison.
- Automated checks using pytest, including 11 dedicated Step-case tests.
- Version-controlled simulation exports and comparison figures.

![Comparison of cumulative propellant consumption for Step and startup-ramp profiles](results/figures/step_vs_ramp_mass_comparison.png)

## Scope

The model supports two prescribed startup profiles:

- an instantaneous Step;
- a linear ramp followed by constant nominal flow.

Separate LOX, CH4, and total-flow branches feed Simulink integrators that compute the cumulative propellant mass consumed during the simulation.

The plotted masses represent cumulative propellant consumption, not propellant remaining in the tanks.

This is an internal-consistency and analytical-verification baseline. It does not represent a complete rocket-engine model or a detailed physical startup or shutdown process, and it has not been validated against experimental data.

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

Nominal mass-flow rates are derived from the thrust and specific-impulse inputs in:

```text
scripts/matlab/setup_simulation.m
```

## Repository layout

```text
models/     Simulink model files
scripts/    MATLAB and Python scripts
src/        Reusable Python source code
tests/      Automated Python tests
results/    Exported data and generated figures
```

## Requirements

- MATLAB and Simulink compatible with the supplied model and scripts.
- Python 3.10 or newer.
- Python packages listed in `requirements.txt`.

## Python setup

From the repository root, create and activate a local virtual environment.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the automated Python checks:

```powershell
python -m pytest tests
```

Python analysis and tests use existing simulation exports. MATLAB and Simulink are required to regenerate those exports, but are not invoked by the Python tests.

## Simulink initialization and profile selection

The model is stored at:

```text
models/simulink/propellant_consuption_baseline.slx
```

The model initializes its parameters through the `InitFcn` callback. The callback resolves the project root from the model file location and runs:

```text
scripts/matlab/setup_simulation.m
```

The setup script defines the engine inputs, nominal mass-flow rates, flow activation time, ramp duration, and simulation stop time.

Each flow branch contains:

- a Step source for instantaneous startup;
- a Ramp source followed by a Saturation block for gradual startup;
- a Switch selecting the flow supplied to the mass integrator.

A common Constant block, `Profile selector`, controls all three branches:

| Selector value | Selected profile |
|---|---|
| `0` | Instantaneous Step startup |
| `1` | Linear startup ramp |

The Switch blocks use the condition `u2 >= 0.5`. The saturated ramp is connected to the first input and the Step signal to the third input.

The export scripts explicitly select the required profile through `Simulink.SimulationInput`, so manual switching is not required.

The shared setup currently prints analytical ramp masses for both runs. For a Step simulation, refer to the final `STEP simulation results` section printed by `export_step_case.m`.

## Regenerating the simulation exports

From the repository root in MATLAB, run:

```matlab
run("scripts/matlab/export_step_case.m")
run("scripts/matlab/export_ramp_case.m")
```

Both scripts use the same Simulink model and save their results relative to the project root.

| Script | Profile | Export |
|---|---|---|
| `scripts/matlab/export_step_case.m` | Step | `results/matlab_simulink/step_export.mat` |
| `scripts/matlab/export_ramp_case.m` | Ramp | `results/matlab_simulink/ramp_export.mat` |

Before saving, the Step export script checks:

- the final simulation time;
- the final total, LOX, and CH4 consumed masses against analytical expectations;
- propellant mass balance across the exported series.

The Step profile label is exported as a MATLAB character array (`'step'`) for compatibility with the Python/SciPy loading workflow.

The historical `baseline_export.mat` is retained for the original baseline analysis. It is not overwritten by the Step export script.

After changing the model or its parameters, regenerate the relevant exports before running Python analysis or tests.

## Analytical expectations

The reference solutions assume zero initial consumed mass and a non-negative nominal mass-flow rate.

Here:

- `t_activation` is the flow activation time, not the simulation start time;
- `t_stop` is the simulation stop time;
- `ramp_duration` is the time required to reach nominal flow.

### Instantaneous Step

For constant nominal flow after activation:

```text
Consumed mass at time t =
nominal flow × max(t − t_activation, 0)
```

For a simulation ending after activation:

```text
Final consumed mass =
nominal flow × (t_stop − t_activation)
```

The dedicated Step tests compare the complete exported mass curves with this analytical solution, not only their final values.

### Linear startup ramp

For a linear ramp that reaches nominal flow before the simulation stops:

```text
Final consumed mass =
nominal flow × (t_stop − t_activation − ramp_duration / 2)
```

This expression accounts for the triangular area under the flow curve during startup, followed by constant nominal flow.

The expressions are applied separately to total propellant, LOX, and CH4.

## Startup-ramp analysis

In the reference configuration, the ramp starts at 1 s, reaches nominal flow at 1.5 s, and remains at nominal flow until the simulation stops at 10 s.

From the repository root, run:

```powershell
python scripts/python/analyze_simulink_ramp.py
```

The script reads:

```text
results/matlab_simulink/ramp_export.mat
```

It checks propellant mass balance, verifies the final masses against the analytical ramp result, and creates:

```text
results/figures/propellant_mass_ramp_python.png
```

## Step vs startup-ramp comparison

After generating both exports, run:

```powershell
python scripts/python/compare_step_and_ramp.py
```

The comparison script reads:

```text
results/matlab_simulink/step_export.mat
results/matlab_simulink/ramp_export.mat
```

It checks mass balance for both datasets, prints the final consumed masses, and saves:

```text
results/figures/step_vs_ramp_mass_comparison.png
```

The script reads existing exports. It does not run MATLAB or Simulink and does not regenerate the simulations.

### Reference results

| Consumed propellant | Step case | 0.5 s startup ramp |
|---|---:|---:|
| Total | 262.2127 kg | 254.9291 kg |
| LOX | 203.9432 kg | 198.2782 kg |
| CH4 | 58.2695 kg | 56.6509 kg |

The total consumption difference is approximately 7.2837 kg, calculated from the unrounded exported values. Subtracting only the displayed rounded totals may differ in the last decimal place.

Both cases activate at 1 s and stop at 10 s. The ramp reaches nominal flow at 1.5 s, so it consumes less propellant during startup.

This difference reflects the different prescribed flow histories over the same simulation interval. It does not demonstrate improved propellant efficiency, equal delivered impulse, or equivalent mission performance.

## Automated verification

From the repository root, with the Python environment activated, run:

```powershell
python -m pytest tests
```

To run only the Step-export tests:

```powershell
python -m pytest tests/test_step_case.py -v
```

To run only the ramp-export tests:

```powershell
python -m pytest tests/test_ramp_case.py -v
```

The suite includes configuration, performance, mass-balance, Step-export, and ramp-export checks.

### Step-export checks

The dedicated Step tests cover:

- the exported profile label;
- finite, non-decreasing simulation times and the expected simulation interval;
- consistent time-series lengths;
- finite mass and nominal-flow values;
- non-negative and non-decreasing cumulative consumed masses within tolerance;
- propellant mass balance across the exported series;
- agreement of the complete total, LOX, and CH4 consumed-mass curves with the analytical Step solution;
- nominal mass-flow balance;
- an oxidizer-to-fuel mass ratio of 3.5.

The latest recorded dedicated Step-test run passed all 11 tests.

The Step export also includes MATLAB assertions checking the final simulation time, final consumed masses, and mass balance before saving.

### Ramp-export checks

The dedicated ramp tests cover:

- the presence of all required exported variables;
- consistent time-series lengths;
- non-decreasing cumulative consumed masses within tolerance;
- agreement between LOX plus CH4 mass and total propellant mass;
- final total, LOX, and CH4 consumed masses against analytical ramp expectations;
- a nominal oxidizer-to-fuel mass ratio of 3.5;
- a ramp duration of 0.5 s.

### Verification scope

Python tests read existing exports; they do not run MATLAB or Simulink.

Passing these tests verifies the available datasets against the implemented checks. It does not independently establish that an export was generated from the latest model revision.

After modifying the model or its parameters:

1. Regenerate the relevant MATLAB exports.
2. Run the Python test suite.
3. Regenerate the affected analysis figures.

These checks establish internal consistency and agreement with analytical reference solutions. They do not constitute experimental validation of a complete engine model.

## Legacy baseline analysis

The original baseline analysis uses the retained historical export:

```text
results/matlab_simulink/baseline_export.mat
```

To analyse that dataset, run:

```powershell
python scripts/python/analyze_simulink_baseline.py
```

The script checks propellant mass balance and creates:

```text
results/figures/propellant_mass_balance_python.png
```

The current Step-vs-ramp comparison uses `step_export.mat`, not this historical export.

### Historical Step baseline results

| Quantity | Value |
|---|---:|
| Final LOX mass consumed | 203.9432 kg |
| Final CH4 mass consumed | 58.2695 kg |
| Final total mass consumed | 262.2127 kg |
| Mass balance | Passed within numerical tolerance |

## Limitations

- Startup profiles are prescribed inputs, not predictions of engine startup dynamics.
- The model does not represent a detailed shutdown process.
- Mass-balance and analytical checks do not validate engine-level assumptions against experimental measurements.
- Comparing consumption over an equal time interval does not establish equal thrust histories, delivered impulse, or mission performance.
- The comparison script checks each dataset's mass balance but does not yet automatically enforce matching nominal parameters and simulation intervals between the two cases.
- Some tests intentionally require the reference configuration, including an oxidizer-to-fuel mass ratio of 3.5 and a ramp duration of 0.5 s. Intentional changes to those reference values require corresponding test updates.
- Python checks use saved exports and do not automatically regenerate them after model changes.

## Future work

- Automatically check matching nominal parameters and simulation intervals before comparing the two exports.
- Separate shared parameter initialization from profile-specific analytical calculations and console output.
- Add a single entry point for regenerating and comparing both cases.
- Add continuous integration for Python checks using the committed exports.
- Extend automated verification to additional flow activation times and ramp durations.