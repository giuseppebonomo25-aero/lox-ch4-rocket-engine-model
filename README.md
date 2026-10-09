# LOX/CH₄ Rocket Engine Model (Preliminary)

Preliminary Python model for LOX/CH₄ rocket engine propellant mass-flow analysis.

## Features

- Estimate total propellant mass flow from thrust and specific impulse.
- Split mass flow between LOX and CH₄ as a function of oxidizer-to-fuel ratio.
- Validate inputs and check mass-flow conservation.
- Compute total propellant mass for a given burn time.
- Generate parametric plots and CSV results.
- Automated tests with pytest.

## Requirements

- Python 3.10+
- NumPy
- Matplotlib
- pytest

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python -m pytest
python -m src.plot_mass_flow
```

Results are saved in the `results/` folder.

## Physics

Total mass flow is estimated from:

\[
\dot{m}_{tot} = \frac{F}{I_{sp} g_0}
\]

where \(F\) is thrust, \(I_{sp}\) is specific impulse, and \(g_0\) is standard gravity.

LOX/CH₄ split depends on the mixture ratio \(O/F\):

\[
\dot{m}_{CH_4} = \frac{\dot{m}_{tot}}{1 + O/F}, \quad
\dot{m}_{LOX} = \dot{m}_{tot} - \dot{m}_{CH_4}
\]

Total propellant mass for a burn time \(t_b\):

\[
m_{prop} = \dot{m}_{tot} t_b
\]

## Limitations

- Specific impulse is an input, not computed from combustion or nozzle physics.
- No chamber pressure, nozzle, or cooling model.
- Intended as a preliminary performance model, not a complete engine design.

## License

MIT