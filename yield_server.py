# coding=utf-8
from collections import deque
from select import select
from socket import *

from fib import fib, fib_ay
from concurrent.futures import ProcessPoolExecutor as Pool
pool = Pool(3)

result = {"Fib": "NA"}
active_tasks = deque()
recv_wait = {}
send_wait = {}
future_wait = {}
future_notify, future_event = socketpair()

def future_done(future):
    active_tasks.append(future_wait.pop(future))
    future_notify.send(b'x')

def future_monitor():
    while True:
        yield future_event, 'recv'
        future_event.recv(100)

active_tasks.append(future_monitor())

def run():
    while any([active_tasks,recv_wait, send_wait]):
        while active_tasks:
            _task = active_tasks.popleft()
            try:
                print(_task)
                obj, action = next(_task)
                if action in ("accept", "recv"):
                    recv_wait[obj] = _task
                elif action in ("send"):
                    send_wait[obj] = _task
                elif action == 'future':
                    future_wait[obj] = _task
                    obj.add_done_callback(future_done)
                elif action == "run":
                    # need to put obj in task queue the generator
                    active_tasks.append(obj)
                    future_wait[obj] = _task
                    print(f"THE OBJ FROM FUTURE {obj}")
                elif action == "repeat":
                    # need to re-iterate the generator
                    active_tasks.append(_task)
                elif action == "res":
                    print(f"value is {obj}")
                    result["Fib"] = obj
                    print(f"THE RES FROM CO {_task}")
                    print(f"Now really dont know what to do!!!")
            except StopIteration:
                print("Done!")
        # No active tasks to run. Handle IO waits
        recv, send, _ = select(recv_wait, send_wait, [])
        for _recv in recv:
            active_tasks.append(recv_wait.pop(_recv))
        for _send in send:
            active_tasks.append(send_wait.pop(_send))

class Handler:
    @staticmethod
    def fib_handler(client):
        while True:
            yield client, 'recv'
            req = client.recv(100)      # Blocking
            if not req:
                break
            n = int(req)
            # result = "NA"
            # result = fib(n)             # processing intensive
            # future = pool.submit(fib, n)
            # yield future, 'future'         # Blocking
            # result = future.result()
            # result = fib_ay(n)
            yield fib_ay(n), 'run'
            resp = str(result).encode('ascii') + b'\n'
            yield client, 'send'
            client.send(resp)           # Blocking
        print("Closed")


class YieldServer:
    def __init__(self):
        self.handler_obj = Handler()

    def start(self, address):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(address)
        sock.listen(5)
        while True:
            yield sock, 'accept'
            client, addr = sock.accept()        # Blocking
            print("Connection", addr)
            active_tasks.append(self.handler_obj.fib_handler(client))


if __name__ == '__main__':
    fib_server = YieldServer()
    active_tasks.append(fib_server.start(('', 26000)))
    run()

