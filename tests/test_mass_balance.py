from pathlib import Path


import numpy as np
from scipy.io import loadmat

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAT_FILE = PROJECT_ROOT / "results" / "matlab_simulink" / "baseline_export.mat"


def test_lox_plus_ch4_equals_total_mass():
    data = loadmat(MAT_FILE)

    total_kg = data["total_mass_kg"].ravel()
    lox_kg = data["lox_mass_kg"].ravel()
    ch4_kg = data["ch4_mass_kg"].ravel()

    np.testing.assert_allclose(
        lox_kg + ch4_kg,
        total_kg,
        rtol=1e-8,
        atol=1e-6,
    )
