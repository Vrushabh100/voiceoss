import threading
from message_bus import send_to_agent, listen_as_agent

ACTION_TO_AGENT = {
    'open_app':          'executor',
    'close_app':         'executor',
    'open_file':         'executor',
    'create_folder':     'executor',
    'delete_file':       'executor',
    'take_screenshot':   'executor',
    'type_text':         'executor',
    'run_command':       'executor',
    'set_volume':        'executor',
    'shutdown':          'executor',
    'restart':           'executor',
    'minimize_window':   'executor',
    'open_website':      'executor',
    'search_web':        'executor',
    'hotkey':            'executor',
    'wait':              'executor',
    'workflow':          'executor',
    'grant_permission':  'permissions',
    'revoke_permission': 'permissions',
    'list_permissions':  'permissions',
}

class AgentManager:
    def __init__(self):
        threading.Thread(target=self._listen, daemon=True).start()
        print('Agent Manager started')

    def dispatch(self, intent: dict):
        action = intent.get('action', 'unknown')
        agent = ACTION_TO_AGENT.get(action, 'executor')
        print(f'[Manager] Routing {action!r} to agent:{agent}')
        send_to_agent(agent, intent)
        return agent

    def _listen(self):
        listen_as_agent('manager', self._handle)

    def _handle(self, msg):
        print(f'[Manager] Received: {msg}')
        self.dispatch(msg)

if __name__ == '__main__':
    import time
    print('Testing Agent Manager...')
    manager = AgentManager()
    
    test_intents = [
        {'action': 'open_app', 'target': 'notepad', 'params': {}},
        {'action': 'take_screenshot', 'target': '', 'params': {}},
        {'action': 'open_website', 'target': 'https://youtube.com', 'params': {}},
    ]
    
    for intent in test_intents:
        agent = manager.dispatch(intent)
        print(f'Dispatched {intent["action"]} to {agent}')
    
    time.sleep(1)
    print('Agent Manager OK!')