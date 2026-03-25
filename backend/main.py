from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from intent_parser import parse_command
from memory import CommandMemory
from executor import execute, execute_workflow
from permissions import (get_startup_apps, get_running_processes,
                         get_disk_usage, kill_process,
                         disable_startup_app, is_admin)
import uvicorn

app = FastAPI(title='VoiceOS Backend')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

memory = CommandMemory()

@app.get('/health')
def health():
    return {'status': 'ok', 'mode': 'text'}

@app.post('/parse')
def parse(body: dict):
    text = body.get('text', '')
    intent = parse_command(text)
    memory.save(text, intent)
    return intent

@app.get('/history')
def history():
    return {'commands': memory.recent(20)}

@app.post('/execute')
def run_action(body: dict):
    intent = body.get('intent', {})
    result = execute(intent)
    return result

@app.post('/voice_command')
def full_pipeline(body: dict):
    text = body.get('text', '')
    intent = parse_command(text)
    memory.save(text, intent)
    if intent.get('action') == 'workflow':
        result = execute_workflow(intent)
    else:
        result = execute(intent)
    return {'intent': intent, 'result': result}

@app.get('/permissions/startup')
def startup_apps():
    return {'apps': get_startup_apps()}

@app.get('/permissions/processes')
def processes():
    return {'processes': get_running_processes()}

@app.get('/permissions/disk')
def disk():
    return {'disks': get_disk_usage()}

@app.get('/permissions/admin')
def admin_status():
    return {'is_admin': is_admin()}

@app.post('/permissions/kill')
def kill(body: dict):
    pid = body.get('pid', '')
    return kill_process(pid)

@app.post('/permissions/disable_startup')
def disable_startup(body: dict):
    name = body.get('name', '')
    return disable_startup_app(name)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)