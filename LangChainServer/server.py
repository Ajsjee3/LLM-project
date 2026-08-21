# Qdrant VectorDB
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

em = OllamaEmbeddings(model = "bge-m3")
lore_db = QdrantVectorStore.from_existing_collection(
    embedding=em,
    collection_name="game_lore",
    vector_name="dense",
    url = "http://localhost:6333"
)

# Redis
import hashlib

from langchain_redis import RedisChatMessageHistory
from langchain_core.prompts import MessagesPlaceholder

# Redis 접속 URL
REDIS_URL = "redis://localhost:6379"

#LangChain
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from fastapi import FastAPI # 웹 서버 모듈
from pydantic import BaseModel #json 검증

#FastAPI ===================================================
app = FastAPI()

class NpcChatRequest(BaseModel):
    player_id: str = "player1"
    npc_id: str = "wizard" # wizard/ guard/ blacksmith
    message: str

@app.get("/check")
def check():
    return {"status": "ok"}

@app.post("/npc/chat")
def npc_chat(req: NpcChatRequest):
    npc = persona(req.npc_id)
    history = get_history(req.player_id, req.npc_id)

    # 1) 불러오기 : Redis에서 과거 이력을 로드
    past = history.messages

    # 4) 마법사만 RAG 적용
    if req.npc_id == "wizard":
        #마법사만 도서관 지식을 활용
        docs = retriever.invoke(req.message)
        reply = rag_chain.invoke({
            "context": format_docs(docs),
            "history": past,
            "message": req.message
        })
    else:
        # 2) 호출: 과거 대화 + 이번 질문을 함께 전송
        reply = build_chain(req.npc_id).invoke({"history": past, "message": req.message})

    # 3) 저장 : 이번 대화 내용 Redis 저장
    history.add_user_message(req.message)
    history.add_ai_message(reply)
    return {
        "reply": reply,
        "npc_name": npc["name"]
    }

# Langchain===================================================
llm = ChatOllama(model="gemma4:e2b", temperature=0.7, reasoning=False)

# 페르소나 리턴
def persona(npc_id:str) -> dict:
    return NPC_PERSONAS.get(npc_id, NPC_PERSONAS["wizard"])

# NPC 별로 system 프롬프트를 변경 : 체인을 변경
def build_chain(npc_id:str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", persona(npc_id)["system"]),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{message}"),
    ])
    return prompt | llm | StrOutputParser()

def get_history(player_id: str, npc_id: str) -> RedisChatMessageHistory:
    # RediSearch 쿼리에서 문제가 되는 하이픈 등의 특수문자를 피한다.
    raw_session_id = f"{player_id}:{npc_id}"
    session_id = hashlib.sha256(raw_session_id.encode("utf-8")).hexdigest()

    return RedisChatMessageHistory(
        session_id=session_id,
        redis_url=REDIS_URL,
    )

NPC_PERSONAS = {
    "wizard": {
        "name": "아르카누스",
        "system": "너는 마법 도서관의 수호자 '아르카누스'다. "
                  "300년을 산 엘프 현자이며 '~하네', '~이라네' 말투를 쓴다. "
                  "반드시 캐릭터를 유지하고 한글로 2~3문장 답하라.",
    },
    "guard": {
        "name": "가르드",
        "system": "너는 왕국 근위병 '가르드'다. 무뚝뚝하고 단호한 군인 말투를 쓴다. "
                  "'~하시오', '~이오' 같은 어미를 쓴다. 한글로 2문장 이내로 짧게 답하라.",
    },
    "blacksmith": {
        "name": "브론",
        "system": "너는 대장장이 '브론'이다. 거칠지만 정 많은 장인 말투를 쓴다. "
                  "'~라고', '~지' 같은 반말 섞인 어미를 쓴다. 한글로 2문장 이내로 답하라.",
    },
}

# RAG ======================================================
retriever = lore_db.as_retriever(search_kwargs={"k": 2})

# 마법사 전용 프롬프트 = 기존 페르소나 + RAG + 지난 대화
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", persona("wizard")["system"] + "\n"
     "세계관 질문은 아래 [도서관 지식]을 근거로 답하시오. "
     "플레이어가 이전에 말한 이름이나 정보는 [대화 이력]을 기억하여 답하시오. "
     "두 근거 어디에도 없는 내용은 모른다고 답하시오.\n"
     "[도서관 지식]\n{context}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{message}"),
])

#검색된 조각을 문자열
def format_docs(docs):
    return "\n".join(d.page_content for d in docs)

# 마법사 전용 LangChain
rag_chain = rag_prompt | llm | StrOutputParser()
