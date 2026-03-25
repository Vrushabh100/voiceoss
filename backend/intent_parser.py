import requests, json, re

# ============================================================
# THESE ARE THE ONLY ACTIONS EXECUTOR SUPPORTS
# LLaMA3 must use ONLY these — nothing else
# ============================================================
ALLOWED_ACTIONS = """
open_app        - open desktop app.         target = app name
close_app       - close desktop app.        target = app name
open_website    - open URL in browser.      target = full https:// URL
search_web      - google search.            target = search query
type_text       - type text via keyboard.   target = text to type
hotkey          - keyboard shortcut.        target = keys e.g. ctrl+s, enter, tab, ctrl+enter
take_screenshot - capture screen.           target = empty
create_folder   - create folder.            target = folder name
set_volume      - change volume.            target = number 0-100
minimize_window - minimize windows.         target = all
shutdown        - shutdown pc.              target = now
restart         - restart pc.               target = now
wait            - pause.                    target = seconds as string e.g. 3
workflow        - multi step task.          target = task name, steps = list of above actions
"""

PROMPT_TEMPLATE = """You are VoiceOS, an AI assistant that converts any user command into executable JSON steps for a Windows PC.

YOU MUST ONLY USE THESE ACTIONS:
{actions}

RULES:
1. Reply ONLY with valid JSON. No explanation. No markdown. No extra text.
2. For simple one-step commands use single action format.
3. For any task needing multiple steps use workflow format with steps list.
4. Always use complete https:// URLs for websites.
5. Add wait steps after opening websites before typing (websites need time to load).
6. Think carefully about what steps a human would take to complete the task.

SINGLE ACTION FORMAT:
{{"action": "open_app", "target": "notepad", "params": {{}}}}

WORKFLOW FORMAT:
{{"action": "workflow", "target": "task_name", "params": {{}}, "steps": [
  {{"action": "ACTION", "target": "TARGET", "params": {{}}}},
  {{"action": "ACTION", "target": "TARGET", "params": {{}}}}
]}}

EXAMPLES:
User: send email to john@gmail.com about project update saying the project is done
{{"action": "workflow", "target": "send_email", "params": {{}}, "steps": [
  {{"action": "open_website", "target": "https://mail.google.com", "params": {{}}}},
  {{"action": "wait", "target": "5", "params": {{}}}},
  {{"action": "hotkey", "target": "c", "params": {{}}}},
  {{"action": "wait", "target": "3", "params": {{}}}},
  {{"action": "type_text", "target": "john@gmail.com", "params": {{}}}},
  {{"action": "hotkey", "target": "tab", "params": {{}}}},
  {{"action": "wait", "target": "1", "params": {{}}}},
  {{"action": "type_text", "target": "project update", "params": {{}}}},
  {{"action": "hotkey", "target": "tab", "params": {{}}}},
  {{"action": "wait", "target": "1", "params": {{}}}},
  {{"action": "type_text", "target": "the project is done", "params": {{}}}},
  {{"action": "hotkey", "target": "ctrl+enter", "params": {{}}}}
]}}

User: compose email to boss@company.com subject weekly report body all tasks completed
{{"action": "workflow", "target": "send_email", "params": {{}}, "steps": [
  {{"action": "open_website", "target": "https://mail.google.com", "params": {{}}}},
  {{"action": "wait", "target": "5", "params": {{}}}},
  {{"action": "hotkey", "target": "c", "params": {{}}}},
  {{"action": "wait", "target": "3", "params": {{}}}},
  {{"action": "type_text", "target": "boss@company.com", "params": {{}}}},
  {{"action": "hotkey", "target": "tab", "params": {{}}}},
  {{"action": "wait", "target": "1", "params": {{}}}},
  {{"action": "type_text", "target": "weekly report", "params": {{}}}},
  {{"action": "hotkey", "target": "tab", "params": {{}}}},
  {{"action": "wait", "target": "1", "params": {{}}}},
  {{"action": "type_text", "target": "all tasks completed", "params": {{}}}},
  {{"action": "hotkey", "target": "ctrl+enter", "params": {{}}}}
]}}
User: open chrome
{{"action": "open_app", "target": "chrome", "params": {{}}}}

User: search youtube for tere naam songs
{{"action": "open_website", "target": "https://www.youtube.com/results?search_query=tere+naam+songs", "params": {{}}}}

User: send email to john@gmail.com about project update saying the project is done
{{"action": "workflow", "target": "send_email", "params": {{}}, "steps": [
  {{"action": "open_website", "target": "https://mail.google.com", "params": {{}}}},
  {{"action": "wait", "target": "4", "params": {{}}}},
  {{"action": "hotkey", "target": "c", "params": {{}}}},
  {{"action": "wait", "target": "2", "params": {{}}}},
  {{"action": "type_text", "target": "john@gmail.com", "params": {{}}}},
  {{"action": "hotkey", "target": "tab", "params": {{}}}},
  {{"action": "type_text", "target": "project update", "params": {{}}}},
  {{"action": "hotkey", "target": "tab", "params": {{}}}},
  {{"action": "type_text", "target": "the project is done", "params": {{}}}},
  {{"action": "hotkey", "target": "ctrl+enter", "params": {{}}}}
]}}

User: ask claude what is python
{{"action": "workflow", "target": "ask_claude", "params": {{}}, "steps": [
  {{"action": "open_website", "target": "https://claude.ai", "params": {{}}}},
  {{"action": "wait", "target": "5", "params": {{}}}},
  {{"action": "type_text", "target": "what is python", "params": {{}}}},
  {{"action": "hotkey", "target": "enter", "params": {{}}}}
]}}

User: open notepad and type hello world
{{"action": "workflow", "target": "open_and_type", "params": {{}}, "steps": [
  {{"action": "open_app", "target": "notepad", "params": {{}}}},
  {{"action": "wait", "target": "2", "params": {{}}}},
  {{"action": "type_text", "target": "hello world", "params": {{}}}}
]}}

User: {command}
"""

