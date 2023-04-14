from sqlalchemy.orm import Session
from enum import Enum

from app.models.aaa import Permission, Role, UserAccount


class RoleNames(Enum):
    admin = "admin"
    op = "op"
    viewer = "viewer"


class DefaultPermissionRules(Enum):
    admin = ["can_read_any", "can_edit_any", "can_delete_any", "can_create_any"]
    op = []
    viewer = []


# add default Role, Permission and admin user
def init_aaa(db: Session):

    try:
        for user_role in RoleNames:
            check_role_existed = db.query(Role).filter_by(name=user_role.name).first()
            if not check_role_existed:
                check_role_existed = Role()
                check_role_existed.name = user_role.value
                db.add(check_role_existed)

        db.commit()

        for rule in DefaultPermissionRules:
            role = db.query(Role).filter_by(name=rule.name).first()
            if role:
                for permission_name in rule.value:
                    permission = (
                        db.query(Permission).filter_by(name=permission_name).first()
                    )
                    if not permission:
                        permission = Permission()
                        permission.name = permission_name
                        db.add(permission)

                    role.permissions.append(permission)
        db.commit()

        # add default admin user
        admin = db.query(UserAccount).filter_by(username="admin").first()
        admin_role = db.query(Role).filter_by(name="admin").first()
        if not admin:
            admin = UserAccount()
            admin.username = "admin"
            admin.display_name = "admin"
            admin.set_password("secret")
            admin.roles.append(admin_role)
            db.add(admin)

        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
