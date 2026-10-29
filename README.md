# LOX/CH4 Propulsion System — Modelling and Verification

A personal engineering project developing from a prescribed-flow propellant-consumption baseline towards component-level modelling of a LOX/CH4 propulsion system for a launch vehicle first-stage application.

The project combines:

- MATLAB/Simulink for dynamic modelling and simulation;
- Simscape and Simscape Fluids for physical component networks;
- Python for preliminary sizing, fluid-property calculations, post-processing and verification;
- Git for version-controlled development.

The engineering focus is on explicit assumptions, component interfaces, conservation laws, analytical checks and traceable development decisions.

This is a work-in-progress numerical project. It is not a complete or experimentally validated rocket-engine design.

## Current development status

| Work package | Status |
|---|---|
| Prescribed Step and startup-ramp consumption baseline | Implemented |
| MATLAB simulation exports | Implemented |
| Python mass-consumption analysis and comparison | Implemented |
| Thrust and accumulated-impulse comparison | Implemented |
| Final impulse–consumed-mass consistency checks | Implemented |
| Isothermal-liquid restriction test bench using water | Implemented; initial operating-point check completed |
| Preliminary LOX equivalent-injector sizing | Implemented |
| Oxygen property calculations using CoolProp | Implemented |
| LOX restriction test bench | Initial operating point simulated |
| Updated LOX area verification | Pending confirmation |
| Coupled feed-system, chamber and nozzle model | Planned |

## Project scope

The repository currently contains two distinct modelling levels.

### 1. Prescribed-flow baseline

A Simulink model compares instantaneous Step and linear startup-ramp mass-flow inputs.

The model integrates total, LOX and CH4 mass flows to obtain cumulative propellant consumption. It also calculates thrust from total mass flow using constant specific impulse and integrates thrust to obtain accumulated impulse.

The startup profiles are prescribed inputs, not predictions of engine startup dynamics.

### 2. Component-level development

Separate Simscape test benches introduce pressure-driven flow through an equivalent hydraulic restriction.

The current component work covers:

- an initial restriction check using water properties;
- preliminary LOX flow-area sizing in Python;
- oxygen property evaluation at an assumed temperature of 90 K;
- a LOX restriction test between prescribed upstream and downstream pressures.

The component test benches are not yet coupled to a dynamic combustion chamber or nozzle.

The baseline is retained as a separate reference model.

## Baseline comparison figures

### Cumulative propellant consumption

![Comparison of cumulative propellant consumption for Step and startup-ramp profiles](results/figures/step_vs_ramp_mass_comparison.png)

### Thrust and accumulated impulse

![Comparison of thrust and accumulated impulse for Step and startup-ramp profiles](results/figures/step_vs_ramp_thrust_impulse.png)

## Repository layout

```text
models/
└── simulink/
    ├── propellant_consuption_baseline.slx
    ├── injector_component_test.slx
    └── lox_injector_test.slx

scripts/
├── matlab/
│   ├── setup_simulation.m
│   ├── export_step_case.m
│   └── export_ramp_case.m
└── python/
    ├── analyze_simulink_baseline.py
    ├── analyze_simulink_ramp.py
    ├── compare_step_and_ramp.py
    ├── compare_thrust_and_impulse.py
    ├── size_lox_injector.py
    └── lox_properties.py

src/        Reusable Python source code
tests/      Automated Python tests
results/    Exported simulation data and generated figures
```

The baseline model filename retains its original spelling.

## Software requirements

### Baseline modelling

- MATLAB
- Simulink

### Physical component test benches

- MATLAB
- Simulink
- Simscape
- Simscape Fluids

The component models were developed using MATLAB/Simulink R2026a.

### Python analysis

- Python 3.10 or newer, subject to compatibility with the installed package versions
- NumPy
- SciPy
- Matplotlib
- pytest
- CoolProp

Install the Python dependencies listed in `requirements.txt`.

The oxygen-property calculations reported here used CoolProp 8.0.0.

## Python setup

From the repository root, create and activate a local virtual environment.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The virtual environment is local and should not be committed.

Run the automated Python checks with:

```powershell
python -m pytest tests
```

The baseline analysis scripts and tests use existing simulation exports. They do not automatically launch MATLAB or Simulink.

The component-sizing and property scripts are separate calculations. They do not automatically configure the Simscape models.

