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
