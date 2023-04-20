from pydantic import BaseModel, validator, Field
from typing import Any, Dict, Optional, List
from email_validator import validate_email, EmailNotValidError

# from app.common.user_preference import AppUserPermissionRule
from pydantic import BaseModel

class RoleCreate(BaseModel):
    name:str

class PermissionCreate(BaseModel):
    name:str