## Baseline reference parameters

| Parameter | Value |
|---|---:|
| Nominal thrust input | 100000 N |
| Specific impulse input | 350 s |
| Standard gravity | 9.80665 m/s² |
| Oxidizer-to-fuel mass ratio | 3.50 |
| Simulation start time | 0 s |
| Simulation stop time | 10 s |
| Flow activation time | 1 s |
| Ramp duration | 0.5 s |
| Total nominal propellant flow | 29.134749 kg/s |
| LOX nominal flow | 22.660360 kg/s |
| CH4 nominal flow | 6.474389 kg/s |

The 100 kN thrust and 350 s specific impulse are baseline inputs. They are not yet demonstrated performance outputs of a coupled physical engine model.

The baseline does not specify an ambient-pressure condition for the 350 s specific impulse input. It should not automatically be interpreted as a sea-level performance value.

The nominal flow rates are calculated in:

```text
scripts/matlab/setup_simulation.m
```

using:

```text
Total flow = thrust / (specific impulse × standard gravity)

LOX flow = total flow × O/F / (1 + O/F)

CH4 flow = total flow / (1 + O/F)
```

## Baseline model initialization

The baseline model is stored at:

```text
models/simulink/propellant_consuption_baseline.slx
```

Its `InitFcn` callback resolves the project root from the model location and runs:

```text
scripts/matlab/setup_simulation.m
```

The setup script defines the nominal inputs, flow rates, activation time, ramp duration and simulation stop time.

Each mass-flow branch contains:

- a Step source;
- a Ramp source followed by a Saturation block;
- a Switch selecting the flow supplied to the mass integrator.

A common Constant block, `Profile selector`, controls all three branches.

| Selector value | Selected profile |
|---|---|
| `0` | Instantaneous Step |
| `1` | Linear startup ramp |

The Switch blocks use the condition `u2 >= 0.5`. The saturated ramp is connected to the first input and the Step signal to the third input.

The export scripts explicitly select the required profile through `Simulink.SimulationInput`.

The shared setup currently prints analytical ramp masses for both runs. For a Step simulation, refer to the profile-specific results printed by the Step export script.

## Regenerating the baseline exports

From the repository root in MATLAB, run:

```matlab
run("scripts/matlab/export_step_case.m")
run("scripts/matlab/export_ramp_case.m")
```

| Script | Profile | Export |
|---|---|---|
| `scripts/matlab/export_step_case.m` | Step | `results/matlab_simulink/step_export.mat` |
| `scripts/matlab/export_ramp_case.m` | Ramp | `results/matlab_simulink/ramp_export.mat` |

Both exports include:

- cumulative total, LOX and CH4 consumed masses;
- nominal mass-flow rates;
- thrust time and thrust series;
- impulse time and accumulated-impulse series;
- nominal thrust, specific impulse and standard gravity;
- profile timing parameters.

The ramp export also includes the ramp duration.

### MATLAB checks before saving

The Step export script checks:

- the final mass-signal simulation time;
- final total, LOX and CH4 consumed masses;
- propellant mass balance across the exported series;
- final accumulated impulse.

The ramp export script checks:

- positive ramp duration and completion before simulation end;
- final times of mass, thrust and impulse signals;
- final total, LOX and CH4 consumed masses;
- matching mass-array dimensions;
- propellant mass balance across the exported series;
- maximum thrust;
- final accumulated impulse.

The ramp checks use analytical expressions valid when the ramp finishes before the simulation ends.

The historical export:

```text
results/matlab_simulink/baseline_export.mat
```

is retained for legacy analysis and is not overwritten by the Step export script.

After changing the baseline model or its parameters, regenerate the relevant exports before running analysis or tests.

## Analytical baseline references

The mass references assume zero initial consumed mass and non-negative nominal flow.

Here:

- `t_activation` is the flow activation time;
- `t_stop` is the simulation stop time;
- `ramp_duration` is the duration of the linear rise to nominal flow.

### Instantaneous Step

```text
Consumed mass at time t =
nominal flow × max(t − t_activation, 0)
```

For a simulation ending after activation:

```text
Final consumed mass =
nominal flow × (t_stop − t_activation)
```

The dedicated Step tests compare the complete exported mass curves with the analytical reference.

### Linear startup ramp

For a ramp that finishes before simulation end:

