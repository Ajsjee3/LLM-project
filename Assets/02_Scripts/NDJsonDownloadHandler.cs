using UnityEngine;
using System;
using System.Text;
using UnityEngine.Networking;

// NDJson이 스트리밍 응답을 처리하는 역할
public class NDJsonDownloadHandler : DownloadHandlerScript
{
 //토큰 (청크) 단위로 호출할 이벤트 선언
    private readonly Action <string> _onToken;
    //\n 종료되지 않은 json토콜을 임시 저장할 계획 
    private readonly StringBuilder _lineBuffer = new();
    // 스트리밍중에 수신한 모든 토클을 순서대로 이어 붙이는 버퍼;
    
    private readonly StringBuilder _fullBuffer = new();
    //스트리밍 완료후 전체응답텍스트(프로퍼티)
    public string FullBuffer => _fullBuffer.ToString();
    
    //생성자
    public NDJsonDownloadHandler(Action<string> onToken) : base(new byte[8192])
    {
        _onToken = onToken;
    }

    //새 데이터(청크)가 도착할 때 마다 자동으로 호출되는 콜백
    protected override bool ReceiveData(byte[] data, int dataLength)
    {
        //1. 수신된 바이트를 utf-8 문자열로 디코딩
        string buffer = Encoding.UTF8.GetString(data, 0, dataLength);

        //2. 이전 청크에서 남은 불완전 조각을 이어 붙임
        _lineBuffer.Append(buffer);

        string[] lines = _lineBuffer.ToString().Split('\n');
        //3. 마지막 원소는 불완전한 조각으로 판정 => _lineBuffer 에 추가
        _lineBuffer.Clear();
        _lineBuffer.Append(lines[lines.Length - 1]);

        //4. 완전한 청크들만 파싱
        for (int i=0; i < lines.Length - 1; i++)
        {
            string line = lines[i];
            if (string.IsNullOrWhiteSpace(line)) continue;

            // 역직렬화 처리
            var res = JsonUtility.FromJson<OllamaResponse>(line);
            // 역직렬화 후에 NULL 체크
            if (res?.message == null) continue;

            _fullBuffer.Append(res.message.content);
            _onToken?.Invoke(res.message.content);
        }
        return true;
    }
    
} 