def extract_json(text):
    start = text.find('{')
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i+1])
                except:
                    return None
    return None

def normalize(parsed):
    if 'target' not in parsed:
        parsed['target'] = ''
    if 'params' not in parsed:
        parsed['params'] = {}
    if parsed.get('action') == 'workflow' and 'steps' in parsed:
        for step in parsed['steps']:
            if 'target' not in step:
                step['target'] = ''
            if 'params' not in step:
                step['params'] = {}
    return parsed

def parse_command(text: str) -> dict:
    t = text.lower().strip()

    # ============================================================
    # AI ASSISTANT QUICK RULES — never hits LLaMA3
    # ============================================================
    ai_sites = {
        'chatgpt':   'https://chat.openai.com',
        'claude':    'https://claude.ai',
        'gemini':    'https://gemini.google.com',
        'copilot':   'https://copilot.microsoft.com',
        'perplexity':'https://perplexity.ai',
        'bard':      'https://gemini.google.com',
    }

    for ai_name, ai_url in ai_sites.items():
        pattern = rf'(?:ask|open|use)\s+{ai_name}\s+(?:about|to|for|and ask)?\s*(.+)'
        match = re.search(pattern, t, re.I)
        if match:
            question = match.group(1).strip()
            return {
                'action': 'workflow',
                'target': f'ask_{ai_name}',
                'params': {'question': question},
                'steps': [
    {'action': 'open_website', 'target': ai_url, 'params': {}},
    {'action': 'wait', 'target': '8', 'params': {}},
    {'action': 'hotkey', 'target': 'tab', 'params': {}},
    {'action': 'wait', 'target': '1', 'params': {}},
    {'action': 'hotkey', 'target': 'tab', 'params': {}},
    {'action': 'wait', 'target': '1', 'params': {}},
    {'action': 'type_text', 'target': question, 'params': {}},
    {'action': 'wait', 'target': '1', 'params': {}},
    {'action': 'hotkey', 'target': 'enter', 'params': {}},
                        ]

            }
        if ai_name in t and len(t.split()) <= 3:
            return {'action': 'open_website', 'target': ai_url, 'params': {}}

    # ============================================================
    # YOUTUBE QUICK RULES
    # ============================================================
    yt_patterns = [
        r'(?:search youtube for|open youtube and search|play|watch)\s+(.+?)(?:\s+on youtube|$)',
        r'youtube\s+(.+)',
    ]
    for pattern in yt_patterns:
        match = re.search(pattern, t, re.I)
        if match:
            q = match.group(1).strip().replace(' ', '+')
            return {
                'action': 'open_website',
                'target': f'https://www.youtube.com/results?search_query={q}',
                'params': {}
            }

    # ============================================================
    # Layer 1 — instant rules for common commands (no LLaMA3 needed)
    # ============================================================

    # Open websites directly
    sites = {
        'youtube':   'https://youtube.com',
        'gmail':     'https://mail.google.com',
        'github':    'https://github.com',
        'facebook':  'https://facebook.com',
        'twitter':   'https://twitter.com',
        'instagram': 'https://instagram.com',
        'linkedin':  'https://linkedin.com',
        'netflix':   'https://netflix.com',
        'reddit':    'https://reddit.com',
        'drive':     'https://drive.google.com',
        'calendar':  'https://calendar.google.com',
        'meet':      'https://meet.google.com',
        'docs':      'https://docs.google.com',
        'sheets':    'https://sheets.google.com',
        'spotify':   'https://open.spotify.com',
        'maps':      'https://maps.google.com',
        'whatsapp':  'https://web.whatsapp.com',
    }

    apps = ['notepad', 'calculator', 'calc', 'paint', 'cmd',
            'terminal', 'explorer', 'word', 'excel', 'chrome',
            'edge', 'taskmgr', 'task manager']

    if t.startswith('open '):
        name = t[5:].strip()
        for site, url in sites.items():
            if site in name:
                return {'action': 'open_website', 'target': url, 'params': {}}
        for app in apps:
            if app in name:
                return {'action': 'open_app', 'target': name, 'params': {}}

    if any(w in t for w in ['screenshot', 'screen shot']):
        return {'action': 'take_screenshot', 'target': '', 'params': {}}

    if 'minimize' in t:
        return {'action': 'minimize_window', 'target': 'all', 'params': {}}

    if 'volume' in t:
        nums = re.findall(r'\d+', t)
        return {'action': 'set_volume',
                'target': nums[0] if nums else '50', 'params': {}}

    if any(w in t for w in ['search google', 'search for', 'google for']):
        query = re.sub(r'.*(search google for|search for|google for)\s+', '', t)
        return {'action': 'search_web', 'target': query, 'params': {}}

    if t.startswith('type '):
        return {'action': 'type_text', 'target': t[5:], 'params': {}}

    if t.startswith('close '):
        return {'action': 'close_app', 'target': t[6:].strip(), 'params': {}}

    # ============================================================
    # Layer 2 — LLaMA3 for complex commands only
    # ============================================================
    prompt = PROMPT_TEMPLATE.format(
        actions=ALLOWED_ACTIONS,
        command=text
    )
    try:
        resp = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'llama3', 'prompt': prompt, 'stream': False},
            timeout=90
        )
        raw = resp.json()['response'].strip()
        parsed = extract_json(raw)
        if parsed and 'action' in parsed:
            return normalize(parsed)
    except Exception as e:
        print(f'Parser error: {e}')

    return {'action': 'unknown', 'target': text, 'params': {}}

