# defining tasks similar to actor model

from queue import Queue
from threading import Thread, Event

# Sentinel used for shutdown
class ActorExit(Exception):
    pass


# Asynchronous and concurrent message delivery
class Actor:
    def __init__(self):
        self._mailbox = Queue()

    def send(self, msg):
        """
        Send a message to actor
        """
        self._mailbox.put(msg)

    def recv(self):
        """
        Receive an incoming message
        """
        msg = self._mailbox.get()
        if msg is ActorExit:
            raise ActorExit()
        return msg

    def close(self):
        """
        Close the actor, thus shutting it down.
        """
        self.send(ActorExit)

    def start(self):
        """
        Start concurrent execution
        """
        self._terminated = Event()
        t = Thread(target=self._bootstrap)
        t.daemon = True
        t.start()

    def _bootstrap(self):
        try:
            self.run()
        except ActorExit:
            pass
        finally:
            self._terminated.set()

    def join(self):
        self._terminated.wait()

    def run(self):
        """
        Run the method to be implemented by the user.
        """
        while True:
            msg = self.recv()


# Sample ActorTask
class PrintActor(Actor):
    def run(self):
        while True:
            msg = self.recv()
            print("Got:", msg)


# Using yield by relaxing the asynchronous
# and concurrent message delivery condition


def print_actor():
    while True:
        try:
            msg = yield
            print("Got:", msg)
        except (GeneratorExit, RuntimeError):
            print("Actor terminating")
            # adding a return statement because
            # otherwise generator try to yield msg
            # and it throws runtime error and and 
            # this error can't be thrown out
            return


# passing tagged messages in the form of tupple
# and have actors take different courese of action
# like this
class TaggedActor(Actor):
    def run(self):
        while True:
            tag, *payload = self.recv()
            getattr(self, f"do_{tag}")(*payload)

    # Methods corresponding to different meassage tags
    def do_A(self, x):
        print("Running A", x)

    def do_B(self, x, y):
        print("Running B", x, y)

# a variation of an actor that allows arbitrary
# functions to be executed in a worker and results
# to be comunicated back using a special Result object.

class Result:
    def __init__(self):
        self._evt = Event()
        self._result = None
    
    def set_result(self, value):
        self._result = value
        self._evt.set()

    def result(self):
        self._evt.wait()
        return self._result

class Worker(Actor):
    def submit(self, func, *args, **kwargs):
        r = Result()
        self.send((func, args, kwargs, r))
        return r
    
    def run(self):
        while True:
            func, args, kwargs, r = self.recv()
            r.set_result(func(*args, **kwargs))


if __name__ == "__main__":
    print("Running PrintActor class\n")
    p = PrintActor()
    p.start()
    p.send("Hello")
    p.send("World")
    p.close()
    p.join()
    ###################
    print("Running print_actor function\n")
    g = print_actor()
    next(g)  # Advance to the yield function
    g.send("Hello")
    g.send("World")
    g.close()
    ##################
    print("Running TaggedActor class\n")
    a = TaggedActor()
    a.start()
    a.send(('A', 1))
    a.send(('B', 2, 3))
    ####################
    print("Running Worker class\n")
    worker = Worker()
    worker.start()
    r = worker.submit(pow, 2, 3)
    print(r.result())