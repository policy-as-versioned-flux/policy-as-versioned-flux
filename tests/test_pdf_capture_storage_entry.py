"""Held-entry source authentication and genuine transport revocation models."""
import pytest
from test_pdf_capture_storage import born,host_model,model_terminal
from twin import pdf_capture_storage as s,pdf_comparison_capture as c


class HeldClock:
    def __init__(self,value):self.value=value;self.target=None;self.remaining=0;self.effects=[];self.guard_to_delay=None;self.late_value=None;self.delay_remaining=0
    def __call__(self):
        if self.target is not None:
            self.remaining-=1
            if self.remaining==0:
                name=self.target;self.target=None
                def revoked(*args):self.effects.append('revoked helper executed')
                setattr(s,name,revoked)
        observed=self.value
        if self.guard_to_delay is not None:
            # A fixed transport models guard readback duration after this
            # clock observation, without changing any product dispatch.
            self.delay_remaining-=1
            if self.delay_remaining==0:self.guard_to_delay.later_value=self.late_value;self.guard_to_delay=None
        return observed


def clock_model(monkeypatch):
    original,selected=born(monkeypatch,allocate=False)
    clock=HeldClock(original._started+1);monkeypatch.setattr(c.time,'monotonic',clock)
    object.__setattr__(selected,'_guard',s._source_guard())
    # Scope restoration belongs to the test transport, not private ledger state.
    return original,selected,clock


@pytest.mark.parametrize('clock_call',(1,2))
@pytest.mark.parametrize('target',('_end','_check_cell'))
def test_held_entry_refuses_scoped_revocation_before_success(monkeypatch,clock_call,target):
    original,selected,clock=clock_model(monkeypatch);s._allocate_selected_stage(original);allocation=s._noncapture(original);cell=s._bound_cell(original)
    monkeypatch.setattr(s,target,getattr(s,target));clock.target=target;clock.remaining=clock_call
    before=(original._retained,original._reserve)
    with pytest.raises(ValueError) as caught:s._reserve_retained(allocation,3)
    assert original._stopped and cell.first_exception is caught.value and clock.effects==[]
    assert (original._retained,original._reserve)==before and cell.journal[-1]['status']=='HELD'


@pytest.mark.parametrize('target',('_end','_check_cell'))
def test_held_retention_entry_rechecks_after_finalizer_and_keeps_payload(monkeypatch,target):
    original,selected,clock=clock_model(monkeypatch);s._allocate_selected_stage(original);allocation=s._noncapture(original);permit=s._reserve_retained(allocation,3);cell=s._bound_cell(original)
    monkeypatch.setattr(s,target,getattr(s,target));clock.target=target;clock.remaining=2
    total=original._retained+original._reserve;raw=bytes(bytearray(b'abc'))
    with pytest.raises(ValueError) as caught:s._retain(original,permit,raw)
    assert original._stopped and cell.first_exception is caught.value and clock.effects==[]
    assert cell._owners[0]._payload is raw and cell._owners[0].transferred and cell._owners[0].phase=='PENDING'
    assert permit.phase=='TRANSFER_PENDING' and original._retained+original._reserve==total and cell.journal[-1]['status']=='HELD'


def test_initial_entry_reauthenticates_after_genuine_clock_before_charge(monkeypatch):
    original,selected,clock=clock_model(monkeypatch)
    monkeypatch.setattr(s,'_verify_guard',s._verify_guard);clock.target='_verify_guard';clock.remaining=1
    with pytest.raises(ValueError) as caught:s._allocate_selected_stage(original)
    cell=s._bound_cell(original)
    assert original._stopped and cell.first_exception is caught.value and clock.effects==[]
    assert original._retained==0 and original._reserve==s.RESERVE and cell.technical_phase=='NOT_CHARGED'


@pytest.mark.parametrize('entry,helper',(('noncapture','_bound_cell'),('reserve','_allocation_cell'),('reserve','_begin'),('reserve','_reserve'),('reserve','_fail'),('scratch-reserve','_check_cell'),('spend','_permit'),('retain','_permit'),('capture','_host_evidence'),('close','_host_evidence')))
def test_fixed_entry_checks_reached_dispatch_before_effects(monkeypatch,entry,helper):
    def held_window(context,**kwargs):return c.sm._json(context._policy)
    monkeypatch.setattr(c.n,'_host_window',held_window)
    original,_,cell,selected=born(monkeypatch,real_guard=True);allocation=s._noncapture(original);permit=s._reserve_retained(allocation,3);scratch=s._reserve_scratch(allocation,1);effects=[]
    context=host_model(monkeypatch,original,selected)
    monkeypatch.setattr(c.n,'_host_window',held_window)
    if entry=='close':allocation=s._capture_allocation(original,context);model_terminal(original,0,context)
    before=(original._retained,original._reserve)
    def changed(*args,**kwargs):effects.append('changed inner helper')
    monkeypatch.setattr(s,helper,changed)
    with pytest.raises(ValueError):
        if entry=='noncapture':s._noncapture(original)
        elif entry=='reserve':s._reserve_retained(allocation,1)
        elif entry=='scratch-reserve':s._reserve_scratch(allocation,1)
        elif entry=='spend':s._spend_scratch(original,scratch)
        elif entry=='retain':s._retain(original,permit,b'abc')
        elif entry=='capture':s._capture_allocation(original,context)
        else:s._close_capture(allocation)
    assert effects==[] and original._stopped and before==(original._retained,original._reserve) and cell.first_exception is not None


class HeldReadback:
    def __init__(self,actual,clock):self.actual=actual;self.clock=clock;self.later_value=None;self.description=actual.description
    def verify(self):
        self.actual.verify()
        if self.later_value is not None:self.clock.value=self.later_value;self.later_value=None


@pytest.mark.parametrize('initial',(False,True))
def test_held_entry_checks_original_window_after_final_guard_readback(monkeypatch,initial):
    original,selected,clock=clock_model(monkeypatch)
    transport=HeldReadback(selected._guard,clock);object.__setattr__(selected,'_guard',transport)
    if not initial:s._allocate_selected_stage(original);allocation=s._noncapture(original)
    # Fixed transports are installed before entry; only their queued duration
    # changes. No product/helper dispatch or private ledger state is replaced.
    clock.guard_to_delay=transport;clock.delay_remaining=3 if initial else 2
    clock.late_value=original._started+(60.25 if initial else 10800.25)
    with pytest.raises(ValueError):
        if initial:s._allocate_selected_stage(original)
        else:s._reserve_retained(allocation,1)
    assert original._stopped and s._bound_cell(original).phase=='STOPPED'