```text
Final consumed mass =
nominal flow × (t_stop − t_activation − ramp_duration / 2)
```

This is applied separately to total propellant, LOX and CH4.

### Thrust and impulse

With constant specific impulse:

```text
Thrust = total mass flow × specific impulse × standard gravity
```

The final impulse references are:

```text
Step impulse =
nominal thrust × (t_stop − t_activation)

Ramp impulse =
nominal thrust × (t_stop − t_activation − ramp_duration / 2)
```

The final impulse and total consumed mass must also satisfy:

```text
Final impulse =
total consumed propellant × specific impulse × standard gravity
```

This last relation is an internal-consistency check, not an independent experimental validation.

## Baseline analysis commands

Run these commands from the repository root with the Python environment activated.

### Ramp consumed-mass analysis

```powershell
python scripts/python/analyze_simulink_ramp.py
```

Reads:

```text
results/matlab_simulink/ramp_export.mat
```

Checks mass balance and final analytical masses, then creates:

```text
results/figures/propellant_mass_ramp_python.png
```

### Step–ramp consumed-mass comparison

```powershell
python scripts/python/compare_step_and_ramp.py
```

Reads both profile exports and creates:

```text
results/figures/step_vs_ramp_mass_comparison.png
```

### Step–ramp thrust and impulse comparison

```powershell
python scripts/python/compare_thrust_and_impulse.py
```

The script:

- checks required exported variables;
- checks matching nominal thrust, specific impulse, gravity and timing parameters;
- checks thrust and impulse array lengths, finite values and time ordering;
- checks the expected time interval;
- compares final impulses with analytical references;
- checks final impulse–consumed-mass consistency;
- prints equivalent specific impulse;
- saves the thrust and impulse comparison figure.

Output:

```text
results/figures/step_vs_ramp_thrust_impulse.png
```

Each signal is plotted against its own exported time vector.

These scripts read existing exports. They do not regenerate simulations.

## Baseline reference results

| Quantity | Step | 0.5 s startup ramp |
|---|---:|---:|
| Total propellant consumed | 262.2127 kg | 254.9291 kg |
| LOX consumed | 203.9432 kg | 198.2782 kg |
| CH4 consumed | 58.2695 kg | 56.6509 kg |
| Maximum thrust | 100000 N | 100000 N |
| Final accumulated impulse | 900000 N·s | 875000 N·s |
| Equivalent specific impulse | 350 s | 350 s |

Both profiles activate at 1 s and stop at 10 s. The ramp reaches nominal flow at 1.5 s.

The total consumption difference is approximately 7.2837 kg, calculated using unrounded results.

The ramp reduces both consumed propellant and delivered impulse by approximately 2.777778% over the same simulation interval.

This does not demonstrate increased propellant efficiency or equivalent mission performance. The prescribed histories deliver different total impulses.

## Automated baseline verification

Run the suite with:

```powershell
python -m pytest tests
```

Run the dedicated profile tests with:

```powershell
python -m pytest tests/test_step_case.py -v
python -m pytest tests/test_ramp_case.py -v
```

### Step-export tests

The dedicated Step tests cover:

- exported profile label;
- finite, non-decreasing times and expected simulation interval;
- consistent time-series lengths;
- finite masses and nominal flows;
- non-negative and non-decreasing consumed masses within tolerance;
- mass balance across the exported series;
- complete mass-curve agreement with the analytical Step reference;
- nominal mass-flow balance;
- O/F ratio of 3.5.

The previously recorded dedicated Step-test run passed all 11 tests. This is a historical test result, not a claim that tests have been rerun after every subsequent change.

### Ramp-export tests

The dedicated ramp tests cover:

- required exported variables;
- consistent time-series lengths;
- non-decreasing consumed masses within tolerance;
- mass balance;
- analytical final masses;
- nominal O/F ratio of 3.5;
- ramp duration of 0.5 s.

### Verification boundaries

The thrust–impulse and impulse–mass checks described above are implemented in the comparison script and MATLAB exports. They should not be assumed to be additional pytest tests unless explicitly added to the suite.

The injector sizing and component test benches are not yet covered by the baseline pytest suite.

Passing tests on saved exports does not establish that those exports were generated from the latest model revision.

## Component test bench: initial water check

Model:

```text
models/simulink/injector_component_test.slx
```

The network contains:

