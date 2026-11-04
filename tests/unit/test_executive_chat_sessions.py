"""Per-session conversation isolation for ExecutiveChatAgent."""

from agents.executive_chat import MAX_HISTORY_PER_SESSION, MAX_SESSIONS, ExecutiveChatAgent


def test_sessions_are_isolated():
    agent = ExecutiveChatAgent()
    agent.chat("hello", session_id="a")
    agent.chat("hello", session_id="b")
    agent.chat("again", session_id="b")
    assert len(agent.get_conversation_history("a")) == 2
    assert len(agent.get_conversation_history("b")) == 4


def test_reset_only_affects_own_session():
    agent = ExecutiveChatAgent()
    agent.chat("hello", session_id="a")
    agent.chat("hello", session_id="b")
    agent.reset_conversation("a")
    assert agent.get_conversation_history("a") == []
    assert len(agent.get_conversation_history("b")) == 2


def test_history_per_session_is_capped():
    agent = ExecutiveChatAgent()
    for i in range(MAX_HISTORY_PER_SESSION):
        agent.chat(f"m{i}", session_id="a")
    assert len(agent.get_conversation_history("a")) == MAX_HISTORY_PER_SESSION


def test_session_count_is_capped():
    agent = ExecutiveChatAgent()
    for i in range(MAX_SESSIONS + 5):
        agent.chat("hi", session_id=f"s{i}")
    assert agent.session_count() == MAX_SESSIONS
    assert agent.get_conversation_history("s0") == []  # oldest evicted


def test_api_reset_does_not_wipe_other_callers(api_client, monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH", "true")
    monkeypatch.setenv("FRAMEWORK_API_KEYS", "k-a:sales,k-b:marketing")
    from api_server import executive_chat_agent
    api_client.post("/chat", json={"message": "hi"}, headers={"X-API-Key": "k-b"})
    before = executive_chat_agent.session_count()
    api_client.post("/chat/reset", headers={"X-API-Key": "k-a"})
    assert executive_chat_agent.session_count() == before
