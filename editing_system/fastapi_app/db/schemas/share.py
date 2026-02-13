from pydantic import BaseModel, EmailStr


class ShareRequest(BaseModel):
    email: EmailStr

