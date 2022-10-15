# coding=utf-8
import multiprocessing
import pickle
import socket
from io import BytesIO

from fib import fib


def forking_dumps(obj):
    buf = BytesIO()
    multiprocessing.reduction.ForkingPickler(buf).dump(obj)
    return buf.getvalue()


def process_sockets(queue):
    while True:
        # fd = multiprocessing.reduction.rebuild_handle(queue.get())
        # client = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        client = pickle.loads(queue.get())

        while True:
            req = client.recv(100)
            if not req:
                break
            n = int(req)
            result = fib(n)
            resp = str(result).encode('ascii') + b'\n'
            client.send(resp)


num_worker = 3


class ProcessServer:
    def __init__(self):
        pass

    def start(self, address):
        queue = multiprocessing.Queue()

        process_list = [multiprocessing.Process(target=process_sockets, args=(queue,)) for i in range(num_worker)]
        for process in process_list:
            process.daemon = True
            process.start()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(address)
        sock.listen(5)
        while True:
            client, addr = sock.accept()
            print("Connection", addr)
            # queue.put(
            #     multiprocessing.reduction.reduce_handle(client.fileno())
            # )
            queue.put(
                forking_dumps(client)
            )


if __name__ == "__main__":
    fib_server = ProcessServer()
    fib_server.start(('', 26000))
