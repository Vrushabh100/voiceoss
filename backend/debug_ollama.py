import requests

def ask_ollama(prompt):
    resp = requests.post(
        'http://localhost:11434/api/generate',
        json={'model': 'llama3', 'prompt': prompt, 'stream': False},
        timeout=60
    )
    return resp.json()['response']

prompt = '''You are a Windows command parser.
Reply ONLY with this exact JSON, no other text:
{"action": "open_app", "target": "chrome", "params": {}}

User: open chrome
JSON:'''

result = ask_ollama(prompt)
print('RAW OUTPUT:')
print(repr(result))
print()
print('VISIBLE:')
print(result)
