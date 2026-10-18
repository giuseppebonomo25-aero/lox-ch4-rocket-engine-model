from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STEP_EXPORT_FILE = (
    PROJECT_ROOT / "results" / "matlab_simulink" / "step_export.mat"
)

MASS_FLOW_PAIRS = [
    ("total_mass_kg", "total_flow_kg_s"),
    ("lox_mass_kg", "lox_flow_kg_s"),
    ("ch4_mass_kg", "ch4_flow_kg_s"),
]

@pytest.fixture(scope="module")
def step_data():
    assert STEP_EXPORT_FILE.is_file(), (
        f"Missing Step export: {STEP_EXPORT_FILE}."
        "Run scripts/matlab/export_step_case.m first"
    )


    data = loadmat(STEP_EXPORT_FILE, squeeze_me=True)

    required = [
        "profile_name",
        "t",
        "total_mass_kg",
        "lox_mass_kg",
        "ch4_mass_kg",
        "total_flow_kg_s",
        "lox_flow_kg_s",
        "ch4_flow_kg_s",
        "start_time_s",
        "stop_time_s",
    ]


    missing = [name for name in required if name not in data]
    assert not missing, f"Missing exported variables: {missing}"

    return data

def test_step_profile_label(step_data):
    assert str(step_data["profile_name"]) == "step"

def test_step_time_axis(step_data):
    time_s = np.asarray(step_data["t"], dtype=float).ravel()

    start_time = float(step_data["start_time_s"])
    stop_time = float(step_data["stop_time_s"])

    assert time_s.size >=2
    assert np.all(np.isfinite(time_s))
    assert np.isfinite(start_time)
    assert np.isfinite(stop_time)
    assert 0 <= start_time < stop_time

    # Repeated timestamps are allowed, but time must not go backwards.
    assert np.all(np.diff(time_s) >= 0)
    assert np.any(np.diff(time_s) > 0)

    np.testing.assert_allclose(
        time_s[0], 0.0, rtol=0, atol=1e-9
    )
    np.testing.assert_allclose(
        time_s[-1], stop_time, rtol=0, atol=1e-9
    )



@pytest.mark.parametrize("mass_key, flow_key", MASS_FLOW_PAIRS)
def test_step_mass_series_are_valid(step_data, mass_key, flow_key):
    time_s = np.asarray(step_data["t"], dtype=float).ravel()
    mass_kg = np.asarray(step_data[mass_key], dtype=float).ravel()
    flow_kg_s = float(step_data[flow_key])


    assert mass_kg.size == time_s.size
    assert mass_kg.size >= 2
    assert np.all(np.isfinite(mass_kg))
    assert np.isfinite(flow_kg_s)
    assert flow_kg_s > 0

    assert np.all(mass_kg >= -1e-9)
    assert np.all(np.diff(mass_kg) >= -1e-9)


def test_step_mass_balance(step_data):
    total_kg = np.asarray(step_data["total_mass_kg"]).ravel()
    lox_kg = np.asarray(step_data["lox_mass_kg"]).ravel()
    ch4_kg = np.asarray(step_data["ch4_mass_kg"]).ravel()

    assert total_kg.shape == lox_kg.shape == ch4_kg.shape

    np.testing.assert_allclose(
        lox_kg + ch4_kg,
        total_kg,
        rtol=1e-8,
        atol=1e-6,
        equal_nan=False,
    )


@pytest.mark.parametrize("mass_key,flow_key", MASS_FLOW_PAIRS)
def test_step_mass_matches_analytical_curve(
    step_data, mass_key, flow_key
):
    time_s = np.asarray(step_data["t"], dtype=float).ravel()
    mass_kg = np.asarray(step_data[mass_key], dtype=float).ravel()

    flow_kg_s = float(step_data[flow_key])
    start_time = float(step_data["start_time_s"])

    expected_mass_kg = flow_kg_s * np.maximum(
        time_s - start_time, 0.0
    )

    assert mass_kg.shape == expected_mass_kg.shape

    np.testing.assert_allclose(
        mass_kg,
        expected_mass_kg,
        rtol=1e-8,
        atol=1e-6,
        equal_nan=False,
        err_msg=f"{mass_key} does not match the ideal Step curve",
    )


def test_step_nominal_flow_balance(step_data):
    total_flow = float(step_data["total_flow_kg_s"])
    lox_flow = float(step_data["lox_flow_kg_s"])
    ch4_flow = float(step_data["ch4_flow_kg_s"])

    np.testing.assert_allclose(
        lox_flow + ch4_flow,
        total_flow,
        rtol=1e-12,
        atol=1e-12,
        equal_nan=False,
    )


def test_step_reference_mixture_ratio(step_data):
    lox_flow = float(step_data["lox_flow_kg_s"])
    ch4_flow = float(step_data["ch4_flow_kg_s"])

    assert ch4_flow > 0

    np.testing.assert_allclose(
        lox_flow / ch4_flow,
        3.5,
        rtol=1e-12,
        atol=0,
        equal_nan=False,
    )


