"""Prospective fixed CI account models, never actual runner account evidence."""
from types import SimpleNamespace
import pytest
from test_linux_lease_control import control


def facts():
    return {'name':'irc','uid':39,'gid':39,'caller_uid':1001,'caller_gid':1001,
            'uid_names':['irc'],'gid_names':['irc'],'primary_names':['irc'],
            'supplementary_names':[],'active':False,'home_exposed':False}


def model(monkeypatch, *, shared_nobody=False):
    c=control()
    users=[SimpleNamespace(pw_name=name,pw_uid=uid,pw_gid=gid,pw_dir=home) for name,uid,gid,home in
           [('irc',39,39,'/TEST_ONLY-no-irc-home'),('nobody',65534,65534,'/TEST_ONLY-no-nobody-home')]]
    if shared_nobody:
        users.extend(SimpleNamespace(pw_name=name,pw_uid=100+i,pw_gid=65534,pw_dir='/TEST_ONLY-no-home')
                     for i,name in enumerate(('_apt','dhcpcd','sshd','sync')))
    lookups=[]
    def lookup(name):
        lookups.append(name)
        return next(user for user in users if user.pw_name==name)
    monkeypatch.setattr(c.pwd,'getpwnam',lookup)
    monkeypatch.setattr(c.pwd,'getpwall',lambda:users)
    monkeypatch.setattr(c.grp,'getgrall',lambda:[SimpleNamespace(gr_name=name,gr_gid=gid,gr_mem=[])
                                             for name,gid in [('irc',39),('nogroup',65534)]])
    class ModelPath:
        def __init__(self,path): self.path=path
        def read_text(self):
            assert self.path=='/proc/201/status'
            return 'TEST_ONLY caller status'
        def exists(self): return False
    monkeypatch.setattr(c,'Path',ModelPath)
    unused=[]; verified=[]
    g=SimpleNamespace(parse_status=lambda value:{'Gid':'1001'},candidate_unused=lambda uid,gid:unused.append((uid,gid)))
    caller=SimpleNamespace(pid=201,uid=[1001]*4,verify=lambda:verified.append(True))
    return c,g,caller,lookups,unused,verified


def test_fixed_ci_source_uses_only_irc_without_accepting_shared_nobody(monkeypatch):
    c,g,caller,lookups,unused,verified=model(monkeypatch,shared_nobody=True)
    assert c.ci_principal_facts(g,caller)==facts()
    assert lookups==['irc'] and unused==[(39,39)] and verified==[True]
    with pytest.raises(ValueError,match='unsafe, shared'):c.principal_facts(g,caller)
    assert lookups==['irc','nobody'], 'No fallback or creation is permitted'


@pytest.mark.parametrize('change',[
    {'name':'nobody'},{'uid':65534},{'gid':65534},{'uid':True},{'gid':True},
    {'caller_uid':39},{'caller_gid':39},{'uid_names':['irc','other']},
    {'gid_names':['irc','other']},{'gid_names':['wrong']},{'primary_names':['irc','other']},
    {'supplementary_names':['other']},{'active':True},{'active':None},
    {'home_exposed':True},{'home_exposed':None},
])
def test_ci_principal_safety_and_exact_fixed_identity_cannot_be_weakened(change):
    c=control();candidate=facts();candidate.update(change)
    with pytest.raises(ValueError):c.validate_ci_principal(candidate)


def test_fixed_ci_absence_has_no_fallback_but_production_still_looks_up_nobody(monkeypatch):
    c=control();lookups=[]
    def missing(name):
        lookups.append(name)
        raise KeyError('TEST_ONLY missing fixed account')
    monkeypatch.setattr(c.pwd,'getpwnam',missing)
    with pytest.raises(c.CiPrerequisiteUnavailable) as caught:c.ci_principal_facts(None,None)
    assert caught.value.facts['name']=='irc' and lookups==['irc']
    with pytest.raises(KeyError):c.principal_facts(None,None)
    assert lookups==['irc','nobody']


def test_legacy_validator_and_fixed_ci_validator_are_disjoint():
    c=control();ci=facts();old=dict(ci,name='nobody',uid=65534,gid=65534,
                                  uid_names=['nobody'],gid_names=['nogroup'],primary_names=['nobody'])
    assert c.validate_ci_principal(ci)==(39,39)
    assert c.validate_principal(old)==(65534,65534)
    with pytest.raises(ValueError):c.validate_principal(ci)
    with pytest.raises(ValueError):c.validate_ci_principal(old)
    assert ci==facts()
