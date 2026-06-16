from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⚠️ ركزي هنا جداً:
# لازم تغيري الـ password (المكتوبة هنا 123456) وتكتبي الباسورد الحقيقية بتاعتك اللي بتفتحي بيها pgAdmin
DATABASE_URL = "postgresql+psycopg2://postgres:Password for superuser (postgres)@localhost:5432/rag_research_db"

# إنشاء محرك الاتصال
engine = create_engine(DATABASE_URL)

# إنشاء جلسة اتصال (Session) لإرسال واستقبال البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# الكلاس الأساسي اللي هتعملي بيه الجداول بعدين
Base = declarative_base()
# ضيفي السطور دي في آخر ملف database.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()