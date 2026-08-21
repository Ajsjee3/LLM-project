from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter


LORE_PATH = Path(__file__).with_name("lore.md")

if not LORE_PATH.exists() or not LORE_PATH.read_text(encoding="utf-8").strip():
    raise FileNotFoundError(
        f"세계관 내용이 있는 lore.md 파일이 필요합니다: {LORE_PATH}"
    )

# 1) 로어 파일 로딩
docs = TextLoader(str(LORE_PATH), encoding="utf-8").load()

# 2) 청크 단위로 분리
splitter = RecursiveCharacterTextSplitter(
    chunk_size=60,
    chunk_overlap=0,
    separators=["\n"],
)
chunks = splitter.split_documents(docs)

# 3) 임베딩 모델 적용
embedding = OllamaEmbeddings(model="bge-m3")

# 4) Qdrant에 저장
QdrantVectorStore.from_documents(
    chunks,
    embedding=embedding,
    url="http://localhost:6333",
    collection_name="game_lore",
    force_recreate=True,
)

print(f"인덱싱 완료: {len(chunks)}개 조각")
