# coding=utf-8
from collections import deque
from select import select
from socket import *

from fib import fib_generator

active_tasks = deque()

result_bank = {}
recv_wait = {}
send_wait = {}
compute_wait = {}


def run():
    while any([active_tasks, recv_wait, send_wait]):
        while active_tasks:
            _task = active_tasks.popleft()
            try:
                obj, action = next(_task)
                # IO calls socket waits
                if action in ("accept", "recv"):
                    recv_wait[obj] = _task
                elif action in ("send"):
                    send_wait[obj] = _task
                # Custom logic to handle compute tasks
                elif action == 'compute':
                    compute_wait[obj] = _task
                    active_tasks.append(obj)
                elif action == "repeat":
                    # need to re-iterate the generator
                    active_tasks.append(_task)
                elif action == "res":
                    # Some task has given results. pop the parent task from compute wait
                    result_bank[_task] = obj
                    active_tasks.append(compute_wait.pop(_task))
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
            req = client.recv(100)  # Blocking
            if not req:
                break
            n = int(req)
            _gen = fib_generator(n)  # Compute
            yield _gen, 'compute'
            resp = str(result_bank[_gen]).encode('ascii') + b'\n'
            yield client, 'send'
            client.send(resp)  # Blocking
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
            client, addr = sock.accept()  # Blocking
            print("Connection", addr)
            active_tasks.append(self.handler_obj.fib_handler(client))


if __name__ == '__main__':
    fib_server = YieldServer()
    active_tasks.append(fib_server.start(('', 26000)))
    run()
