import requests, json, re

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

# ============================================================
# WORKFLOWS — multi step actions
# ============================================================

def workflow_send_email(text):
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group() if email_match else ''
    subject_match = re.search(r'(?:about|subject|regarding)\s+(.+?)(?:\s+saying|\s+body|$)', text, re.I)
    subject = subject_match.group(1).strip() if subject_match else 'No Subject'
    body_match = re.search(r'(?:saying|body|message|content)\s+(.+?)$', text, re.I)
    body = body_match.group(1).strip() if body_match else ''
    return {
        'action': 'workflow', 'target': 'send_email',
        'params': {'email': email, 'subject': subject, 'body': body},
        'steps': [
            {'action': 'open_website', 'target': 'https://mail.google.com', 'params': {}},
            {'action': 'wait', 'target': '4', 'params': {}},
            {'action': 'hotkey', 'target': 'c', 'params': {}},
            {'action': 'wait', 'target': '2', 'params': {}},
            {'action': 'type_text', 'target': email, 'params': {}},
            {'action': 'hotkey', 'target': 'tab', 'params': {}},
            {'action': 'type_text', 'target': subject, 'params': {}},
            {'action': 'hotkey', 'target': 'tab', 'params': {}},
            {'action': 'type_text', 'target': body, 'params': {}},
        ]
    }

def workflow_whatsapp(text):
    contact_match = re.search(r'(?:to|message)\s+([\w\s]+?)(?:\s+saying|\s+about|$)', text, re.I)
    contact = contact_match.group(1).strip() if contact_match else ''
    msg_match = re.search(r'(?:saying|message|about)\s+(.+?)$', text, re.I)
    message = msg_match.group(1).strip() if msg_match else ''
    return {
        'action': 'workflow', 'target': 'whatsapp_message',
        'params': {'contact': contact, 'message': message},
        'steps': [
            {'action': 'open_website', 'target': 'https://web.whatsapp.com', 'params': {}},
            {'action': 'wait', 'target': '4', 'params': {}},
        ]
    }

def workflow_youtube(text):
    query_match = re.search(r'(?:youtube|play|watch|search youtube for|open youtube and search)\s+(.+?)$', text, re.I)
    query = query_match.group(1).strip() if query_match else text
    # Direct search URL — no typing needed, instant results
    url = f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}'
    return {
        'action': 'workflow', 'target': 'youtube_search',
        'params': {'query': query},
        'steps': [
            {'action': 'open_website', 'target': url, 'params': {}},
        ]
    }

def workflow_create_doc(text):
    name_match = re.search(r'(?:called|named|document|file)\s+(.+?)(?:\s+with|\s+containing|$)', text, re.I)
    name = name_match.group(1).strip() if name_match else 'NewDocument'
    content_match = re.search(r'(?:with|containing|content|write)\s+(.+?)$', text, re.I)
    content = content_match.group(1).strip() if content_match else ''
    return {
        'action': 'workflow', 'target': 'create_document',
        'params': {'name': name, 'content': content},
        'steps': [
            {'action': 'open_app', 'target': 'notepad', 'params': {}},
            {'action': 'wait', 'target': '2', 'params': {}},
            {'action': 'type_text', 'target': content, 'params': {}},
            {'action': 'hotkey', 'target': 'ctrl+s', 'params': {}},
            {'action': 'wait', 'target': '1', 'params': {}},
            {'action': 'type_text', 'target': name, 'params': {}},
            {'action': 'hotkey', 'target': 'enter', 'params': {}},
        ]
    }


def workflow_ai(site_url, question):
    # Build direct search URLs where possible
    direct_urls = {
        'https://chat.openai.com': f'https://chat.openai.com/?q={question.replace(" ", "+")}',
        'https://perplexity.ai': f'https://www.perplexity.ai/search?q={question.replace(" ", "+")}',
        'https://gemini.google.com': f'https://gemini.google.com/app?q={question.replace(" ", "+")}',
    }
    # For sites with direct URL search, just open the URL
    if site_url in direct_urls and question:
        return {
            'action': 'workflow', 'target': 'ask_ai',
            'params': {'question': question, 'site': site_url},
            'steps': [
                {'action': 'open_website', 'target': direct_urls[site_url], 'params': {}},
            ]
        }
    # For Claude and Copilot, open site and type
    return {
        'action': 'workflow', 'target': 'ask_ai',
        'params': {'question': question, 'site': site_url},
        'steps': [
            {'action': 'open_website', 'target': site_url, 'params': {}},
            {'action': 'wait', 'target': '6', 'params': {}},
            {'action': 'hotkey', 'target': 'tab', 'params': {}},
            {'action': 'hotkey', 'target': 'tab', 'params': {}},
            {'action': 'type_text', 'target': question, 'params': {}},
            {'action': 'hotkey', 'target': 'enter', 'params': {}},
        ]
    }
