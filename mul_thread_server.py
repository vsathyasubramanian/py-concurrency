# coding=utf-8


from socket import *
from threading import Thread

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


class ThreadServer:
    def __init__(self):
        self.handler_obj = Handler()

    def start(self, address):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(address)
        sock.listen(5)
        while True:
            client, addr = sock.accept()
            print("Connection", addr)
            Thread(target=self.handler_obj.fib_handler, args=(client,), daemon=True).start()


if __name__ == '__main__':
    fib_server = ThreadServer()
    fib_server.start(('', 25000))
