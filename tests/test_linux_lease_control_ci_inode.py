"""Closed passive inode boundary; synthetic data cannot select a live caller."""
import pytest
from test_linux_lease_control_ci_sudo import Kernel,ci


def record_with_inode(monkeypatch,node,inode):
    model=Kernel();endpoint,record=model.run(monkeypatch)
    for snapshot in record['snapshots']:
        if snapshot['node']==node:
            for side in ('named_file','image_file'):snapshot['executable'][side]['inode']=inode
    return record

@pytest.mark.parametrize('node',[0,1,2],ids=['self','sudo','endpoint'])
def test_passive_inode_zero_refuses_for_every_role(monkeypatch,node):
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record_with_inode(monkeypatch,node,0))

@pytest.mark.parametrize('inode',[-1,False])
def test_passive_inode_existing_invalid_neighbors_still_refuse(monkeypatch,inode):
    with pytest.raises(ValueError):ci.validate_ci_caller_record(record_with_inode(monkeypatch,2,inode))


def test_passive_inode_one_remains_valid(monkeypatch):
    ci.validate_ci_caller_record(record_with_inode(monkeypatch,2,1))
