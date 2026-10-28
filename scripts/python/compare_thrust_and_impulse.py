from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "results" / "matlab_simulink"
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"


def read_series(data, time_key, value_key):
    time = np.asarray(data[time_key], dtype=float).ravel()
    values = np.asarray(data[value_key], dtype=float).ravel()

    assert time.size == values.size, (
        f"Inconsistent lengths: {time_key}, {value_key}"
    )
    assert time.size >= 2, f"Insufficient samples: {value_key}"
    assert np.all(np.isfinite(time)), f"Invalid times: {time_key}"
    assert np.all(np.isfinite(values)), f"Invalid values: {value_key}"
    assert np.all(np.diff(time) >= 0), (
        f"Time goes backwards: {time_key}"
    )
    assert np.any(np.diff(time) > 0), (
        f"Time does not advance: {time_key}"
    )

    return time, values


def load_case(case):
    file_path = EXPORT_DIR / f"{case}_export.mat"
    assert file_path.is_file(), f"Missing export: {file_path}"

    data = loadmat(file_path, squeeze_me=True)

    required = [
        "thrust_time_s",
        "thrust_N_series",
        "impulse_time_s",
        "impulse_N_s_series",
        "thrust_N",
        "isp_s",
        "g0_m_s2",
        "start_time_s",
        "stop_time_s",
    ]

    if case == "ramp":
        required.append("ramp_duration_s")

    missing = [key for key in required if key not in data]
    assert not missing, f"{case}: missing variables {missing}"

    for key in [
        "thrust_N",
        "isp_s",
        "g0_m_s2",
        "start_time_s",
        "stop_time_s",
    ]:
        assert np.isfinite(float(data[key])), (
            f"{case}: invalid parameter {key}"
        )

    return data


def main():
    cases = {
        "step": load_case("step"),
        "ramp": load_case("ramp"),
    }

    # Compare the same nominal conditions and simulation interval.
    for key in [
        "thrust_N",
        "isp_s",
        "g0_m_s2",
        "start_time_s",
        "stop_time_s",
    ]:
        np.testing.assert_allclose(
            float(cases["step"][key]),
            float(cases["ramp"][key]),
            rtol=1e-12,
            atol=1e-12,
            equal_nan=False,
            err_msg=f"Exports use different values of {key}",
        )

    fig, axes = plt.subplots(
        2, 1, figsize=(10, 7), sharex=True
    )

    final_impulses = {}

    for case, data in cases.items():
        thrust_time, thrust = read_series(
            data, "thrust_time_s", "thrust_N_series"
        )
        impulse_time, impulse = read_series(
            data, "impulse_time_s", "impulse_N_s_series"
        )

        nominal_thrust = float(data["thrust_N"])
        activation_time = float(data["start_time_s"])
        stop_time = float(data["stop_time_s"])

        assert nominal_thrust > 0
        assert 0 <= activation_time < stop_time

        for time in (thrust_time, impulse_time):
            np.testing.assert_allclose(
                [time[0], time[-1]],
                [0.0, stop_time],
                rtol=0,
                atol=1e-9,
            )

        if case == "step":
            expected_impulse = nominal_thrust * (
                stop_time - activation_time
            )
            label = "Step"
        else:
            ramp_duration = float(data["ramp_duration_s"])
            assert np.isfinite(ramp_duration)
            assert 0 < ramp_duration < stop_time - activation_time

            expected_impulse = nominal_thrust * (
                stop_time - activation_time - ramp_duration / 2
            )
            label = f"Ramp ({ramp_duration:g} s)"

        np.testing.assert_allclose(
            impulse[-1],
            expected_impulse,
            rtol=1e-8,
            atol=1e-6,
            equal_nan=False,
            err_msg=f"{case}: final impulse differs from reference",
        )

        # Each signal is plotted against its own exported time axis.
        axes[0].plot(
            thrust_time, thrust / 1000,
            label=label, linewidth=1.8,
        )
        axes[1].plot(
            impulse_time, impulse / 1000,
            label=label, linewidth=1.8,
        )

        final_impulses[case] = float(impulse[-1])

        print(f"\n{label}")
        print(f"Maximum thrust: {np.max(thrust):.3f} N")
        print(f"Final impulse: {impulse[-1]:.3f} N s")
        print(f"Analytical reference: {expected_impulse:.3f} N s")

    difference = final_impulses["step"] - final_impulses["ramp"]
    print(f"\nStep minus ramp final impulse: {difference:.3f} N s")

    axes[0].set_ylabel("Thrust [kN]")
    axes[0].set_title("Prescribed-profile thrust comparison")
    axes[1].set_ylabel("Accumulated impulse [kN s]")
    axes[1].set_xlabel("Time [s]")

    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend()

    fig.suptitle("LOX/CH4 baseline — constant specific impulse")
    fig.tight_layout()

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    output_file = FIGURE_DIR / "step_vs_ramp_thrust_impulse.png"
    fig.savefig(output_file, dpi=200, bbox_inches="tight")

    print(f"\nSaved figure: {output_file}")
    plt.show()


if __name__ == "__main__":
    main()



