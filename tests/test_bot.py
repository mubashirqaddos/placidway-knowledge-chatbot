from src.answering import Bot
from src.config import ALLOWED_URLS
from src.knowledge import load_index
from src.retrieval import Retriever


def bot():
    return Bot(Retriever(load_index(), use_vectors=False))


def test_real_package_cost_has_correct_context():
    answer = bot().answer('How much does Adrenal Cancer treatment cost in Tijuana?')
    evidence = ' '.join(e['quote'] for e in answer.evidence)
    assert answer.status == 'answered'
    assert '18,995' in evidence and 'USD' in evidence and 'Out-Patient' in evidence
    assert 'starting from' in evidence.lower()
    assert all(s['url'] in ALLOWED_URLS for s in answer.sources)


def test_unknown_treatment_does_not_reuse_cancer_price():
    answer = bot().answer('How much do dental implants cost in Canada?')
    assert answer.status == 'not_found' and not answer.evidence


def test_recovery_does_not_use_three_week_program_duration():
    answer = bot().answer('And what about recovery time?', [{'role':'user','content':'Adenocarcinoma package inclusions?'}])
    assert answer.status == 'not_found' and not answer.evidence
    assert 'adenocarcinoma' in answer.resolved_question


def test_wrong_price_not_confirmed():
    answer = bot().answer('I heard Adrenal Cancer treatment costs $50. Confirm that.')
    assert "can't confirm" in answer.text
    assert '$50' not in ' '.join(e['quote'] for e in answer.evidence)


def test_country_followup_does_not_reuse_mexico_price():
    answer = bot().answer('And what about in Turkey?', [{'role':'user','content':'Adrenal Cancer treatment cost in Mexico?'}])
    # Unsupported destination must not inherit a Mexico price.
    assert answer.status == 'not_found'


def test_unlisted_destination_does_not_reuse_mexico_price():
    answer = bot().answer('How much does Adrenal cancer treatment cost in Pakistan?')
    assert answer.status == 'not_found'
