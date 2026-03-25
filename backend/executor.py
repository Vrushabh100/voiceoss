import subprocess, os, pyautogui, time, shutil, logging

logging.basicConfig(
    filename='C:/VoiceOS/voiceos.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

APP_MAP = {
    
    'chrome':        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'google':        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'google chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'edge':          r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'msedge':        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'browser':       r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'notepad':       r'C:\Windows\System32\notepad.exe',
    'calculator':    r'C:\Windows\System32\calc.exe',
    'calc':          r'C:\Windows\System32\calc.exe',
    'explorer':      r'C:\Windows\explorer.exe',
    'files':         r'C:\Windows\explorer.exe',
    'cmd':           r'C:\Windows\System32\cmd.exe',
    'terminal':      r'C:\Windows\System32\cmd.exe',
    'paint':         'mspaint.exe',
    'word':          'winword.exe',
    'excel':         'excel.exe',
    'task manager':  'taskmgr.exe',
    'taskmgr':       'taskmgr.exe',

}

def execute(intent: dict) -> dict:
    try:
        action = intent.get('action', 'unknown')
        target = str(intent.get('target', ''))
        params = intent.get('params', {})

        handlers = {
        'open_app':           _open_app,
        'launch_app':         _open_app,
        'open_application':   _open_app,
        'close_app':          _close_app,
        'close_process':      _close_app,
        'close_window':       _close_app,
        'take_screenshot':    _take_screenshot,
        'capture_screenshot': _take_screenshot,
        'type_text':          _type_text,
        'print_message':      _type_text,
        'run_command':        _run_command,
        'create_folder':      _create_folder,
        'open_website':       _open_website,
        'search_web':         _search_web,
        'set_volume':         _set_volume,
        'shutdown':           _shutdown,
        'minimize_window':    _minimize_window,
        'minimize_windows':   _minimize_window,
        'restart':            lambda t, p: (os.system('shutdown /r /t 0'), {'success': True})[1],
        'wait':               lambda t, p: (time.sleep(float(t or 1)), {'success': True})[1],
        'hotkey':             lambda t, p: (pyautogui.hotkey(*t.split('+')), {'success': True})[1],
        'workflow':           lambda t, p: execute_workflow(intent),
    }
        

        fn = handlers.get(action)
        if fn:
            result = fn(target, params)
            logging.info(f'Executed: {intent} -> {result}')
            return result

        logging.warning(f'Unknown action: {action}')
        return {'success': False, 'message': f'Unknown action: {action}'}

    except Exception as e:
        logging.error(f'Executor error: {e} | intent: {intent}')
        return {'success': False, 'error': str(e)}


def _open_app(target, params):
    exe = APP_MAP.get(target.lower().strip(), target)
    try:
        subprocess.Popen(exe, shell=True)
        return {'success': True, 'message': f'Opened {target}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _close_app(target, params):
    try:
        os.system(f'taskkill /f /im {target}.exe')
        return {'success': True, 'message': f'Closed {target}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _take_screenshot(target, params):
    try:
        folder = 'C:/VoiceOS/screenshots'
        os.makedirs(folder, exist_ok=True)
        path = target if target else f'{folder}/shot_{int(time.time())}.png'
        pyautogui.screenshot(path)
        return {'success': True, 'message': f'Screenshot saved to {path}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _type_text(target, params):
    try:
        text = target or params.get('text', '')
        pyautogui.write(str(text), interval=0.05)
        return {'success': True, 'message': f'Typed: {text}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _run_command(target, params):
    try:
        result = subprocess.run(target, shell=True,
                                capture_output=True, text=True)
        return {'success': True, 'output': result.stdout}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _create_folder(target, params):
    try:
        base = params.get('path', os.path.expanduser('~') + '/Desktop')
        path = os.path.join(base, target)
        os.makedirs(path, exist_ok=True)
        return {'success': True, 'message': f'Folder created: {path}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
def _open_website(target, params):
    try:
        url = target if target.startswith('http') else f'https://{target}'
        chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
        browser = chrome if os.path.exists(chrome) else edge
        subprocess.Popen([browser, url])
        return {'success': True, 'message': f'Opened {url}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _search_web(target, params):
    try:
        query = target.replace(' ', '+')
        url = f'https://www.google.com/search?q={query}'
        subprocess.Popen(['msedge.exe', url], shell=True)
        return {'success': True, 'message': f'Searching: {target}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _set_volume(target, params):
    try:
        level = int(''.join(filter(str.isdigit, str(target))) or
                    str(params.get('level', 50)))
        # Using nircmd — download from nirsoft.net if not working
        subprocess.run(f'nircmd.exe setsysvolume {int(level * 655.35)}',
                       shell=True)
        return {'success': True, 'message': f'Volume set to {level}%'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _shutdown(target, params):
    try:
        delay = 0 if 'now' in str(target) else 60
        os.system(f'shutdown /s /t {delay}')
        return {'success': True, 'message': 'Shutting down'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def _minimize_window(target, params):
    try:
        if target == 'all' or target == '':
            pyautogui.hotkey('win', 'd')
        return {'success': True, 'message': 'Minimized windows'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def execute_workflow(intent: dict) -> dict:
    steps = intent.get('steps', [])
    results = []
    print(f'\n[Workflow] Starting: {intent.get("target")} ({len(steps)} steps)')

    for i, step in enumerate(steps, 1):
        action = step.get('action', '')
        target = str(step.get('target', ''))
        params = step.get('params', {})

        print(f'  Step {i}/{len(steps)}: {action} -> {target[:50]}')

        if action == 'wait':
            secs = float(target or 1)
            print(f'    Waiting {secs} seconds...')
            time.sleep(secs)
            results.append({'success': True})

        elif action == 'hotkey':
            keys = target.split('+')
            # Small delay before each hotkey so UI is ready
            time.sleep(0.5)
            pyautogui.hotkey(*keys)
            results.append({'success': True})

        elif action == 'type_text':
            # Small delay before typing so field is focused
            time.sleep(0.3)
            # Use pyperclip for reliable unicode typing
            try:
                import pyperclip
                pyperclip.copy(target)
                pyautogui.hotkey('ctrl+v')
            except:
                pyautogui.write(target, interval=0.05)
            results.append({'success': True})

        else:
            result = execute(step)
            results.append(result)

    print(f'[Workflow] Complete: {len(results)} steps executed')
    return {
        'success': True,
        'workflow': intent.get('target', ''),
        'steps_executed': len(results)
    }

if __name__ == '__main__':
    tests = [
        {'action': 'open_app', 'target': 'notepad', 'params': {}},
        {'action': 'take_screenshot', 'target': '', 'params': {}},
        {'action': 'create_folder', 'target': 'TestFolder', 'params': {}},
    ]
    for intent in tests:
        result = execute(intent)
        print(f'{intent["action"]:20} -> {result}')