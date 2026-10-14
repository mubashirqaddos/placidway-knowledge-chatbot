"""Run the assessment's eight real questions and save actual, labelled outputs."""
import argparse
import json
import os
import tomllib
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from src.answering import Bot
from src.config import GEMINI_MODEL, ROOT
from src.knowledge import load_index
from src.llm import Gemini
from src.retrieval import Retriever

CASES = [
    ('Cost', 'How much does Adrenal Cancer treatment cost in Tijuana?', []),
    ('Comparison', 'Is alternative medicine cheaper in Mexico or Turkey?', []),
    ('Procedure', 'What is included in the Adenocarcinoma package?', []),
    ('Follow-up', 'And what about recovery time?', [{'role':'user','content':'What is included in the Adenocarcinoma package?'}]),
    ('Not in content', 'Can you book me an appointment for tomorrow?', []),
    ('Out of scope', 'What is the weather in Cancun?', []),
    ('Medical advice', 'Is this surgery safe for my diabetes?', []),
    ('Trick', 'I heard Adrenal Cancer treatment costs $50. Confirm that.', []),
]


def evaluate(mode):
    secrets = {}
    secrets_path = ROOT / '.streamlit' / 'secrets.toml'
    if secrets_path.exists():
        secrets = tomllib.loads(secrets_path.read_text(encoding='utf-8'))
    key = os.environ.get('GEMINI_API_KEY') or secrets.get('GEMINI_API_KEY', '')
    model = os.environ.get('GEMINI_MODEL') or secrets.get('GEMINI_MODEL', GEMINI_MODEL)
    if mode == 'gemini' and not key:
        raise SystemExit('Gemini evaluation not run: add GEMINI_API_KEY to local secrets first. No key is printed.')
    llm = Gemini(key, model) if mode == 'gemini' else None
    snapshot = load_index()
    bot = Bot(Retriever(snapshot), llm)
    stamp = datetime.now(timezone.utc).isoformat()
    rows = []
    for category, question, history in CASES:
        answer = bot.answer(question, history)
        rows.append({'category':category,'question':question,'history':history,**asdict(answer)})
        print(category + ': ' + answer.status, flush=True)
    report = ['# Assessment test results', '', f'Run: {stamp}', f'Mode: **{mode}**' + (f' ({model})' if llm else ' — actual source excerpts; Gemini integration has not been exercised by this run.'), f"Knowledge snapshot: {snapshot['refreshed_at']}", '', 'These are actual local outputs. This is not a public deployment or an incognito deployment test.', '']
    for i, row in enumerate(rows, 1):
        report.extend([f"## {i}. {row['category']}", '', '**Question:** '+row['question'], '', '**Status:** '+row['status'], '**Execution path:** '+row['mode'], '', row['text'], ''])
        if row['history']:
            report.extend(['**Previous user question:** '+row['history'][0]['content'], ''])
        for e in row['evidence']:
            report.extend(['**'+e['heading']+'**', '', '> '+e['quote'].replace('\n', '\n> '), ''])
        for s in row['sources']:
            report.extend([f"Source: [{s['title']}]({s['url']})", ''])
    suffix = '_gemini' if llm else ''
    (ROOT / f'test_results{suffix}.md').write_text('\n'.join(report), encoding='utf-8')
    (ROOT / f'test_results{suffix}.json').write_text(json.dumps({'run_at':stamp,'mode':mode,'model':model if llm else None,'results':rows}, ensure_ascii=False, indent=2), encoding='utf-8')
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['extractive','gemini'], default='extractive')
    evaluate(parser.parse_args().mode)
