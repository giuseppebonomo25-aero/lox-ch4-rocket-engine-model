from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat


project_root = Path(__file__).resolve().parents[2]

mat_file = project_root / "results" / "matlab_simulink" / "ramp_export.mat"
figure_file = project_root / " results" / "figures" / "propellant_mass_ramp_python.png"

data = loadmat(mat_file)

time_s = data["t"].ravel()
total_kg = data["total_mass_kg"].ravel()
lox_kg = data["lox_mass_kg"].ravel()
ch4_kg = data["ch4_mass_kg"].ravel()

flow_total = float(data["total_flow_kg_s"].squeeze())
flow_lox = float(data["lox_flow_kg_s"].squeeze())
flow_ch4 = float(data["ch4_flow_kg_s"].squeeze())

start_time_s = float(data["start_time_s"].squeeze())
ramp_duration_s = float(data["ramp_duration_s"].squeeze())
stop_time_s = float(data["stop_time_s"].squeeze())

np.testing.assert_allclose(
    lox_kg + ch4_kg,
    total_kg,
    rtol=1e-8,
    atol=1e-6,
)

equivalent_full_flow_duration_s = (
    stop_time_s - start_time_s - ramp_duration_s / 2
)

expected_total_kg = flow_total * equivalent_full_flow_duration_s
expected_lox_kg = flow_lox * equivalent_full_flow_duration_s
expected_ch4_kg = flow_ch4 * equivalent_full_flow_duration_s

np.testing.assert_allclose(total_kg[-1], expected_total_kg, rtol=1e-8, atol=1e-6)
np.testing.assert_allclose(lox_kg[-1], expected_lox_kg, rtol=1e-8, atol=1e-6)
np.testing.assert_allclose(ch4_kg[-1], expected_ch4_kg, rtol=1e-8, atol=1e-6)

print(f"Final total mass: {total_kg[-1]:.4f} kg")
print(f"Final LOX mass:   {lox_kg[-1]:.4f} kg")
print(f"Final CH4 mass:   {ch4_kg[-1]:.4f} kg")
print(f"Ramp duration:    {ramp_duration_s:.4f} s")
print(f"O/F ratio:        {flow_lox / flow_ch4:.4f}")
print("Mass balance:     PASS")
print("Final mass check: PASS")

figure_file.parent.mkdir(parents=True, exist_ok=True)

plt.plot(time_s, ch4_kg, label="CH4 consumed")
plt.plot(time_s, lox_kg, label="LOX consumed")
plt.plot(time_s, total_kg, "--", label="Total")
plt.axvline(start_time_s, color="black", linestyle=":", label="Ramp start")
plt.axvline(
    start_time_s + ramp_duration_s,
    color="gray",
    linestyle=":",
    label="Nominal flow reached",
)
plt.xlabel("Time [s]")
plt.ylabel("Propellant mass [kg]")
plt.title(
    "Simulink ramp case — "
    f"{ramp_duration_s:g} s startup ramp from {start_time_s:g} s"
)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(figure_file, dpi=300)
plt.show()