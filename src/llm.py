"""Gemini REST client; bounded retries, JSON schema, no search tools or paid fallback."""
import json
import re
import time
import requests


class ServiceUnavailable(RuntimeError):
    def __init__(self, reason='provider_error'):
        # Safe diagnostic category only; never put a provider response or key here.
        self.reason = reason
        super().__init__('Service temporarily unavailable.')


class Gemini:
    def __init__(self, api_key, model):
        if not re.fullmatch(r'gemini-[a-zA-Z0-9.\-]+', model):
            raise ValueError('Invalid Gemini model name.')
        self.key, self.model = api_key, model

    def generate(self, system, prompt, schema, max_tokens=4096):
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent'
        body = {
            'systemInstruction': {'parts': [{'text': system}]},
            'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': 0, 'maxOutputTokens': max_tokens,
                'responseMimeType': 'application/json', 'responseJsonSchema': schema,
            },
        }
        for attempt in range(2):
            try:
                response = requests.post(url, headers={'x-goog-api-key': self.key}, json=body, timeout=(5, 18))
                if response.status_code in (429, 500, 502, 503, 504) and attempt < 1:
                    try:
                        delay = min(8, max(1, float(response.headers.get('Retry-After', 2 ** attempt))))
                    except ValueError:
                        delay = 2 ** attempt
                    time.sleep(delay)
                    continue
                if response.status_code != 200:
                    raise ServiceUnavailable(f'http_{response.status_code}')
                result = response.json()
                candidate = result.get('candidates', [{}])[0]
                if candidate.get('finishReason') not in (None, 'STOP'):
                    raise ServiceUnavailable('incomplete_response')
                text = ''.join(p.get('text', '') for p in candidate.get('content', {}).get('parts', []) if not p.get('thought'))
                return json.loads(text)
            except (requests.RequestException, ValueError, KeyError, IndexError) as exc:
                # Do not log provider responses or exception URLs/headers containing secrets.
                raise ServiceUnavailable('invalid_or_unreachable_response') from exc
        raise ServiceUnavailable('retry_limit')
