import redis, json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def publish(channel: str, data: dict):
    r.publish(channel, json.dumps(data))

def subscribe(channel: str):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    return pubsub

def send_to_agent(agent_name: str, task: dict):
    publish(f'agent:{agent_name}', task)

def listen_as_agent(agent_name: str, handler):
    ps = subscribe(f'agent:{agent_name}')
    for msg in ps.listen():
        if msg['type'] == 'message':
            handler(json.loads(msg['data']))

if __name__ == '__main__':
    print('Testing Redis message bus...')
    try:
        r.ping()
        print('Redis connection OK')
        send_to_agent('test', {'action': 'open_app', 'target': 'notepad'})
        print('Message sent OK')
        print('Message bus working!')
    except Exception as e:
        print(f'Redis error: {e}')