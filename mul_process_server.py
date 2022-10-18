# coding=utf-8
"""
Multi process server
"""
import time
from multiprocessing import Process
from socket import *

from fib import fib


class Handler:
    """
    handler method which manages the service layer
    """
    @staticmethod
    def fib_handler(client):
        while True:
            req = client.recv(100)
            if not req:
                break
            n = int(req)
            result = fib(n)
            resp = str(result).encode('ascii') + b'\n'
            client.send(resp)
        print("Closed")


num_workers = 2


class WorkerProcess:
    """
    Worker Process which starts the slave worker and initialises the service layer
    """
    def __init__(self):
        self.handler_obj = Handler()

    def start(self, sock):
        while True:
            client, addr = sock.accept()
            print("Connection", addr)
            self.handler_obj.fib_handler(client)


class MasterServer:
    """
    Master Server class (Master Process) which spins number of worker pool to manage connections and process request
    """
    def __init__(self):
        self.handler_obj = Handler()
        self.worker_process = WorkerProcess()

    def start(self, address):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(address)
        sock.listen(5)
        w_process = [Process(target=self.worker_process.start, args=(sock,)) for i in
                     range(num_workers)]
        for _p in w_process:
            # _p = w_process.pop()
            _p.daemon = True
            _p.start()
        while True:
            print("Master Process is UP!")
            time.sleep(10)


if __name__ == '__main__':
    fib_server = MasterServer()
    fib_server.start(('', 26000))
