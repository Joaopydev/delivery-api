from typing import Optional
from pydantic import BaseModel, EmailStr

class SigninSchema(BaseModel):
    email: EmailStr
    password: str


class SignupSchema(SigninSchema):
    name: str
    active: Optional[bool] = True
    admin: Optional[bool] = False
    
