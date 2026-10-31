"""Fixed C1 initialization/method-custody regressions; no actual selection/OS."""
import pytest
from test_pdf_capture_storage import born
from twin import pdf_capture_storage as s,pdf_remap_resources as r,pdf_comparison_capture as c


def test_initial_guard_refuses_changed_helper_without_effects_or_retry(monkeypatch):
    original,selected=born(monkeypatch,allocate=False,real_guard=True);effects=[];actual=r._stage_placeholder
    def changed(owner):effects.append('modeled write');return actual(owner)
    monkeypatch.setattr(r,'_stage_placeholder',changed)
    with pytest.raises(ValueError) as caught:s._allocate_selected_stage(original)
    cell=s._bound_cell(original)
    assert effects==[] and original._stopped and original._technical_state is None and cell._stage is None
    assert selected._initial_cell is cell and cell.first_exception is caught.value and cell.journal[0]['status']=='HELD'
    monkeypatch.setattr(r,'_stage_placeholder',actual)
    with pytest.raises(ValueError):s._allocate_selected_stage(original)
    assert s._bound_cell(original) is cell and cell.first_exception is caught.value and effects==[]


@pytest.mark.parametrize('name',('_Cell','_Allocation','_Permit','_OwnedBytes','_StageState','OriginalComparisonSuite'))
def test_behaviorful_method_defaults_are_fixed_before_mutation(monkeypatch,name):
    original,_,cell,_=born(monkeypatch,real_guard=True);allocation=s._noncapture(original)
    cls=r._StageState if name=='_StageState' else c.OriginalComparisonSuite if name=='OriginalComparisonSuite' else getattr(s,name)
    monkeypatch.setattr(cls.__setattr__,'__defaults__',(None,))
    before=(original._retained,original._reserve,allocation.issued)
    with pytest.raises(ValueError):s._reserve_retained(allocation,3)
    assert original._stopped and before==(original._retained,original._reserve,allocation.issued) and not cell._owners


@pytest.mark.parametrize('name',('_Cell','OriginalComparisonSuite'))
def test_emergency_stop_does_not_invoke_changed_setter(monkeypatch,name):
    original,_,cell,_=born(monkeypatch,real_guard=True);allocation=s._noncapture(original);effects=[]
    cls=s._Cell if name=='_Cell' else c.OriginalComparisonSuite;actual=cls.__setattr__
    def changed(owner,key,value):effects.append(key);return actual(owner,key,value)
    monkeypatch.setattr(cls,'__setattr__',changed)
    with pytest.raises(ValueError) as caught:s._reserve_retained(allocation,3)
    assert effects==[] and original._stopped and cell.first_exception is caught.value and cell.phase=='STOPPED'


@pytest.mark.parametrize('mutation',('dispatch','code','defaults'))
def test_local_guard_entry_is_checked_by_unchanged_core_before_call(monkeypatch,mutation):
    original,_,cell,_=born(monkeypatch,real_guard=True);allocation=s._noncapture(original);effects=[]
    def replacement(self):effects.append('changed verifier')
    def code_change(self):raise AssertionError('changed verifier must not execute')
    if mutation=='dispatch':monkeypatch.setattr(s._Guard,'verify',replacement)
    if mutation=='code':monkeypatch.setattr(s._Guard.verify,'__code__',code_change.__code__)
    if mutation=='defaults':monkeypatch.setattr(s._Guard.verify,'__defaults__',(None,))
    before=(original._retained,original._reserve,allocation.issued)
    with pytest.raises(ValueError):s._reserve_retained(allocation,3)
    assert effects==[] and original._stopped and before==(original._retained,original._reserve,allocation.issued) and not cell._owners
