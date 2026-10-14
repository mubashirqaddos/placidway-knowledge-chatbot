from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def app():
    instance = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)
    # UI smoke tests do not consume API quota.
    instance.secrets['GEMINI_API_KEY'] = ''
    instance.secrets['ADMIN_TOKEN'] = 'test-admin'
    return instance.run()


def test_page_and_actual_cost_question():
    at = app()
    assert not at.exception
    assert at.title[0].value == 'Ask about your care journey'
    at.chat_input[0].set_value('How much does Adrenal Cancer treatment cost in Tijuana?').run()
    assert not at.exception
    messages = at.session_state['messages']
    assert messages[-1]['answer']['status'] == 'answered'
    assert messages[-1]['answer']['sources']


def test_medical_route_and_single_session_disclaimer():
    at = app()
    at.chat_input[0].set_value('Is this safe for my diabetes?').run()
    assert not at.exception
    assert at.session_state['messages'][-1]['answer']['status'] == 'medical'
    assert at.session_state['disclaimer_shown']
    at.chat_input[0].set_value('Is this safe for my condition?').run()
    assert not at.exception
    assert not at.session_state['messages'][-1]['disclaimer']
