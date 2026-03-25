import chromadb, json
from datetime import datetime

class CommandMemory:
    def __init__(self):
        self.client = chromadb.PersistentClient(path='C:/VoiceOS/memory')
        self.collection = self.client.get_or_create_collection('commands')
        self.counter = self.collection.count()

    def save(self, spoken_text: str, parsed_intent: dict):
        self.counter += 1
        self.collection.add(
            documents=[spoken_text],
            metadatas=[{
                'intent': json.dumps(parsed_intent),
                'timestamp': datetime.now().isoformat()
            }],
            ids=[f'cmd_{self.counter}']
        )
        print(f'[Memory] Saved: {spoken_text}')

    def recall(self, query: str, n=5):
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n, self.counter)
            )
            return results['documents'][0] if results['documents'] else []
        except:
            return []

    def recent(self, n=10):
        try:
            results = self.collection.get(limit=n)
            return results['documents']
        except:
            return []

if __name__ == '__main__':
    mem = CommandMemory()
    mem.save('open chrome', {'action': 'open_app', 'target': 'chrome', 'params': {}})
    mem.save('take a screenshot', {'action': 'take_screenshot', 'target': '', 'params': {}})
    print('Recent:', mem.recent())
    print('Recall:', mem.recall('open browser'))
    print('Memory OK!')
