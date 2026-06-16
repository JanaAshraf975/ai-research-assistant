from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# البيانات المطلوبة عند التسجيل
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# شكل البيانات اللي هترجع لما نعرض بيانات مستخدم
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

# البيانات المطلوبة عند الـ Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# شكل الـ Token
class Token(BaseModel):
    access_token: str
    token_type: str

# شكل البيانات المخرجة اللي جوا الـ Token
class TokenData(BaseModel):
    email: str | None = None

# الشكل اللي هيرجع بعد رفع الملف بنجاح
class UploadResponse(BaseModel):
    message: str
    file_name: str
    total_chunks: int

# الشكل الصحيح للـ ChatRequest
class ChatRequest(BaseModel):
    question: str
    language: str = "English"

# ضيفي كلاس جديد للـ Source عشان نحدد شكل البيانات اللي جوا الـ List
class Source(BaseModel):
    text: str
    file: str

# عدلي الـ ChatResponse عشان تستخدم الـ Source الجديد
class ChatResponse(BaseModel):
    answer: str
    sources: list[Source] # هنا بدل ما كانت list[str] بقت list[Source]