- upstream reservoir;
- constant-area `Orifice (IL)`;
- `Flow Rate Sensor (IL)`;
- downstream reservoir;
- `Isothermal Liquid Properties (IL)`;
- `Solver Configuration`;
- physical-signal conversion and Simulink visualisation.

### Initial operating point

| Parameter | Value |
|---|---:|
| Upstream absolute pressure | 1 MPa |
| Downstream absolute pressure | 0.5 MPa |
| Orifice area | 1e-5 m² |
| Discharge coefficient | 0.64 |
| Port cross-sectional area | `inf` |
| Pressure recovery | Disabled |
| Entrained-air fraction | 0 |
| Reference liquid density | 998.21 kg/m³ |

The simplified turbulent-flow reference is:

```text
Mass flow = Cd × area × sqrt(2 × density × pressure drop)
```

Recorded results:

| Method | Mass flow |
|---|---:|
| Simplified Python reference | 0.202205 kg/s |
| Simscape display | Approximately 0.2022 kg/s |

The results agree at the displayed precision.

This is an initial operating-point check, not a complete characterisation or experimental validation of the component.

## Preliminary LOX equivalent-injector sizing

Sizing script:

```text
scripts/python/size_lox_injector.py
```

Run:

```powershell
python scripts/python/size_lox_injector.py
```

The script calculates the equivalent flow area needed to deliver the baseline LOX flow at an assumed pressure drop and discharge coefficient.

```text
Equivalent area =
target mass flow / (Cd × sqrt(2 × density × pressure drop))
```

### Preliminary assumptions

| Parameter | Value |
|---|---:|
| Target LOX mass flow | 22.660360 kg/s |
| Assumed temperature | 90 K |
| Downstream absolute pressure | 5 MPa |
| Upstream absolute pressure | 6 MPa |
| Injector pressure drop | 1 MPa |
| Pressure-drop / downstream-pressure ratio | 0.20 |
| Assumed discharge coefficient | 0.64 |

The pressures and discharge coefficient are preliminary assumptions, not optimised design values.

The upstream pressure is the pressure immediately before the injector. It is not automatically a tank-pressure requirement.

The equivalent area represents the aggregate hydraulic passage of the LOX branch. It does not specify the number, diameter or arrangement of individual injection elements.

The reported equivalent circular diameter is only the diameter of a circle with the same total area.

## LOX thermophysical properties

Property script:

```text
scripts/python/lox_properties.py
```

Run:

```powershell
python scripts/python/lox_properties.py
```

The script uses CoolProp to evaluate oxygen properties at 90 K and three pressures.

### Recorded property results

| Property | Reference | Injector outlet | Injector inlet |
|---|---:|---:|---:|
| Absolute pressure | 1.01325 bar | 50 bar | 60 bar |
| Density | 1142.108492 kg/m³ | 1152.617849 kg/m³ | 1154.672179 kg/m³ |
| Dynamic viscosity | 1.95647258e-4 Pa·s | 2.05326366e-4 Pa·s | 2.07288990e-4 Pa·s |
| Kinematic viscosity | 1.71303567e-7 m²/s | 1.78139152e-7 m²/s | 1.79521940e-7 m²/s |
| Isothermal bulk modulus | 5.12866481e8 Pa | 5.57136372e8 Pa | 5.66013155e8 Pa |

These are outputs of the selected property model, not experimental measurements performed in this project.

### Simscape approximation

The LOX test bench uses reference properties at atmospheric pressure, zero entrained air and a constant isothermal bulk modulus.

For this approximation:

```text
density(p) =
reference density × exp((p − reference pressure) / bulk modulus)
```

The Python sizing calculation uses the mean of the inlet and outlet densities obtained with this same approximation.

This is not identical to evaluating the full CoolProp equation of state at every simulation point.

The assumed temperature is represented through the selected isothermal properties. No energy balance is solved in this component test bench.

## LOX component test bench

Model:

```text
models/simulink/lox_injector_test.slx
```

### Sizing iterations

| Stage | Density used for sizing | Equivalent area | Result |
|---|---:|---:|---|
| Initial sizing | Constant 1141 kg/m³ | 741.189 mm² | Simscape displayed approximately 22.79 kg/s |
| Updated sizing | Mean operating density of approximately 1154.2 kg/m³ from the constant-bulk-modulus approximation | 736.940 mm² | Simulation confirmation pending |

