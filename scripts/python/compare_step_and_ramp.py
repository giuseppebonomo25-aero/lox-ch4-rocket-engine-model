from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat


project_root = Path(__file__).resolve().parents[2]

results_dir = project_root / "results" / "matlab_simulink"
figures_dir = project_root / "results" / "figures"

step_file = results_dir / "step_export.mat"
ramp_file = results_dir / "ramp_export.mat"
figure_file = figures_dir / "step_vs_ramp_mass_comparison.png"


def load_export(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing export file: {file_path}. "
            "Run the corresponding MATLAB export script first."
        )

    data = loadmat(file_path, squeeze_me=True, struct_as_record=False)

    required = [
        "t",
        "total_mass_kg",
        "lox_mass_kg",
        "ch4_mass_kg",
        "total_flow_kg_s",
        "lox_flow_kg_s",
        "ch4_flow_kg_s",
        "start_time_s",
    ]

    for variable in required:
        if variable not in data:
            raise KeyError(f"Missing variable '{variable}' in {file_path.name}")

    return {
        "time_s": np.asarray(data["t"]).ravel(),
        "total_kg": np.asarray(data["total_mass_kg"]).ravel(),
        "lox_kg": np.asarray(data["lox_mass_kg"]).ravel(),
        "ch4_kg": np.asarray(data["ch4_mass_kg"]).ravel(),
        "total_flow": float(data["total_flow_kg_s"]),
        "lox_flow": float(data["lox_flow_kg_s"]),
        "ch4_flow": float(data["ch4_flow_kg_s"]),
        "start_time": float(data["start_time_s"]),
    }


step = load_export(step_file)
ramp = load_export(ramp_file)

for name, case in (("Step", step), ("Ramp", ramp)):
    np.testing.assert_allclose(
        case["lox_kg"] + case["ch4_kg"],
        case["total_kg"],
        rtol=1e-8,
        atol=1e-6,
        err_msg=f"Mass balance failed for the {name} case",
    )

step_final_total = step["total_kg"][-1]
ramp_final_total = ramp["total_kg"][-1]
mass_difference = step_final_total - ramp_final_total

step_final_lox = step["lox_kg"][-1]
ramp_final_lox = ramp["lox_kg"][-1]

step_final_ch4 = step["ch4_kg"][-1]
ramp_final_ch4 = ramp["ch4_kg"][-1]

print("Propellant consumption comparison")
print("--------------------------------")
print(f"Step final total mass:  {step_final_total:.4f} kg")
print(f"Ramp final total mass:  {ramp_final_total:.4f} kg")
print(f"Total mass difference:  {mass_difference:.4f} kg")
print()
print(f"Step final LOX mass:    {step_final_lox:.4f} kg")
print(f"Ramp final LOX mass:    {ramp_final_lox:.4f} kg")
print()
print(f"Step final CH4 mass:    {step_final_ch4:.4f} kg")
print(f"Ramp final CH4 mass:    {ramp_final_ch4:.4f} kg")
print()
print(f"Step O/F ratio:         {step['lox_flow'] / step['ch4_flow']:.4f}")
print(f"Ramp O/F ratio:         {ramp['lox_flow'] / ramp['ch4_flow']:.4f}")

figures_dir.mkdir(parents=True, exist_ok=True)

fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

axes[0].plot(step["time_s"], step["total_kg"], label="Step case")
axes[0].plot(ramp["time_s"], ramp["total_kg"], label="Ramp case")
axes[0].set_ylabel("Total mass [kg]")
axes[0].set_title("Propellant consumption: Step vs 0.5 s startup ramp")
axes[0].legend()
axes[0].grid(True)

axes[1].plot(step["time_s"], step["lox_kg"], label="Step case")
axes[1].plot(ramp["time_s"], ramp["lox_kg"], label="Ramp case")
axes[1].set_ylabel("LOX mass [kg]")
axes[1].legend()
axes[1].grid(True)

axes[2].plot(step["time_s"], step["ch4_kg"], label="Step case")
axes[2].plot(ramp["time_s"], ramp["ch4_kg"], label="Ramp case")
axes[2].set_ylabel("CH4 mass [kg]")
axes[2].set_xlabel("Time [s]")
axes[2].legend()
axes[2].grid(True)

fig.tight_layout()
fig.savefig(figure_file, dpi=300)
plt.show()

print(f"Saved comparison figure: {figure_file}")