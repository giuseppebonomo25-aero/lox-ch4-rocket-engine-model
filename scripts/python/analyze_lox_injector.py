from pathlib import Path
import csv

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT / "results" / "components" / "lox_injector_export.mat"
)

FIGURE_FILE = (
    PROJECT_ROOT / "results" / "figures" / "lox_injector_mass_flow.png"
)

SUMMARY_FILE = (
    PROJECT_ROOT / "results" / "components" / "lox_injector_summary.csv"
)

TARGET_FLOW = 22.660360 # Roundend nominal target, kg/s

EXPECTED_START = 0.0
EXPECTED_STOP = 1.0
TIME_ATOL = 1e-9

FLOW_RTOL = 1e-4
FLOW_ATOL = 1e-6


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    if not INPUT_FILE.is_file():
        raise FileNotFoundError(
            f"Simulation export not fount:\n{INPUT_FILE}\n"
            "Run the MATLAB simulation and export first"
        )

    data = loadmat(INPUT_FILE, squeeze_me=True)

    required = (
        "t_lox",
        "mdot_lox_values",
        "model_name",
        "flow_unit",
        "time_unit",
    )

    missing = [name for name in required if name not in data]
    require(not missing, f"Missing exported variables: {missing}")

    require(
        str(data["model_name"]) == "lox_injector_test",
        "Unexpected model label."
    )

    require(str(data["flow_unit"]) == "kg/s", "Unexpected flow unit.")
    require(str(data["time_unit"]) == "s", "Unexpected time unit.")


    time = np.asarray(data["t_lox"], dtype=float)
    flow = np.asarray(data["mdot_lox_values"], dtype=float)

    require(time.ndim == 1, "Expected a one-dimensional time array.")
    require(flow.ndim == 1, "Expected a one-dimensional flow array.")
    require(time.size >= 2, "At least two samples are required.")
    require(time.size == flow.size, "Time and flow lengths differ.")

    require(np.all(np.isfinite(time)), "Non-finite times found.")
    require(np.all(np.isfinite(flow)), "Non-finite flows found.")
    require(np.all(np.diff(time) > 0), "Times must strictly increase.")

    require(
        np.isclose(time[0], EXPECTED_START, rtol=0, atol=TIME_ATOL),
        "Unexpected simulation start time.",
    )
    require(
        np.isclose(time[-1], EXPECTED_STOP, rtol=0, atol=TIME_ATOL),
        "Unexpected simulation stop time.",
    )
    require(
        np.all(flow >= -FLOW_ATOL),
        "Negative flow exceeds the allowed numerical tolerance.",
    )

    final_flow = float(flow[-1])
    minimum_flow = float(np.min(flow))
    maximum_flow = float(np.max(flow))
    flow_range = maximum_flow - minimum_flow

    final_difference = final_flow - TARGET_FLOW
    final_relative_difference = final_difference / TARGET_FLOW

    allowed_difference = FLOW_ATOL + FLOW_RTOL * abs(TARGET_FLOW)

    final_pass = bool(
        np.isclose(
            final_flow,
            TARGET_FLOW,
            rtol=FLOW_RTOL,
            atol=FLOW_ATOL,
        )
    )

    all_samples_pass = bool(
        np.all(
            np.isclose(
                flow,
                TARGET_FLOW,
                rtol=FLOW_RTOL,
                atol=FLOW_ATOL,
            )
        )
    )

    duration = float(time[-1] - time[0])
    transported_mass = float(np.trapezoid(flow, x=time))
    nominal_mass = TARGET_FLOW * duration
    time_average_flow = transported_mass / duration

    summary = {
        "model_name": str(data["model_name"]),
        "sample_count": int(time.size),
        "start_time_s": float(time[0]),
        "stop_time_s": float(time[-1]),
        "rounded_target_flow_kg_s": TARGET_FLOW,
        "final_flow_kg_s": final_flow,
        "minimum_flow_kg_s": minimum_flow,
        "maximum_flow_kg_s": maximum_flow,
        "flow_range_kg_s": flow_range,
        "time_average_flow_kg_s": time_average_flow,
        "final_minus_rounded_target_kg_s": final_difference,
        "final_relative_difference_to_rounded_target":
            final_relative_difference,
        "flow_rtol": FLOW_RTOL,
        "flow_atol_kg_s": FLOW_ATOL,
        "allowed_flow_difference_kg_s": allowed_difference,
        "final_flow_within_tolerance": final_pass,
        "all_samples_within_tolerance": all_samples_pass,
        "transported_mass_kg": transported_mass,
        "nominal_constant_flow_mass_kg": nominal_mass,
    }

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with SUMMARY_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary))
        writer.writeheader()
        writer.writerow(summary)

    FIGURE_FILE.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(
        2, 1, figsize=(9, 7), sharex=True, constrained_layout=True
    )

    axes[0].plot(time, flow, label="Simscape export", linewidth=1.5)
    axes[0].axhline(
        TARGET_FLOW,
        color="black",
        linestyle="--",
        label="Rounded nominal target",
    )
    axes[0].set_ylim(
        0,
        1.1 * max(maximum_flow, TARGET_FLOW),
    )
    axes[0].set_ylabel("LOX mass flow [kg/s]")
    axes[0].set_title("LOX equivalent restriction — nominal operating point")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(time, flow - TARGET_FLOW, linewidth=1.5)
    axes[1].axhline(0, color="black", linestyle="--")
    axes[1].set_xlabel("Time [s]")
    axes[1].set_ylabel("Flow minus rounded target [kg/s]")
    axes[1].grid(True)

    fig.savefig(FIGURE_FILE, dpi=200)
    plt.close(fig)

    print("--- LOX restriction export analysis ---")
    print(f"Samples: {time.size}")
    print(f"Time interval: {time[0]:.9f} to {time[-1]:.9f} s")
    print(f"Rounded target: {TARGET_FLOW:.6f} kg/s")
    print(f"Initial flow: {flow[0]:.9f} kg/s")
    print(f"Final flow: {final_flow:.9f} kg/s")
    print(f"Minimum flow: {minimum_flow:.9f} kg/s")
    print(f"Maximum flow: {maximum_flow:.9f} kg/s")
    print(f"Flow range: {flow_range:.9e} kg/s")
    print(f"Allowed flow difference: {allowed_difference:.9e} kg/s")
    print(f"Final-flow check: {'PASS' if final_pass else 'FAIL'}")
    print(
        "All-sample nominal-flow check: "
        f"{'PASS' if all_samples_pass else 'FAIL'}"
    )
    print(f"Integrated transported mass: {transported_mass:.9f} kg")
    print(f"Nominal constant-flow mass: {nominal_mass:.9f} kg")
    print(f"Summary saved to: {SUMMARY_FILE}")
    print(f"Figure saved to: {FIGURE_FILE}")
    print(
        "Scope: saved nominal-case data only; "
        "not experimental validation or model-parameter verification."
    )

    require(final_pass, "Final flow is outside the nominal-case tolerance.")

    if not all_samples_pass:
        print(
            "WARNING: Some samples differ from the nominal target. "
            "Inspect the time history before interpreting the result."
        )


if __name__ == "__main__":
    main()