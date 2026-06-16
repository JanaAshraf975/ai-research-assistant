from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# 1. تحميل موديل الـ Embeddings المطلوب في مشروعكم (all-MiniLM-L6-v2)
# الموديل ده هيشتغل Local بالكامل على جهازك ويحول النصوص لأرقام
# تحميل الموديل وتجبيير تشغيله على الـ CPU لتجنب كراش الويندوز
embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

# 2. إعداد قاعدة بيانات ChromaDB 
# السطر ده هيعمل فولدر اسمه chroma_data جوه مشروعك يحفظ فيه الـ Vectors تلقائياً
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="research_documents")

# 3. دالة لقراءة النص من ملف PDF مرفوع
def extract_text_from_pdf(file_bytes) -> str:
    reader = PdfReader(file_bytes)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

# 4. دالة لتقسيم النص لقطع صغيرة (Chunks)
def split_text_into_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# 5. ✨ الدالة الجديدة لتوليد الـ Embeddings وحفظها في ChromaDB
def save_chunks_to_vector_db(chunks: list[str], document_id: int, filename: str):
    ids = []
    embeddings = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        # عمل ID فريد لكل قطعة (مثلاً: doc_1_chunk_0)
        chunk_id = f"doc_{document_id}_chunk_{i}"
        
        # توليد الـ Vector (مصفوفة الأرقام) اللي بتعبر عن معنى القطعة
        vector = embedding_model.encode(chunk).tolist()
        
        ids.append(chunk_id)
        embeddings.append(vector)
        
        # حفظ بيانات ميتا (Metadata) عشان الـ AI يعرف القطعة دي تابعة لـ أنهي ملف بالإصدار بتاعه
        metadatas.append({
            "document_id": document_id, 
            "filename": filename, 
            "text": chunk
        })
        
    # حفظ البيانات دفعة واحدة في مجموعة ChromaDB
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=chunks
    )# 🔍 دالة البحث الدلالي (Similarity Search) جوه ChromaDB
def search_similar_chunks(query: str, top_k: int = 3):
    # 1. تحويل سؤال المستخدم إلى Vector
    query_vector = embedding_model.encode(query).tolist()
    
    # 2. البحث في ChromaDB
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=['metadatas', 'documents'] # تأكدي إننا بنطلب الـ metadatas والـ documents
    )
    
    # 3. إرجاع النتائج ككائنات تحتوي على النص والـ metadata
    retrieved_items = []
    if results and results['metadatas'] and results['metadatas'][0]:
        for i in range(len(results['metadatas'][0])):
            # إنشاء كائن بسيط (أو NamedTuple) بيجمع النص والـ metadata
            class SearchResult:
                def __init__(self, page_content, metadata):
                    self.page_content = page_content
                    self.metadata = metadata
            
            item = SearchResult(
                page_content=results['documents'][0][i],
                metadata=results['metadatas'][0][i]
            )
            retrieved_items.append(item)
            
    return retrieved_items
