from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from google import genai 
from datetime import datetime
import traceback
import time

import models
import schemas
import auth_utils 
import pdf_utils 
from database import engine, get_db
from auth_utils import hash_password
import os



# 1. إعداد الـ App
app = FastAPI(title="AI-Powered Research Assistant")
models.Base.metadata.create_all(bind=engine)

# 🔑 إعداد عميل جيرمني
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
#client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

@app.get("/")
def read_root():
    return {"message": "Server is running!"}

# 2. تسجيل مستخدم جديد
@app.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered!")
    new_user = models.User(name=user_data.name, email=user_data.email, password_hash=hash_password(user_data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 3. تسجيل الدخول
@app.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth_utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth_utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# 4. رفع الملفات
@app.post("/documents/upload", response_model=schemas.UploadResponse)
def upload_research_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed!")
    
    try:
        db_doc = models.Document(filename=file.filename, user_id=1)
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        extracted_text = pdf_utils.extract_text_from_pdf(file.file)
        chunks = pdf_utils.split_text_into_chunks(extracted_text)
        pdf_utils.save_chunks_to_vector_db(chunks, document_id=db_doc.id, filename=file.filename)
        
        return {"message": "Document processed successfully!", "file_name": file.filename, "total_chunks": len(chunks)}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# 5. دالة المحادثة (المصححة)
@app.post("/chat", response_model=schemas.ChatResponse)
def chat_with_documents(chat_req: schemas.ChatRequest, db: Session = Depends(get_db)):
    time.sleep(1) # تأخير بسيط لتقليل الضغط
    try:
        results = pdf_utils.search_similar_chunks(chat_req.question, top_k=3)
        sources_list = [{"text": res.page_content, "file": res.metadata.get("filename", "Unknown")} for res in results]
        context = "\n\n".join([res.page_content for res in results])
        
        prompt = f"Context: {context}\nQuestion: {chat_req.question}\nAnswer in {chat_req.language}."
        
        response = client.models.generate_content(
            model='models/gemini-2.0-flash',
            contents=prompt,
        )
        
        answer_text = response.text or "No response generated."
        
        db_chat = models.ChatHistory(
            user_id=1, 
            question=chat_req.question, 
            answer=answer_text,
            sources=sources_list,
            timestamp=datetime.utcnow()
        )
        db.add(db_chat)
        db.commit()
        
        return {"answer": answer_text, "sources": sources_list}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))