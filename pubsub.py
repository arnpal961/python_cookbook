# Problem #
# Program based on comunicating threads 
# and wants them to implement pub/sub 
# messaging.

from collections import defaultdict
from contextlib import contextmanager

class Exchange:
    def __init__(self):
        self._subscribers = set()

    def attach(self, task):
        self._subscribers.add(task)
    
    def detach(self, task):
        self._subscribers.remove(task)

    @contextmanager
    def subscribe(self, *tasks):
        for task in tasks:
            self.attach(task)
        try:
            yield
        finally:
            for task in tasks:
                self.detach(task)
                
    def send(self, msg):
        for subscriber in self._subscribers:
            subscriber.send(msg)

# Dictionary for all created exchanges
_exchanges = defaultdict(Exchange)

# Return the Exchange instance associated with a given name
def get_exchange(name):
    return _exchanges[name]

# Task is a any class with a send method
class Task: 
    def send(self, msg): 
        print(msg)

class DisplayMessages:
    def __init__(self):
        self.count = 0

    def send(self, msg):
        self.count += 1
        print(f"msg[{self.count}]: {msg}")

if __name__ == "__main__":
    exc = get_exchange('name')
    # d = DisplayMessages()
    # exc.attach(d)
    # try:
    #     exc.send('msg1')
    #     exc.send('msg2')
    # except Exception as e:
    #     print(e.args)
    # finally:
    #     print("detaching...")
    #     exc.detach(d)

    tasks = [DisplayMessages() for i in range(5)]
    with exc.subscribe(*tasks):
        for i in range(5):
            exc.send(f"msg{i+1}")
