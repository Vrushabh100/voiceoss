import requests, json

# ============================================================
# DAY 8 — Test Ollama API connection and JSON intent parsing
# ============================================================

def ask_ollama(prompt, model='llama3'):
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': model, 'prompt': prompt, 'stream': False},
            timeout=60
        )
        return response.json()['response']
    except Exception as e:
        print(f'Ollama error: {e}')
        return ''

# Test 1 — basic connection
print('=' * 50)
print('TEST 1 — Basic Ollama connection')
print('=' * 50)
result = ask_ollama('Say hello in one word')
print(f'Response: {result}')
print()

# Test 2 — JSON intent extraction
SYSTEM_PROMPT = '''You are a Windows voice assistant command parser.
Convert the user command into JSON only. No explanation. No extra text.
Output format: {"action": "ACTION", "target": "TARGET", "params": {}}
Actions: open_app, close_app, open_file, move_file, delete_file,
type_text, take_screenshot, search_web, set_volume, shutdown,
create_folder, open_website, run_command, minimize_window'''

def parse_command(text):
    prompt = f"{SYSTEM_PROMPT}\n\nUser command: {text}\nJSON:"
    raw = ask_ollama(prompt)
    print(f'Raw response: {raw}')
    try:
        start = raw.find('{')
        end = raw.rfind('}') + 1
        return json.loads(raw[start:end])
    except Exception as e:
        print(f'Parse error: {e}')
        return {'action': 'unknown', 'target': text, 'params': {}}

print('=' * 50)
print('TEST 2 — JSON intent extraction')
print('=' * 50)
tests = ['open chrome', 'take a screenshot', 'create folder named projects']
for t in tests:
    print(f'Input:  {t}')
    print(f'Output: {parse_command(t)}')
    print()
