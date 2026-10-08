import pytest

from src.performance import (
    calculate_total_mass_flow,
    check_mass_flow_balance,
    split_propellant_mass_flow,
)


def test_total_mass_flow():
    result = calculate_total_mass_flow(
        thrust=100_000.0,
        specific_impulse=350.0,
    )

    assert result > 0
    assert result == pytest.approx(29.132, rel=1e-3)


def test_propellant_split():
    total_flow = 29.132

    lox_flow, methane_flow = split_propellant_mass_flow(
        total_mass_flow=total_flow,
        oxidizer_to_fuel_ratio=3.5,
    )

    assert lox_flow > 0
    assert methane_flow > 0
    assert lox_flow + methane_flow == pytest.approx(total_flow)
    assert lox_flow / methane_flow == pytest.approx(3.5)


def test_invalid_thrust():
    with pytest.raises(ValueError):
        calculate_total_mass_flow(
            thrust=0.0,
            specific_impulse=350.0,
        )


def test_invalid_mixture_ratio():
    with pytest.raises(ValueError):
        split_propellant_mass_flow(
            total_mass_flow=29.132,
            oxidizer_to_fuel_ratio=0.0,
        )

def test_mass_flow_balance():
    total_flow = 29.132

    lox_flow, methane_flow = split_propellant_mass_flow(
        total_mass_flow=total_flow,
        oxidizer_to_fuel_ratio=3.5,
    )

    assert check_mass_flow_balance(
        total_mass_flow=total_flow,
        oxidiser_flow=lox_flow,
        fuel_flow=methane_flow,

    )


