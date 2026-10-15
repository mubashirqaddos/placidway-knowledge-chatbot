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


def test_rewrite_outage_still_searches_sources_with_history():
    from src.llm import ServiceUnavailable

    class UnavailableProvider:
        def generate(self, *args, **kwargs):
            raise ServiceUnavailable('http_503')

    assistant = Bot(Retriever(load_index(), use_vectors=False), UnavailableProvider())
    answer = assistant.answer(
        'Is alternative medicine cheaper in Mexico or Turkey?',
        [{'role': 'user', 'content': 'Tell me about the clinic.'}],
    )
    assert answer.status == 'not_found'
    assert answer.mode == 'extractive_fallback'
    assert answer.sources and 'search-medical-pricings' in answer.sources[0]['url']
    assert 'like-for-like' in answer.text


def test_rewrite_outage_preserves_followup_subject_and_price():
    from src.llm import ServiceUnavailable

    class UnavailableProvider:
        def generate(self, *args, **kwargs):
            raise ServiceUnavailable('http_503')

    assistant = Bot(Retriever(load_index(), use_vectors=False), UnavailableProvider())
    answer = assistant.answer(
        'And what does it cost?',
        [{'role': 'user', 'content': 'Tell me about the Adrenal package.'}],
    )
    assert answer.status == 'answered'
    assert 'adrenal' in answer.resolved_question.lower()
    evidence = ' '.join(e['quote'] for e in answer.evidence)
    assert '18,995' in evidence and 'USD' in evidence


def test_new_package_inclusions_cannot_be_rewritten_to_previous_adrenal_price():
    import json

    class CheckingProvider:
        def generate(self, system, prompt, schema, *args):
            # The old path requested a rewrite and could change both disease and
            # intent to match the preceding cost question.
            assert 'question' not in schema['properties']
            context = json.loads(prompt)['CONTEXT']
            assert len(context) == 2
            assert all(c['id'].startswith('adenocarcinoma-') and 'Included in' in c['heading'] for c in context)
            return {'status': 'answered', 'used_chunk_ids': [c['id'] for c in context],
                    'claims': [{'text': c['heading'], 'quote': c['text'], 'chunk_id': c['id']} for c in context]}

    assistant = Bot(Retriever(load_index(), use_vectors=False), CheckingProvider())
    answer = assistant.answer('What is included in the Adenocarcinoma package?',
                              [{'role': 'user', 'content': 'How much does Adrenal Cancer treatment cost in Tijuana?'}])
    assert answer.status == 'answered' and answer.mode == 'gemini'
    assert all('/7903/' in s['url'] for s in answer.sources)
    assert 'In-Patient' in answer.text and 'Out-Patient' in answer.text
    assert any('Medical Supervision' in e['quote'] for e in answer.evidence)


def test_comparison_after_two_packages_uses_comparison_source_without_rewrite():
    import json

    class CheckingProvider:
        def generate(self, system, prompt, schema, *args):
            assert 'question' not in schema['properties']
            context = json.loads(prompt)['CONTEXT']
            assert context and all(c['id'].startswith('comparison-') for c in context)
            return {'status': 'not_found', 'used_chunk_ids': [], 'claims': []}

    assistant = Bot(Retriever(load_index(), use_vectors=False), CheckingProvider())
    answer = assistant.answer('Is alternative medicine cheaper in Mexico or Turkey?', [
        {'role': 'user', 'content': 'How much does Adrenal Cancer treatment cost in Tijuana?'},
        {'role': 'user', 'content': 'What is included in the Adenocarcinoma package?'},
    ])
    assert answer.status == 'not_found'
    assert 'like-for-like' in answer.text
    assert all('search-medical-pricings' in s['url'] for s in answer.sources)
    assert answer.resolved_question == 'Is alternative medicine cheaper in Mexico or Turkey?'


def test_translation_cannot_replace_explicit_package_with_previous_subject():
    from src.llm import ServiceUnavailable

    class WrongTranslator:
        def generate(self, system, prompt, schema, *args):
            if 'question' in schema['properties']:
                assert 'previous_user_questions' not in prompt
                return {'question': 'What does adrenal treatment cost?'}
            raise ServiceUnavailable('http_503')

    assistant = Bot(Retriever(load_index(), use_vectors=False), WrongTranslator())
    answer = assistant.answer('Qué incluye el paquete Adenocarcinoma?', [
        {'role': 'user', 'content': 'How much does adrenal treatment cost?'}])
    assert 'Adenocarcinoma' in answer.resolved_question
    # If the untranslated query has insufficient lexical overlap, an honest
    # unknown/contact response is allowed; the previous package is never used.
    assert all('/7902/' not in s['url'] for s in answer.sources)
    assert 'adrenal' not in answer.resolved_question.lower()


def test_fresh_recovery_followup_stays_with_new_package_after_switch():
    history = [
        {'role': 'user', 'content': 'How much does Adrenal Cancer treatment cost in Tijuana?'},
        {'role': 'user', 'content': 'What is included in the Adenocarcinoma package?'},
    ]
    answer = bot().answer('And what about recovery time?', history)
    assert answer.status == 'not_found'
    assert 'adenocarcinoma' in answer.resolved_question
    assert all('/7903/' in s['url'] for s in answer.sources)
