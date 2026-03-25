from voice_pipeline import get_pipeline
import requests

def handle_command(text):
    print(f'Heard: {text}')
    resp = requests.post('http://127.0.0.1:8000/voice_command', json={'text': text})
    data = resp.json()
    print(f'Full response: {data}')
    if 'intent' in data:
        print(f'Intent: {data["intent"]}')
        print(f'Result: {data["result"]}')
    else:
        print(f'Error: {data}')
    print('---')

print('Pipeline test started.')
print('Make sure FastAPI is running in another terminal.')
print()

pipeline = get_pipeline()
pipeline.start(handle_command)

import time
while pipeline.running:
    time.sleep(0.5)