from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAMP_EXPORT_FILE = (
    PROJECT_ROOT / "results" / "matlab_simulink" / "ramp_export.mat" 
)



@pytest.fixture(scope="module")
def ramp_data():
    assert RAMP_EXPORT_FILE.exists, (
        f"Missing ramp export file: {RAMP_EXPORT_FILE}."
        "Run scripts/matlab/export_ramp_case.m first."
    )

    return loadmat(
        RAMP_EXPORT_FILE,
        squeeze_me=True,
        struct_as_record=False,
    )


def test_required_variables_exist(ramp_data):
    required = [
        "t",
        "total_mass_kg",
        "lox_mass_kg",
        "ch4_mass_kg",
        "total_flow_kg_s",
        "lox_flow_kg_s",
        "ch4_flow_kg_s",
        "start_time_s",
        "ramp_duration_s",
        "stop_time_s",
    ]


    for variable in required:
        assert variable in ramp_data, f"Missing exported variable: {variable}"


def test_time_series_have_same_length(ramp_data):
    time_s = np.asarray(ramp_data["t"]).ravel()
    total_kg = np.asarray(ramp_data["total_mass_kg"]).ravel()
    lox_kg = np.asarray(ramp_data["lox_mass_kg"]).ravel()
    ch4_kg = np.asarray(ramp_data["ch4_mass_kg"]).ravel()


    assert time_s.size > 0
    assert total_kg.size == time_s.size
    assert lox_kg.size == time_s.size
    assert ch4_kg.size == time_s.size


def test_masses_increase_monotonically(ramp_data):
    lox_kg = np.asarray(ramp_data["lox_mass_kg"]).ravel()
    ch4_kg = np.asarray(ramp_data["ch4_mass_kg"]).ravel()
    total_kg = np.asarray(ramp_data["total_mass_kg"]).ravel()

    np.testing.assert_array_less(
        np.concatenate(([lox_kg[0]], lox_kg[:-1])),
        lox_kg + 1e-9,
    )

    np.testing.assert_array_less(
        np.concatenate(([ch4_kg[0]], ch4_kg[:-1])),
        ch4_kg + 1e-9,
    )

    np.testing.assert_array_less(
        np.concatenate(([total_kg[0]], total_kg[:-1])),
        total_kg + 1e-9,
    )


def test_propellant_mass_balance(ramp_data):
    total_kg = np.asarray(ramp_data["total_mass_kg"]).ravel()
    lox_kg = np.asarray(ramp_data["lox_mass_kg"]).ravel()
    ch4_kg = np.asarray(ramp_data["ch4_mass_kg"]).ravel()

    np.testing.assert_allclose(
        lox_kg + ch4_kg,
        total_kg,
        rtol=1e-8,
        atol=1e-6,
    )



def test_final_total_mass_matches_analytical_ramp(ramp_data):
    total_kg = np.asarray(ramp_data["total_mass_kg"]).ravel()

    total_flow = float(ramp_data["total_flow_kg_s"])
    start_time = float(ramp_data["start_time_s"])
    ramp_duration = float(ramp_data["ramp_duration_s"])
    stop_time = float(ramp_data["stop_time_s"])

    expected_total_kg = total_flow * (
        stop_time - start_time - ramp_duration / 2
    )

    np.testing.assert_allclose(
        total_kg[-1],
        expected_total_kg,
        rtol=1e-8,
        atol=1e-6,
    )


def test_final_lox_mass_matches_analytical_ramp(ramp_data):
    lox_kg = np.asarray(ramp_data["lox_mass_kg"]).ravel()

    lox_flow = float(ramp_data["lox_flow_kg_s"])
    start_time = float(ramp_data["start_time_s"])
    ramp_duration = float(ramp_data["ramp_duration_s"])
    stop_time = float(ramp_data["stop_time_s"])

    expected_lox_kg = lox_flow * (
        stop_time - start_time - ramp_duration / 2
    )

    np.testing.assert_allclose(
        lox_kg[-1],
        expected_lox_kg,
        rtol=1e-8,
        atol=1e-6,
    )


def test_final_ch4_mass_matches_analytical_ramp(ramp_data):
    ch4_kg = np.asarray(ramp_data["ch4_mass_kg"]).ravel()

    ch4_flow = float(ramp_data["ch4_flow_kg_s"])
    start_time = float(ramp_data["start_time_s"])
    ramp_duration = float(ramp_data["ramp_duration_s"])
    stop_time = float(ramp_data["stop_time_s"])

    expected_ch4_kg = ch4_flow * (
        stop_time - start_time - ramp_duration / 2
    )

    np.testing.assert_allclose(
        ch4_kg[-1],
        expected_ch4_kg,
        rtol=1e-8,
        atol=1e-6,
    )


def test_mixture_ratio_is_3_5(ramp_data):
    lox_flow = float(ramp_data["lox_flow_kg_s"])
    ch4_flow = float(ramp_data["ch4_flow_kg_s"])

    of_ratio = lox_flow / ch4_flow

    np.testing.assert_allclose(of_ratio, 3.5, rtol=1e-12)


def test_ramp_duration_is_0_5_s(ramp_data):
    ramp_duration = float(ramp_data["ramp_duration_s"])

    np.testing.assert_allclose(ramp_duration, 0.5, rtol=1e-12)