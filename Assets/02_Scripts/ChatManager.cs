using System.Collections.Generic;
using UnityEngine;
using TMPro;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public enum NpcType
{
    wizard,
    guard,
    blacksmith
}


// NPC 페르소나 로딩 -> 대화 히스토리 관리 -> UI 갱신
public class ChatManager : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI _npcNameText;
    [SerializeField] private TextMeshProUGUI _npcDialogText;
    [SerializeField] private TMP_InputField _userInputField;
    [SerializeField] private Button _sendButton;
    [SerializeField] private NpcType _npcType;
    
    private OllamaClient _ollamaClient;
    private NpcPersona _npcPersona;
    
    // 대화 히스토리 관리를 위한 컬렉션
    public List<OllamaMessage> _history = new();

    private void Awake()
    {
        EnsureEventSystem();

        _ollamaClient = GetComponent<OllamaClient>();
        if (_ollamaClient == null)
            _ollamaClient = FindAnyObjectByType<OllamaClient>();

        LoadPersona();
    }

    private static void EnsureEventSystem()
    {
        if (EventSystem.current != null) return;

        var eventSystemObject = new GameObject("EventSystem");
        eventSystemObject.AddComponent<EventSystem>();
        eventSystemObject.AddComponent<StandaloneInputModule>();
    }

    private void OnEnable()
    {
        if (_sendButton != null)
        {
            _sendButton.onClick.AddListener(OnSendButtonClick);
            _userInputField.onSubmit.AddListener( _ => OnSendButtonClick());
            //응답이 수신되었을때 호출되는 이벤트에 연결
            OllamaClient.OnResponseReceived += ResponseHandler;

            OllamaClient.OnTokenReceived +=TokenHandler;

            OllamaClient.OnLoadingChanged += LoadingChangeHandler;
        }
    }

    private void OnDisable()
    {
        if (_sendButton != null)
        {
            _sendButton.onClick.RemoveListener(OnSendButtonClick);
            _userInputField.onSubmit.RemoveAllListeners();
            OllamaClient.OnResponseReceived -= ResponseHandler;
            OllamaClient.OnTokenReceived -=TokenHandler;
            OllamaClient.OnLoadingChanged -= LoadingChangeHandler;
        }
    }
    private void LoadingChangeHandler(bool isLoading)
    {
        if (isLoading)
            _npcDialogText.text = string.Empty;
    }
    private void TokenHandler(string token)
    {
        _npcDialogText.text += token;
    }

    // 페르소나 로딩
    private void LoadPersona()
    {
        TextAsset json = Resources.Load<TextAsset>("WizardPersona");
        // 역직렬화 (json => 객체)
        _npcPersona = JsonUtility.FromJson<NpcPersona>(json.text);
        
        _history.Add(new OllamaMessage
        {
            role = "system",
            content = $"당신의 이름은 {_npcPersona.name} 입니다. " +
                      $"성격 : {_npcPersona.personality} " +
                      $"배경 : {_npcPersona.background} " +
                      $"말투 : {_npcPersona.speechStyle} " +
                      "반드시 캐릭터 성격을 유지하고, 한글로 답하세요."
        });

        _npcNameText.text = _npcPersona.name;
        _npcDialogText.text = _npcPersona.greeting;

    }
    
    private void OnSendButtonClick()
    {
        string userText = _userInputField.text.Trim();
        if (string.IsNullOrEmpty(userText)) return;

        //사용자가 입력한 메시지를 히스토리에 저장 -> 전체 메시지(_history)를 LLM 전송 -> 응답 -> UI갱신
        _history.Add(new OllamaMessage
        {
           role = "user",
           content = userText  
        });

        // UI 전송
        _userInputField.text = string.Empty;
        _npcDialogText.text = "NPC 생각중 ...";
        //메시지 전송 =>LLM
        // _ollamaClient.SendChat(_history);

        _npcNameText.text = _npcType.ToString();
        _ollamaClient.SendToNPC(_npcType.ToString(), userText);
    }

    private void ResponseHandler(string response)
    {
        // 대화 맥락 유지용 히스토리에 추가
        _history.Add(new OllamaMessage
        {
            role = "assistant",
            content = response
        });

        _npcDialogText.text = response;
    }
}
