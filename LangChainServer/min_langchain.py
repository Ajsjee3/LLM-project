#ChatOllama : LangChain 편하게 사용할수 있는 채팅 래퍼
from langchain_ollama import ChatOllama 
# 프롬프트를 쉽게 만들수 있는 템플릿
from langchain_core.prompts import ChatPromptTemplate
# content 영역만 추출하는 출력 파서
from langchain_core.output_parsers import StrOutputParser 

# 1) 모델 (gemma4:e2b) 로드
llm = ChatOllama(model = " gemma4:e2b", temperature=0.7)

# 2) 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 RPG게임의 대장장이야. 무뚝뚝한 성격의 소유자야."),
    ("human","{topic} 을  구하고 싶어")    
])

# 3) 파이프로 체인을 구성 : 프롬프트 -> LLM -> 응답메시지
chain = prompt | llm | StrOutputParser()

# 4) 실행
result = chain.invoke({"topic" : "전설의 검"})

print(result)
