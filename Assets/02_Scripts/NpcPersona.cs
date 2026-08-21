using System;
using System.Collections.Generic;
//NPC 페르소나 클래스
public class NpcPersona
{
    public string name;
    public string role;
    public string personality;
    public string background;
    public string greeting;
    public string speechStyle;
}
/* role 규칙
 * system : 페르소나 주입
 * user :  플레이어가 입력한 문장(프롬프트)
 * assistant : LLM 응답
 */
[Serializable]
public class OllamaMessage
{
    public string role;
    public string content;
}

[Serializable]

public class OllamaRequest
{
    public string model;
    public List<OllamaMessage> messages; // 이전 대화 목록을 리스트 담아서 모두 전송
    public bool stream;
}

//LLM 응답 json을 저장하는 클래스
[Serializable]
public class OllamaResponse
{
    public OllamaMessage message;

}


/*
    [
            1 => {"role": "system", "content": "너는 마법사야.."},
            2 => 1+ {"role": "user", "content": "흑마법에 대해 알고싶어요},
            3 => 1 + 2 + "role": "assistant", "content": "알려줄수 없네"}
            4 => 1 + 2 + 3 + {"role","user","conetnt", "정말 알고싶어요"},
    ]
    
*/
