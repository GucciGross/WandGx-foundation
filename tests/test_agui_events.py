from agui_runtime import make_text_stream_events


def test_agui_text_stream_events_have_lifecycle():
    events = make_text_stream_events("hello world", thread_id="thread_test", run_id="run_test")
    assert events[0]["type"] == "RUN_STARTED"
    assert events[-1]["type"] == "RUN_FINISHED"
    assert any(event["type"] == "TEXT_MESSAGE_CONTENT" for event in events)
