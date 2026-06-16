from datetime import datetime, timedelta
from jose import jwt

# إعدادات الـ JWT (تقدري تغيري الـ SECRET_KEY براحتك)
SECRET_KEY = "SUPER_SECRET_RAG_ASSISTANT_KEY_2026" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # التوكن هتقعد ساعة وتنتهي للأمان

# 1. دالة الـ Hash (مؤقتة ومبسطة عشان نضمن إنها متضربش معاكِ)
def hash_password(password: str) -> str:
    return password

# 2. دالة التحقق
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password == hashed_password

# 3. دالة توليد الـ JWT Token السحرية ✨
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt