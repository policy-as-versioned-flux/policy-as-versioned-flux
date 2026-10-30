"""CASE-FREE task shapes and independently frozen rubrics."""
import pytest


def test_task_contract_shapes_reject_bool_magnitude_and_invalid_dates():
    from twin.task_contracts import TaskContract, validate, decode
    contract = TaskContract.freeze('causal')
    assert contract.metrics == ('causal-claims', 'causal-claims-grade-accuracy')
    contract.verify()
    validate('Pert', {'min': 0, 'mode': .5, 'max': 1})
    for bad in ({'min': False, 'mode': .5, 'max': 1}, {'min': 0, 'mode': 2, 'max': 1}):
        with pytest.raises(ValueError):
            validate('Pert', bad)
    with pytest.raises(ValueError):
        validate('PublicContext', {'as_of': '2026-02-30'})
    for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'```{}', b'{} {}', b'"\xff"'):
        with pytest.raises(ValueError):
            decode(raw)
