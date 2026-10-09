import pytest

from src.config import EngineCase


def test_default_engine_case():
    case = EngineCase()


    assert case.thrust == pytest.approx(100_000.0)
    assert case.specific_impulse == pytest.approx(350.0)
    assert case.mixture_ratio == pytest.approx(3.5)
    assert case.burn_time == pytest.approx(10.0)



@pytest.mark.parametrize(
    "field",
    ["thrust","specific_impulse","mixture_ratio","burn_time"],
)

def test_invalid_engine_case(field):
    values = {
        "thrust": 100_000.0,
        "specific_impulse": 350.0,
        "mixture_ratio": 3.5,
        "burn_time": 10.0,
    }
    values[field] = 0.0

    with pytest.raises(ValueError):
        EngineCase(**values)