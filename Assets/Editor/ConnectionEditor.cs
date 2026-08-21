using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(Connection))]
public class ConnectionEditor : Editor
{
    public override void OnInspectorGUI()
    {
        // 기본 UI는 드로잉
        DrawDefaultInspector();
        // 접근할 대상 클래스 할당
        var connection = (Connection)target;
        // 버튼 생성
        if (!EditorApplication.isPlaying)
        {
            EditorGUILayout.HelpBox(
                "연결 테스트는 Play 모드에서 실행할 수 있습니다.",
                MessageType.Info);
        }

        using (new EditorGUI.DisabledScope(!EditorApplication.isPlaying))
        {
            if (GUILayout.Button("연결 테스트"))
            {
                // Connection 클래스의 OllamaConnect 루틴호출
                connection.StartCoroutine(connection.OllamaConnect());
            }
        }
    }
}
