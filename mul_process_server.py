# coding=utf-8
import time
from multiprocessing import Process
from socket import *

from fib import fib


class Handler:
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


num_workers = 3


class WorkerProcess:
    def __init__(self):
        self.handler_obj = Handler()

    def start(self, sock):
        while True:
            client, addr = sock.accept()
            print("Connection", addr)
            self.handler_obj.fib_handler(client)


class MasterServer:
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
        for p in w_process:
            p.daemon = True
            p.start()
        while True:
            print("Master Process is UP!")
            time.sleep(10)


if __name__ == '__main__':
    fib_server = MasterServer()
    fib_server.start(('', 25000))
