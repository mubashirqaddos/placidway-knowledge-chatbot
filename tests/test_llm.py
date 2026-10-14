import pytest
import requests
from src.llm import Gemini, ServiceUnavailable


def test_provider_timeout_does_not_expose_credentials(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.ReadTimeout('provider-detail-that-must-not-be-shown')
    monkeypatch.setattr(requests, 'post', fail)
    with pytest.raises(ServiceUnavailable) as exc:
        Gemini('synthetic-private-key', 'gemini-3.1-flash-lite').generate('system', 'question', {})
    assert str(exc.value) == 'Service temporarily unavailable.'
    assert 'synthetic-private-key' not in str(exc.value)
    assert 'provider-detail' not in str(exc.value)


def test_transient_failure_recovers_with_bounded_retry(monkeypatch):
    class Response:
        headers = {}
        def __init__(self, status): self.status_code = status
        def json(self):
            return {'candidates':[{'finishReason':'STOP', 'content':{'parts':[{'text':'{"status":"not_found"}'}]}}]}
    responses = iter([Response(503), Response(200)])
    monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: next(responses))
    waits = []
    monkeypatch.setattr('src.llm.time.sleep', waits.append)
    result = Gemini('synthetic-key','gemini-3.1-flash-lite').generate('system','question',{})
    assert result == {'status':'not_found'} and len(waits) == 1


def test_persistent_failure_stops_retrying(monkeypatch):
    class Response:
        status_code = 503
        headers = {}
    calls = []
    def fail(*args, **kwargs):
        calls.append(1)
        return Response()
    monkeypatch.setattr(requests, 'post', fail)
    monkeypatch.setattr('src.llm.time.sleep', lambda *args: None)
    with pytest.raises(ServiceUnavailable):
        Gemini('synthetic-key','gemini-3.1-flash-lite').generate('system','question',{})
    assert len(calls) == 2
