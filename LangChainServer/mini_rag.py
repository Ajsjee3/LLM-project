from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

em = OllamaEmbeddings(model ="bge-m3")

db = QdrantVectorStore.from_existing_collection(
    embedding= em,
    collection_name="game_lore",
    vector_name="dense",
    url = "http://localhost:6333"
)

hits = db.similarity_search("북쪽에는 뭐가 있어?", k=2)

for i, h in enumerate(hits):
    print(f"[{i}] {h.page_content}")