# def parse_command(text: str) -> dict:
#     # Layer 1 — instant rules for common commands (no LLaMA3 needed)
#     t = text.lower().strip()

#     # Open websites directly
#     sites = {
#         'youtube':   'https://youtube.com',
#         'gmail':     'https://mail.google.com',
#         'github':    'https://github.com',
#         'facebook':  'https://facebook.com',
#         'twitter':   'https://twitter.com',
#         'instagram': 'https://instagram.com',
#         'linkedin':  'https://linkedin.com',
#         'netflix':   'https://netflix.com',
#         'reddit':    'https://reddit.com',
#         'drive':     'https://drive.google.com',
#         'calendar':  'https://calendar.google.com',
#         'meet':      'https://meet.google.com',
#         'docs':      'https://docs.google.com',
#         'sheets':    'https://sheets.google.com',
#         'spotify':   'https://open.spotify.com',
#         'maps':      'https://maps.google.com',
#         'whatsapp':  'https://web.whatsapp.com',
#         'chatgpt':   'https://chat.openai.com',
#         'claude':    'https://claude.ai',
#         'gemini':    'https://gemini.google.com',
#         'copilot':   'https://copilot.microsoft.com',
#         'perplexity':'https://perplexity.ai',
#     }

#     # Apps
#     apps = ['notepad', 'calculator', 'calc', 'paint', 'cmd',
#             'terminal', 'explorer', 'word', 'excel', 'chrome',
#             'edge', 'taskmgr', 'task manager']

