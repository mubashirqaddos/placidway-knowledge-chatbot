"""Run with: streamlit run app.py."""
import hmac
import os
from dataclasses import asdict
from datetime import datetime, timezone
from urllib.parse import quote

import streamlit as st

from src.answering import Bot
from src.config import GEMINI_MODEL, INDEX, MAX_QUESTION_CHARS, SOURCES
from src.guardrails import message
from src.knowledge import load_index, refresh
from src.llm import Gemini
from src.logging_hooks import log_unanswered
from src.retrieval import Retriever

st.set_page_config(page_title='PlacidWay | Website Knowledge Assistant', page_icon='💬', layout='centered')


def setting(name, default=''):
    try:
        value = st.secrets.get(name, os.environ.get(name, default))
    except Exception:
        value = os.environ.get(name, default)
    return str(value).strip()


@st.cache_resource
def get_retriever(index_revision):
    return Retriever(load_index())


def render_answer(answer):
    # Model/source text is plain text; only verified metadata supplies clickable URLs.
    st.write(answer['text'])
    for evidence in answer.get('evidence', []):
        st.caption(evidence['heading'])
        with st.container(border=True):
            st.text(evidence['quote'])
    if answer.get('sources'):
        st.caption('Sources')
        for source in answer['sources']:
            st.link_button(source['title'], source['url'])


st.markdown('### PlacidWay')
st.title('Ask about your care journey')
st.caption('Published package details, clinic information and prices — with links to the original pages.')

if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.disclaimer_shown = False

with st.sidebar:
    st.markdown('### Website knowledge assistant')
    st.write('Answers are limited to the seven pages provided for this assessment.')
    if INDEX.exists():
        try:
            snapshot = load_index()
            stamp = datetime.fromisoformat(snapshot['refreshed_at'])
            st.caption('Last refreshed: ' + stamp.astimezone(timezone.utc).strftime('%d %b %Y, %H:%M UTC'))
            st.caption(f"{len(snapshot['pages'])} sources · {len(snapshot['chunks'])} passages")
        except Exception:
            st.warning('Knowledge base needs a refresh.')
    else:
        st.caption('Knowledge base not built yet.')
    st.divider()
    st.markdown('**Try a question**')
    examples = [
        'How much does Adrenal Cancer treatment cost in Tijuana?',
        'What is included in the Adenocarcinoma package?',
        'Is alternative medicine cheaper in Mexico or Turkey?',
        'Can you book me an appointment tomorrow?',
    ]
    for i, example in enumerate(examples):
        if st.button(example, key=f'example_{i}', use_container_width=True):
            st.session_state.pending_question = example
    if st.button('Clear conversation', use_container_width=True):
        st.session_state.messages = []
        st.session_state.disclaimer_shown = False
        st.session_state.pop('quote_draft', None)
        st.rerun()
    with st.expander('Knowledge base admin'):
        token = st.text_input('Admin token', type='password', key='admin_input', autocomplete='off')
        admin = setting('ADMIN_TOKEN')
        if st.button('Refresh Knowledge Base', disabled=not admin):
            if not token or not hmac.compare_digest(token, admin):
                st.error('Invalid admin token.')
            else:
                try:
                    with st.spinner('Refreshing the seven source pages…'):
                        refresh()
                    get_retriever.clear()
                    st.success('Knowledge base refreshed.')
                    st.rerun()
                except Exception:
                    st.error('Refresh could not be completed. The previous knowledge base is still available.')
        if not admin:
            st.caption('Owner: set ADMIN_TOKEN in secrets to enable refresh. CLI refresh is also available.')

if not INDEX.exists():
    try:
        with st.spinner('Preparing the seven-page knowledge base…'):
            refresh()
    except Exception:
        st.error('Service temporarily unavailable. The knowledge base could not be prepared. Please try again later.')
        st.stop()

api_key = setting('GEMINI_API_KEY')
if not api_key:
    st.info('Source excerpt mode: replies quote the provided pages. The owner can enable AI summaries in server secrets.')

for turn in st.session_state.messages:
    with st.chat_message(turn['role']):
        if turn['role'] == 'assistant':
            render_answer(turn['answer'])
            if turn.get('disclaimer'):
                st.caption(turn['disclaimer'])
        else:
            st.write(turn['content'])

question = st.chat_input('Ask about a treatment, package or price', max_chars=MAX_QUESTION_CHARS)
question = st.session_state.pop('pending_question', None) or question
if question:
    history = [{'role':t['role'], 'content':t['content']} for t in st.session_state.messages]
    st.session_state.messages.append({'role':'user', 'content':question})
    with st.chat_message('user'):
        st.write(question)
    with st.chat_message('assistant'):
        with st.spinner('Checking the provided pages…'):
            try:
                retriever = get_retriever(INDEX.stat().st_mtime_ns)
                llm = Gemini(api_key, setting('GEMINI_MODEL', GEMINI_MODEL)) if api_key else None
                result = Bot(retriever, llm).answer(question, history)
            except Exception:
                from src.answering import Answer
                result = Answer('unavailable', message('unavailable'))
        answer = asdict(result)
        render_answer(answer)
        disclaimer = ''
        if result.status in ('answered', 'medical') and not st.session_state.disclaimer_shown:
            disclaimer = message('disclaimer', result.language)
            st.caption(disclaimer)
            st.session_state.disclaimer_shown = True
        st.session_state.messages.append({'role':'assistant', 'content':result.text, 'answer':answer, 'disclaimer':disclaimer})
        log_unanswered(question, result)

show_quote = any(t.get('answer', {}).get('quote_intent') for t in st.session_state.messages[-2:])
if show_quote:
    with st.expander('Want a free quote?', expanded=True):
        st.write('Use the quote form on the PlacidWay page, or prepare a request below.')
        st.link_button('Open PlacidWay quote form', SOURCES[0].url)
        with st.form('quote_request', clear_on_submit=False):
            name = st.text_input('Name', max_chars=100)
            email = st.text_input('Email', max_chars=254)
            consent = st.checkbox('Use these details only to prepare my quote request.')
            submitted = st.form_submit_button('Prepare quote request')
            if submitted:
                import re
                if not consent or not name.strip() or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
                    st.warning('Enter a name, valid email and consent to prepare your request.')
                else:
                    st.session_state.quote_draft = f'Free quote request\nName: {name.strip()}\nEmail: {email.strip()}\nPlease contact me about the ITC treatment options listed on PlacidWay.\nSource: {SOURCES[0].url}\n'
        if st.session_state.get('quote_draft'):
            st.info('Your draft is ready. It has not been sent. Submit it through PlacidWay to request a quote.')
            st.download_button('Download request draft', st.session_state.quote_draft, 'quote-request.txt', mime='text/plain')
            contact = setting('CONTACT_EMAIL')
            if contact and __import__('re').fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', contact):
                st.link_button('Open email draft', 'mailto:' + quote(contact, safe='@.') + '?subject=Free%20quote%20request&body=' + quote(st.session_state.quote_draft))

st.caption('For questions about your personal medical condition, please speak with a qualified doctor.')
