import pytest

from engine_build.validation.helpers import run_validation_case
from engine_build.validation.contracts import REGIME_CONTRACTS
from engine_build.validation.assertions import assert_finite_summary, assert_contract


@pytest.mark.parametrize("regime_name", ["stable", "extinction", "saturated"])
def test_regime_contract(regime_name: str):
    case = run_validation_case(regime_name)

    assert_finite_summary(case.summary)
    assert_contract(case.summary, REGIME_CONTRACTS[regime_name])

