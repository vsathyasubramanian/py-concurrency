def fib(n):
    if n <= 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def _fibbonacci_generator(n, fibArray):
    for i in range(2, n + 1):
        yield fibArray[i - 1] + fibArray[i - 2]


def fib_generator(n):
    fibArray = [0, 1]
    for v in _fibbonacci_generator(n, fibArray):
        fibArray.append(v)
        yield '', 'repeat'
    yield fibArray[n], 'res'
