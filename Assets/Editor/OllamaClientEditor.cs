using UnityEngine;
using UnityEditor;
using System.Collections.Generic;

[CustomEditor(typeof(OllamaClient))]
public class OllamaClientEditor : Editor
{
    private string _systemMessage = "마법 왕국의 현자이자 마법 도서관의 수호자 마법사 입니다.";
    private string _userMessage = "안녕하세요. 저는 방랑검객 잭입니다.";

    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        var client = (OllamaClient)target;

        //입력필드 표시
        _systemMessage = EditorGUILayout.TextField("System Message", _systemMessage);
        _userMessage = EditorGUILayout.TextField("User Message", _userMessage);

        if (!EditorApplication.isPlaying)
        {
            EditorGUILayout.HelpBox(
                "Ollama 요청은 Play 모드에서 실행할 수 있습니다.",
                MessageType.Info);
        }

        using (new EditorGUI.DisabledScope(!EditorApplication.isPlaying))
        {
            if (GUILayout.Button("요청 보내기"))
            {
                var messages = new List<OllamaMessage>
                {
                    new OllamaMessage { role = "system", content = _systemMessage },
                    new OllamaMessage { role = "user", content = _userMessage }
                };

                client.SendChat(messages);
            }
        }
    }
}
