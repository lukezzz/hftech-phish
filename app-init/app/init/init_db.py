from sqlalchemy.orm import Session
from enum import Enum

from app.models.aaa import Permission, Role, UserAccount


class RoleNames(Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


class DefaultPermissionRules(Enum):
    admin = [
        "can_read_any",
        "can_edit_any",
        "can_delete_any",
        "can_create_any",
    ]
    api = [
        "can_api_read",
        "can_change_password",
    ]


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
            admin.email = "admin@admin.com"
            admin.set_password("secret")
            admin.role = admin_role
            db.add(admin)
            db.commit()

    except Exception as e:
        print(e)
        db.rollback()




# class DefaultPrpos(Enum):
#     default = "default"


# class DefaultPlatform(Enum):
#     Apache = "Apache"
#     IIS = "IIS"
#     Nginx = "Nginx"


# def init_assets(db: Session):
#     try:
#         for prop in DefaultPrpos:
#             check_project_existed = db.query(Project).filter_by(name=prop.value).first()
#             if not check_project_existed:
#                 check_project_existed = Project()
#                 check_project_existed.name = prop.value
#                 db.add(check_project_existed)

#         db.commit()

#     except Exception as e:
#         print(e)
#         db.rollback()

#     try:
#         for prop in DefaultPrpos:
#             check_location_existed = (
#                 db.query(Location).filter_by(name=prop.value).first()
#             )
#             if not check_location_existed:
#                 check_location_existed = Location()
#                 check_location_existed.name = prop.value
#                 db.add(check_location_existed)

#         db.commit()

#     except Exception as e:
#         print(e)
#         db.rollback()

#     try:
#         for prop in DefaultPlatform:
#             check_platform_existed = (
#                 db.query(Platform).filter_by(name=prop.value).first()
#             )
#             if not check_platform_existed:
#                 check_platform_existed = Platform()
#                 check_platform_existed.name = prop.value
#                 db.add(check_platform_existed)

#         db.commit()

#     except Exception as e:
#         print(e)
#         db.rollback()
