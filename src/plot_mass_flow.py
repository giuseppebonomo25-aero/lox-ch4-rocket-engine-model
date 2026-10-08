from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .performance import (
    calculate_total_mass_flow,
    split_propellant_mass_flow,
)


def main() -> None:
    thrust = 100_000.0
    specific_impulse = 350.0
    mixture_ratios = np.linspace(1.5, 5.0, 100)

    total_flow = calculate_total_mass_flow(
        thrust=thrust,
        specific_impulse=specific_impulse,
    )

    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    lox_flows = []
    methane_flows = []

    for mixture_ratio in mixture_ratios:
        lox_flow, methane_flow = split_propellant_mass_flow(
            total_mass_flow=total_flow,
            oxidizer_to_fuel_ratio=mixture_ratio,
        )

        lox_flows.append(lox_flow)
        methane_flows.append(methane_flow)

    table_ratios = [2.0, 3.0, 3.5, 4.0, 5.0]

    table_lines = [
        "O/F,Total flow [kg/s],LOX flow [kg/s],CH4 flow [kg/s]"
    ]

    for mixture_ratio in table_ratios:
        lox_flow, methane_flow = split_propellant_mass_flow(
            total_mass_flow=total_flow,
            oxidizer_to_fuel_ratio=mixture_ratio,
        )

        table_lines.append(
            f"{mixture_ratio:.2f},"
            f"{total_flow:.6f},"
            f"{lox_flow:.6f},"
            f"{methane_flow:.6f}"
        )

    (results_dir / "mass_flow_table.csv").write_text(
        "\n".join(table_lines) + "\n",
        encoding="utf-8",
    )

    plt.figure(figsize=(8, 5))
    plt.plot(mixture_ratios, lox_flows, label="LOX")
    plt.plot(mixture_ratios, methane_flows, label="CH4")

    plt.xlabel("Oxidizer-to-fuel ratio, O/F")
    plt.ylabel("Mass flow rate [kg/s]")
    plt.title("Propellant Mass Flow Split")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        results_dir / "propellant_mass_flow_split.png",
        dpi=300,
    )
    plt.show()


if __name__ == "__main__":
    main()