def workflow_open_and_type(text):
    match = re.match(r'open\s+(\w+)\s+and\s+type\s+(.+)', text, re.I)
    if match:
        app = match.group(1).strip()
        content = match.group(2).strip()
        return {
            'action': 'workflow', 'target': 'open_and_type',
            'params': {'app': app, 'text': content},
            'steps': [
                {'action': 'open_app', 'target': app, 'params': {}},
                {'action': 'wait', 'target': '2', 'params': {}},
                {'action': 'type_text', 'target': content, 'params': {}},
            ]
        }
    return None

# ============================================================
# RULE BASED PARSER
# ============================================================

def rule_based_parse(text):
    t = text.lower().strip()
    # YouTube patterns — must be before single-word site check
    youtube_patterns = [
        r'open youtube and search\s+(.+)',
        r'search youtube for\s+(.+)',
        r'play\s+(.+?)\s+on youtube',
        r'watch\s+(.+?)\s+on youtube',
        r'youtube\s+(.+)',
    ]
    for pattern in youtube_patterns:
        match = re.search(pattern, t, re.I)
        if match:
            query = match.group(1).strip()
            url = f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}'
            return {
                'action': 'workflow', 'target': 'youtube_search',
                'params': {'query': query},
                'steps': [
                    {'action': 'open_website', 'target': url, 'params': {}},
                ]
            }


    # Email
    if any(w in t for w in ['send email', 'send mail', 'email to', 'mail to']):
        return workflow_send_email(text)

    # WhatsApp
    if any(w in t for w in ['whatsapp', 'whats app', 'send whatsapp']):
        return workflow_whatsapp(text)

    # YouTube search
    if any(w in t for w in ['play on youtube', 'search youtube', 'watch on youtube']):
        return workflow_youtube(text)

    # Create document
    if any(w in t for w in ['create document', 'new document', 'create file', 'write document']):
        return workflow_create_doc(text)

    # Google Meet
    if any(w in t for w in ['google meet', 'start meeting', 'new meeting']):
        return {'action': 'workflow', 'target': 'google_meet', 'params': {},
                'steps': [{'action': 'open_website', 'target': 'https://meet.google.com/new', 'params': {}}]}

    # AI Assistants
    if any(w in t for w in ['ask claude', 'open claude', 'claude ai']):
        q = re.sub(r'.*(ask claude|open claude|claude ai)\s*', '', text, flags=re.I).strip()
        return workflow_ai('https://claude.ai', q)

    if any(w in t for w in ['ask chatgpt', 'open chatgpt', 'chatgpt']):
        q = re.sub(r'.*(ask chatgpt|open chatgpt|chatgpt)\s*', '', text, flags=re.I).strip()
        return workflow_ai('https://chat.openai.com', q)

    if any(w in t for w in ['ask gemini', 'open gemini', 'gemini ai', 'gemini']):
        q = re.sub(r'.*(ask gemini|open gemini|gemini ai|gemini)\s*', '', text, flags=re.I).strip()
        return workflow_ai('https://gemini.google.com', q)

    if any(w in t for w in ['ask copilot', 'open copilot', 'microsoft copilot', 'copilot']):
        q = re.sub(r'.*(ask copilot|open copilot|microsoft copilot|copilot)\s*', '', text, flags=re.I).strip()
        return workflow_ai('https://copilot.microsoft.com', q)

    if any(w in t for w in ['ask perplexity', 'perplexity']):
        q = re.sub(r'.*(ask perplexity|perplexity)\s*', '', text, flags=re.I).strip()
        return workflow_ai('https://perplexity.ai', q)

    # Open X and type Y
    if re.match(r'open\s+\w+\s+and\s+type\s+', t):
        return workflow_open_and_type(text)

    # Screenshot
    if any(w in t for w in ['screenshot', 'screen shot', 'capture screen']):
        return {'action': 'take_screenshot', 'target': '', 'params': {}}

    # Minimize
    if any(w in t for w in ['minimize', 'minimise']):
        return {'action': 'minimize_window', 'target': 'all', 'params': {}}

    # Search web
    if any(w in t for w in ['search for', 'google for', 'look up', 'search google']):
        query = re.sub(r'.*(search for|google for|look up|search google for)\s+', '', t)
        return {'action': 'search_web', 'target': query, 'params': {}}
     # YouTube search
    if any(w in t for w in ['play on youtube', 'search youtube', 
                             'watch on youtube', 'open youtube and search',
                             'youtube and search', 'play', 'watch']):
        return workflow_youtube(text)
    
    # Open website by name
    sites = {
        'youtube':   'https://youtube.com',
        'facebook':  'https://facebook.com',
        'twitter':   'https://twitter.com',
        'instagram': 'https://instagram.com',
        'github':    'https://github.com',
        'gmail':     'https://mail.google.com',
        'reddit':    'https://reddit.com',
        'linkedin':  'https://linkedin.com',
        'netflix':   'https://netflix.com',
        'spotify':   'https://open.spotify.com',
        'maps':      'https://maps.google.com',
        'drive':     'https://drive.google.com',
        'calendar':  'https://calendar.google.com',
        'meet':      'https://meet.google.com',
        'docs':      'https://docs.google.com',
        'sheets':    'https://sheets.google.com',
    }
    for site, url in sites.items():
        if site in t:
            return {'action': 'open_website', 'target': url, 'params': {}}

    # Volume
    if any(w in t for w in ['volume', 'set volume', 'change volume']):
        nums = re.findall(r'\d+', t)
        level = nums[0] if nums else '50'
        return {'action': 'set_volume', 'target': level, 'params': {}}

    # Shutdown / Restart
    if 'shutdown' in t or 'shut down' in t:
        return {'action': 'shutdown', 'target': 'now', 'params': {}}
    if 'restart' in t or 'reboot' in t:
        return {'action': 'restart', 'target': 'now', 'params': {}}

    # Type text
    if t.startswith('type '):
        return {'action': 'type_text', 'target': t[5:], 'params': {}}

    # Create folder
    if any(w in t for w in ['create folder', 'new folder', 'make folder']):
        name = re.sub(r'.*(create|new|make)\s+(a\s+)?folder\s*(named|called)?\s*', '', t).strip()
        return {'action': 'create_folder', 'target': name, 'params': {}}

    # Close app
    if t.startswith('close '):
        return {'action': 'close_app', 'target': t[6:].strip(), 'params': {}}

    # Open app
    if t.startswith('open '):
        target = re.sub(r'\s+and.*$', '', t[5:]).strip()
        return {'action': 'open_app', 'target': target, 'params': {}}

    return None

