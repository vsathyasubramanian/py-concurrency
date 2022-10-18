def fib(n):
    """
    Unoptimized recursive function to stress the CPU
    :param n:
    :type n:
    :return:
    :rtype:
    """
    if n <= 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def _fibonacci_generator(n, fib_array):
    """
    Inner function to iterate through the generator and generate the nth fibonacci number
    :param n:
    :type n:
    :param fib_array:
    :type fib_array:
    :return:
    :rtype:
    """
    for i in range(2, n + 1):
        yield fib_array[i - 1] + fib_array[i - 2]


def fib_generator(n):
    """
    Main async - generator based method to generate the nth fibonacci number
    :param n:
    :type n:
    :return:
    :rtype:
    """
    fib_array = [0, 1]
    for v in _fibonacci_generator(n, fib_array):
        fib_array.append(v)
        yield '', 'repeat'
    yield fib_array[n], 'res'
