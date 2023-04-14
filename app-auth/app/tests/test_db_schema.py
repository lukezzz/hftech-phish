import pytest
from app.main import app

from app.models.aaa import *
from app.common.security import PermissionType
from app.common.db import get_db
from .conftest import override_get_db

app.dependency_overrides[get_db] = override_get_db
from .conftest import db


## 测试 user account roles
@pytest.mark.parametrize(
    ("name",),
    (
        ("admin",),
        ("op",),
        ("viewer",),
    ),
)
def test_init_roles(name):
    assert db.query(Role).filter_by(name=name).first().name == name


## admin为系统默认用户
def test_init_default_user():
    assert db.query(UserAccount).filter_by(username="admin").first().username == "admin"
    assert db.query(UserAccount).filter_by(username="test_admin").first() == None


## 测试 admin的permission是否包含 "can_edit_any"
@pytest.mark.parametrize(
    ("username", "permission"),
    (("admin", PermissionType.can_edit_any.value),),
)
def test_init_user_permission(username, permission):
    user = db.query(UserAccount).filter_by(username=username).first()
    permissions = []
    for role in user.roles:
        permissions = permissions + [p.name for p in role.permissions]
    assert permission in permissions
