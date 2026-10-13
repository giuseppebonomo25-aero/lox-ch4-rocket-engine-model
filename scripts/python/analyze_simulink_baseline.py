from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat

project_root = Path(__file__).resolve().parents[2]
mat_file = project_root / "results" / "matlab_simulink" / "baseline_export.mat"
figure_file = project_root / "results" / "figures" / "propellant_mass_balance_python.png"


data = loadmat(mat_file)

time_s = data["t"].ravel()
total_kg = data["total_mass_kg"].ravel()
lox_kg = data["lox_mass_kg"].ravel()
ch4_kg = data["ch4_mass_kg"].ravel()

flow_total = float(data["total_flow_kg_s"].squeeze())
flow_lox = float(data["lox_flow_kg_s"].squeeze())
flow_ch4 = float(data["ch4_flow_kg_s"].squeeze())
start_time = float(data["start_time_s"].squeeze())

np.testing.assert_allclose(
    lox_kg + ch4_kg, total_kg, rtol=1e-8, atol=1e-6
)

print(f"Final total mass: {total_kg[-1]:.4f} kg")
print(f"Final LOX mass:   {lox_kg[-1]:.4f} kg")
print(f"Final CH4 mass:   {ch4_kg[-1]:.4f} kg")
print(f"O/F ratio:        {flow_lox / flow_ch4:.4f}")
print(f"Mass balance:     PASS")

figure_file.parent.mkdir(parents=True, exist_ok=True)

plt.plot(time_s, ch4_kg, label="CH4 consumed")
plt.plot(time_s, lox_kg, label="LOX consumed")
plt.plot(time_s, total_kg, "--", label="Total")
plt.xlabel("Time [s]")
plt.ylabel("Propellant mass [kg]")
plt.title(f"Simulink baseline — flow starts at {start_time:g} s")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(figure_file, dpi=300)
plt.show()