#     # YouTube search
#     yt = re.search(r'(?:search youtube for|open youtube and search|play|watch)\s+(.+?)(?:\s+on youtube|$)', t)
#     if yt:
#         q = yt.group(1).strip().replace(' ', '+')
#         return {'action': 'open_website',
#                 'target': f'https://www.youtube.com/results?search_query={q}',
#                 'params': {}}

#     # Open website
#     if t.startswith('open '):
#         name = t[5:].strip()
#         for site, url in sites.items():
#             if site in name:
#                 return {'action': 'open_website', 'target': url, 'params': {}}
#         for app in apps:
#             if app in name:
#                 return {'action': 'open_app', 'target': name, 'params': {}}

#     # Screenshot
#     if any(w in t for w in ['screenshot', 'screen shot']):
#         return {'action': 'take_screenshot', 'target': '', 'params': {}}

#     # Minimize
#     if 'minimize' in t:
#         return {'action': 'minimize_window', 'target': 'all', 'params': {}}

#     # Volume
#     if 'volume' in t:
#         nums = re.findall(r'\d+', t)
#         return {'action': 'set_volume',
#                 'target': nums[0] if nums else '50', 'params': {}}

#     # Search web
#     if any(w in t for w in ['search google', 'search for', 'google for']):
#         query = re.sub(r'.*(search google for|search for|google for)\s+', '', t)
#         return {'action': 'search_web', 'target': query, 'params': {}}

#     # Type text
#     if t.startswith('type '):
#         return {'action': 'type_text', 'target': t[5:], 'params': {}}

#     # Close app
#     if t.startswith('close '):
#         return {'action': 'close_app', 'target': t[6:].strip(), 'params': {}}

#     # Layer 2 — LLaMA3 for complex commands only
#     prompt = PROMPT_TEMPLATE.format(
#         actions=ALLOWED_ACTIONS,
#         command=text
#     )
#     try:
#         resp = requests.post(
#             'http://localhost:11434/api/generate',
#             json={'model': 'llama3', 'prompt': prompt, 'stream': False},
#             timeout=90
#         )
#         raw = resp.json()['response'].strip()
#         parsed = extract_json(raw)
#         if parsed and 'action' in parsed:
#             return normalize(parsed)
#     except Exception as e:
#         print(f'Parser error: {e}')

#     return {'action': 'unknown', 'target': text, 'params': {}}

if __name__ == '__main__':
    commands = [
        'open chrome',
        'open notepad',
        'take a screenshot',
        'search youtube for tere naam songs',
        'open youtube and search lofi music',
        'send email to test@gmail.com about meeting saying see you at 3pm',
        'ask claude what is python',
        'ask chatgpt explain machine learning',
        'open google meet',
        'set volume to 30',
        'minimize all windows',
        'open notepad and type hello world',
        'create folder named projects on desktop',
        'search google for python tutorials',
        'open gmail and send mail to boss@company.com subject weekly report body all tasks completed',
    ]
    passed = 0
    for cmd in commands:
        print(f'\nTesting: {cmd!r}')
        result = parse_command(cmd)
        status = 'OK' if result['action'] != 'unknown' else 'FAIL'
        if status == 'OK':
            passed += 1
        steps = len(result.get('steps', []))
        steps_str = f' ({steps} steps)' if steps else ''
        print(f'[{status}] -> {result["action"]}{steps_str}')
        if result.get('steps'):
            for s in result['steps']:
                print(f'       {s["action"]:20} {s["target"][:50]}')
    print(f'\nFinal Score: {passed}/{len(commands)}')