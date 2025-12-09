from typing import Optional
from pydantic import BaseModel, EmailStr

class SigninSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True  

class SignupSchema(SigninSchema):
    name: str
    admin: Optional[bool] = False
    
    class Config:
        from_attributes = True  