def normalize_action(parsed):
    action_map = {
        'open_application':  'open_app',
        'launch_app':        'open_app',
        'launch_program':    'open_app',
        'launch_process':    'open_app',
        'start_app':         'open_app',
        'run_exe':           'open_app',
        'run_program':       'open_app',
        'execute_program':   'open_app',
        'close_application': 'close_app',
        'close_process':     'close_app',
        'close_window':      'close_app',
        'kill_process':      'close_app',
        'screenshot':        'take_screenshot',
        'capture_screenshot':'take_screenshot',
        'print_message':     'type_text',
        'write_text':        'type_text',
        'open_url':          'open_website',
        'open_link':         'open_website',
        'browse_to':         'open_website',
        'navigate_to':       'open_website',
        'google':            'search_web',
        'search':            'search_web',
        'volume':            'set_volume',
        'minimize_windows':  'minimize_window',
        'minimize_all':      'minimize_window',
        'make_folder':       'create_folder',
        'new_folder':        'create_folder',
    }
    parsed['action'] = action_map.get(
        parsed.get('action', ''), parsed.get('action', 'unknown')
    )
    if 'target' not in parsed:
        parsed['target'] = ''
    if 'params' not in parsed:
        parsed['params'] = {}
    if not parsed['target']:
        p = parsed['params']
        parsed['target'] = (p.get('url') or p.get('app') or
                            p.get('name') or p.get('query') or '')
    return parsed

def parse_command(text: str) -> dict:
    result = rule_based_parse(text)
    if result:
        return result
    prompt = ("You are a Windows command parser.\n"
              "Reply ONLY with valid JSON, no other text.\n"
              'Example: {"action": "open_app", "target": "chrome", "params": {}}\n'
              "User: " + text + "\nJSON:")
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=60
        )
        raw = resp.json()["response"].strip()
        parsed = extract_json(raw)
        if parsed and "action" in parsed:
            return normalize_action(parsed)
    except Exception as e:
        print(f"Parser error: {e}")
    return {"action": "unknown", "target": text, "params": {}}

if __name__ == "__main__":
    commands = [
        "open chrome",
        "open notepad",
        "take a screenshot",
        "open youtube",
        "open gmail",
        "search google for python tutorials",
        "set volume to 50",
        "minimize all windows",
        "open notepad and type hello world",
        "send email to test@gmail.com about Meeting saying Hello there",
        "send whatsapp message to John saying good morning",
        "search youtube for lofi music",
        "create document called report with hello world",
        "open google meet",
        "ask claude what is python",
        "ask chatgpt explain machine learning",
        "ask gemini what is the weather today",
        "ask copilot write me a poem",
        "ask perplexity latest news in AI",
    ]
    passed = 0
    for cmd in commands:
        result = parse_command(cmd)
        status = "OK" if result["action"] != "unknown" else "FAIL"
        if status == "OK":
            passed += 1
        steps = len(result.get('steps', []))
        steps_str = f" ({steps} steps)" if steps else ""
        print(f"[{status}] {cmd!r:55} -> {result['action']}{steps_str}")
    print(f"\nScore: {passed}/{len(commands)}")