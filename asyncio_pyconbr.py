import asyncio
import time
from types import coroutine
from collections import deque
from selectors import (DefaultSelector,
                       EVENT_READ,
                       EVENT_WRITE)
from socket import (socket, 
                    AF_INET,
                    SOCK_STREAM,
                    SOL_SOCKET,
                    SO_REUSEADDR)

from gevent.server import StreamServer


async def echo_server(address):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    sock.setblocking(False)
    while True:
        client, addr = await loop.sock_accept(sock)
        print("Connection from", addr)
        loop.create_task(echo_handler(client))


async def echo_handler(client):
    with client:
        while True:
            data = await loop.sock_recv(client, 10000)
            if not data:
                break
            await loop.sock_sendall(client, b"Got:" + data)

    print("Connection closed")

def countdown(n):
    while n > 0:
        yield n
        n -= 1

@coroutine
def spam():
    result = yield 'somevalue'
    print('The result is', result)

async def foo():
    print('start foo')
    await spam()
    print("End foo")

async def bar():
    print('Start bar')
    await foo()
    print('End bar')

############################
#                          #
# async await from scratch #
#                          #
############################

@coroutine
def read_wait(sock):
    yield 'read_wait', sock

@coroutine
def write_wait(sock):
    yield "write wait", sock

class Loop:

    def __init__(self):
        self.ready = deque()
        self.selector = DefaultSelector()
    
    async def sock_recv(self, sock, maxbytes):
        await read_wait(sock)
        return sock.recv(maxbytes)

    async def sock_accept(self, sock):
        await read_wait(sock)
        return sock.accept()

    async def sock_sendall(self, sock, data):
        while data:
            try:
                nsent = sock.send(data)
                data = data[nsent:]
            except BlockingIOError:
                await write_wait(sock)
        # this version of tutorial will not work
        #    await write_wait(sock)
        #    nsent = sock.send(data)
        #    data = data[nsent:]

    def create_task(self, coro):
        self.ready.append(coro)

    def run_forever(self):
        while True:
            while not self.ready:
                events = self.selector.select()
                for key,_ in events:
                    self.ready.append(key.data)
                    self.selector.unregister(key.fileobj)
            while self.ready:
                self.current_task = self.ready.popleft()
                try:
                    op, *args = self.current_task.send(None)
                    getattr(self, op)(*args)
                except StopIteration:
                    pass

    def read_wait(self, sock):
        self.selector.register(sock, EVENT_READ, self.current_task)


    def write_wait(self, sock):
        self.selector.register(sock, EVENT_WRITE, self.current_task)

def echo_green(sock, addr):
    print(f"New connection from {addr}")
    while True:
        data = sock.recv(100000)
        if not data:
            break
        sock.sendall(b'Got:'+ data)
    sock.close()

def benchmark(addr, nmessages):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(addr)
    start = time.time()
    for _ in range(nmessages):
        sock.send(b'x')
        _ = sock.recv(10000)
    end = time.time()
    print(nmessages/(end-start), 'msgs/sec')

if __name__=="__main__":
    # for i in countdown(5):
    #     print(i)

    # If to use the builtin asyncio
    # then uncomment and comment the the
    # following two lines respectively

    loop = asyncio.get_event_loop()
    # loop = Loop()
    loop.create_task(echo_server(("", 25000)))
    loop.run_forever()

    # for gevent testing
    # server = StreamServer(('0.0.0.0', 25000), echo_green)
    # server.serve_forever()