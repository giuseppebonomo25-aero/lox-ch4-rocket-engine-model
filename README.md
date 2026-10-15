# LOX/CH4 Propellant Consumption Baseline

This repository contains a small, reproducible baseline workflow for a LOX/CH4
rocket-engine propellant-consumption model. It combines a Simulink model,
MATLAB post-processing/export, and Python analysis and automated checks.

## Scope

The current baseline models constant LOX, CH4, and total propellant mass-flow
rates that start at a configurable time. The Simulink integrators compute the
cumulative propellant mass consumed during the simulation.

This is an internal consistency baseline. It does **not** yet validate the
model against experimental data or represent a detailed physical engine
start-up/shutdown process.

## Baseline case

- Simulation duration: 10 s
- Flow activation time: 1 s
- Total propellant flow: 29.1347 kg/s
- LOX flow: 22.6604 kg/s
- CH4 flow: 6.4744 kg/s
- Oxidizer-to-fuel ratio: 3.50
- Final total mass consumed: 262.2127 kg

## Repository layout

```text
models/                 Simulink model files
scripts/                MATLAB and Python scripts
src/                    Reusable Python source code
tests/                  Automated Python tests
results/                Exported data and generated figures
```

## Requirements

- MATLAB/Simulink installation used to run and export the baseline model
- Python 3.10 or newer
- Python packages listed in `requirements.txt`

## Python setup

Create and activate a local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Simulink initialization

The baseline Simulink model initializes its parameters through the `InitFcn`
model callback. Before the model is updated or simulated, the callback runs:

```matlab
run("scripts/matlab/setup_simulation.m")
```

The setup script defines the engine inputs and derived variables used by the
three Step blocks:

- `start_time_s`
- `total_flow_kg_s`
- `lox_flow_kg_s`
- `ch4_flow_kg_s`

This keeps the MATLAB configuration and Simulink baseline model consistent.

## Startup ramp case

The repository includes a 0.5 s startup ramp case in addition to the
instantaneous step case.

The propellant flow starts at 1 s, increases linearly until 1.5 s, and then
remains at the nominal flow rate until the 10 s simulation stop time.

| Case | Flow profile | Total propellant consumed |
|---|---|---:|
| Step | Instantaneous nominal flow at 1 s | 262.2127 kg |
| Startup ramp | Linear ramp from 1 s to 1.5 s | 254.9291 kg |

The MATLAB export script writes `results/matlab_simulink/ramp_export.mat`.
The Python script `scripts/python/analyze_simulink_ramp.py` reads this file,
checks the propellant mass balance, verifies the final mass against the
analytical ramp result, and creates
`results/figures/propellant_mass_ramp_python.png`.

## Automated verification

The startup ramp export is verified automatically with pytest.

After regenerating the MATLAB export with:

```matlab
run("scripts/matlab/export_ramp_case.m")
```

run the Python test suite from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
pytest
```

The ramp-case tests check that:

- the exported MAT-file contains all required variables;
- the time, LOX, CH4, and total-mass series have consistent lengths;
- the consumed propellant masses increase monotonically;
- LOX mass plus CH4 mass equals total propellant mass;
- the final LOX, CH4, and total masses match the analytical ramp result;
- the LOX/CH4 mixture ratio is 3.5;
- the startup ramp duration is 0.5 s.

## Step vs startup ramp comparison

Run the comparison script from the repository root:

```powershell
python scripts/python/compare_step_and_ramp.py
```

The script reads the historical Step export, `baseline_export.mat`,
and the startup ramp export, `ramp_export.mat`, from
`results/matlab_simulink/`.

It checks the mass balance for both datasets, prints the final consumed
propellant masses, and saves a comparison figure to:

```text
results/figures/step_vs_ramp_mass_comparison.png
```

| Consumed propellant | Step case | 0.5 s startup ramp |
|---|---:|---:|
| Total | 262.2127 kg | 254.9291 kg |
| LOX | 203.9432 kg | 198.2782 kg |
| CH4 | 58.2695 kg | 56.6509 kg |

The total consumption difference is approximately 7.2837 kg,
calculated from the unrounded exported values.

Both cases start at 1 s and end at 10 s. The ramp case reaches the
nominal flow rate at 1.5 s. Its lower consumption therefore reflects
the reduced flow during startup, not improved propellant efficiency.

The comparison script reads existing exports; it does not regenerate
the MATLAB/Simulink simulations.

## Run the analysis

After running the Simulink baseline and exporting the results to
`results/matlab_simulink/baseline_export.mat`, run:

```powershell
python .\scripts\python\analyze_simulink_baseline.py
```

The script reads the exported MATLAB data, checks the propellant mass balance,
and creates:

```text
results/figures/propellant_mass_balance_python.png
```

## Run the tests

```powershell
python -m pytest .\tests
```

The mass-balance test verifies that, across the exported time series,

```text
LOX mass + CH4 mass = total propellant mass
```

within a numerical tolerance.

## Results

The baseline result is:

| Quantity | Value |
|---|---:|
| Final LOX mass | 203.9432 kg |
| Final CH4 mass | 58.2695 kg |
| Final total mass | 262.2127 kg |
| Mass-balance error | 0.000000 kg |

## Future work

- Add a documented simulation workflow that runs the model from MATLAB.
- Add independent references for validating engine-level assumptions.
- Extend the baseline toward engine-cycle and vehicle-level dynamics.
- Add CAD and structural-analysis cases only where they support a specific
  engineering question.