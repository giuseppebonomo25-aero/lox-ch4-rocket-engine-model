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