The initial result exceeded the target by approximately 0.57%, based on the rounded displayed flow.

The area was updated to make the sizing assumptions more consistent with the Simscape fluid configuration. The discharge coefficient was not adjusted to force agreement.

### Updated area

```text
Orifice area = 7.36940222e-4 m²
```

Equivalent circular diameter:

```text
30.632 mm
```

Confirmation of the simulated flow with this area remains a pending verification item.

## Running the component models

1. Open the required model from `models/simulink/`.
2. Review its reservoir pressures, orifice parameters and fluid properties.
3. Confirm that the PS–Simulink Converter output unit is `kg/s`.
4. Run the simulation.
5. Read the mass flow from the Scope or Display.
6. Compare the result with a reference using consistent assumptions.

The current component tests use a simulation stop time of 1 s.

The reservoir pressures are constant boundary conditions. These test benches do not represent a commanded ignition sequence.

Parameters are currently transferred manually from Python calculations to Simscape block dialogs. There is no automated Python-to-Simulink configuration workflow yet.

## Legacy baseline analysis

The original analysis uses:

```text
results/matlab_simulink/baseline_export.mat
```

Run:

```powershell
python scripts/python/analyze_simulink_baseline.py
```

It checks mass balance and creates:

```text
results/figures/propellant_mass_balance_python.png
```

The current Step–ramp comparisons use `step_export.mat` and `ramp_export.mat`, not the historical export.

## Engineering assumptions and limitations

### Baseline

- Startup profiles are prescribed.
- Specific impulse is constant.
- Thrust is derived from prescribed total flow.
- No detailed startup or shutdown physics is represented.
- Equal simulation duration does not imply equal delivered impulse.
- The mass-comparison script does not yet enforce all cross-case parameter checks; the separate thrust–impulse comparison checks its required nominal parameters and timing.
- Some tests intentionally depend on the reference configuration.
- Saved exports are not automatically regenerated by Python.

### Component models

- The injector is an equivalent hydraulic restriction.
- Reservoirs prescribe boundary pressures and do not model finite propellant inventories.
- No coupled tank, pump or feed-system architecture has been selected.
- LOX temperature is assumed constant at 90 K.
- Constant bulk modulus is a limited property approximation.
- The discharge coefficient is assumed rather than experimentally identified.
- Individual injector-element geometry is not represented.
- Atomisation, mixing, combustion, cavitation and heat transfer are not modelled.
- The downstream reservoir is not a dynamic combustion chamber.
- No nozzle is coupled to the component test bench.
- The 100 kN baseline target has not been demonstrated by a coupled physical engine model.

### Verification and validation

The available checks establish selected numerical and analytical consistency properties.

They do not constitute experimental validation of an injector or complete propulsion system.

## Development workflow

For baseline changes:

1. Modify the model or parameters.
2. Regenerate the relevant MATLAB exports.
3. Run the Python test suite.
4. Regenerate affected figures.
5. Review results and document limitations.
6. Commit the related code, model and documentation changes.

For component changes:

1. Define the physical question and boundary conditions.
2. Document equations, parameters and assumptions.
3. Calculate a preliminary reference or sizing result in Python.
4. Configure and run the component model.
5. Compare results using consistent assumptions.
6. Record verification status before integration with other components.

## Roadmap

### Immediate next steps

- Confirm the LOX operating-point flow with the updated equivalent area.
- Record component results with sufficient numerical precision.
- Add reproducible parameter initialization and result export for the component test benches.
- Study sensitivity to pressure drop and discharge coefficient with fixed geometry.
- Extend equivalent-injector modelling to the CH4 branch.

### Physical-system development

- Define system requirements and an explicit nominal operating point.
- Select and justify the feed-system modelling scope.
- Introduce distinct valve and feed-line components.
- Couple LOX and CH4 branches and monitor mixture ratio.
- Introduce a chamber model with mass and energy balances.
- Introduce a nozzle model and ambient-pressure effects.
- Analyse integrated transients and off-nominal conditions.

### Verification and reproducibility

- Add automated component-level checks.
- Separate shared initialization from profile-specific reference calculations.
- Provide a single entry point for baseline regeneration and analysis.
- Add continuous integration for Python checks using committed exports.
- Extend reference-profile tests to additional activation times and ramp durations.
- Document parameter sources, interfaces and verification evidence.