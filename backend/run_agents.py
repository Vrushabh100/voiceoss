import threading, time
from voice_pipeline import get_pipeline
from intent_parser import parse_command
from executor import execute, execute_workflow
from agent_manager import AgentManager
from memory import CommandMemory
from message_bus import listen_as_agent

memory = CommandMemory()
manager = AgentManager()

# ============================================================
# EXECUTOR AGENT — listens on Redis and executes intents
# ============================================================
def executor_agent_loop():
    def handle(intent):
        print(f'[Executor] Received: {intent.get("action")}')
        if intent.get('action') == 'workflow':
            result = execute_workflow(intent)
        else:
            result = execute(intent)
        print(f'[Executor] Result: {result}')
    listen_as_agent('executor', handle)

# ============================================================
# VOICE COMMAND HANDLER — called when user speaks/types
# ============================================================
def on_voice_command(text):
    print(f'\n[Voice] Heard: {text}')

    # Check memory for similar past commands
    similar = memory.recall(text, n=3)
    if similar:
        print(f'[Memory] Similar past commands: {similar}')

    # Parse command to intent
    intent = parse_command(text)
    print(f'[Parser] Intent: {intent.get("action")} -> {intent.get("target")}')

    # Save to memory
    memory.save(text, intent)

    # Dispatch to agent
    manager.dispatch(intent)

# ============================================================
# START ALL AGENTS
# ============================================================
print('=' * 50)
print('VoiceOS Agent System Starting...')
print('=' * 50)

# Start executor agent in background thread
threading.Thread(target=executor_agent_loop, daemon=True).start()
print('[Agent] Executor agent started')

# Start voice pipeline
pipeline = get_pipeline()
pipeline.start(on_voice_command)

print('[Agent] All agents running!')
print('=' * 50)

# Keep running until user exits
while pipeline.running:
    time.sleep(0.5)

print('VoiceOS stopped.')