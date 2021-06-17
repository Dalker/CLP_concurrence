"""
Test comparatif entre différentes méthodes de concurrence.

Les tests sont faits avec un test de primalité, intensif en calcul CPU. On
s'attend donc à ce que le multi-process soit plus efficace.

@author: Bâr (puis quelques modifs par Dalker)
@date: mars 2021
"""

import math
import time
import concurrent.futures


def is_prime(n):
    """Retourner vrai si n est premier, faux sinon."""
    if n < 1 or n % 1 > 0:
        return False
    if n == 1 or n == 2:
        return True
    for i in range(3, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def sequentiel():
    """Tester primalité de manière séquentielle."""
    res = []
    for i in range(len(a)):
        res.append(is_prime(a[i]))
    return res


def future_Threads():
    """Tester primalité avec Futures en multi-thread."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        define_calls = (executor.submit(is_prime, i) for i in a)
        res = []
        for future in concurrent.futures.as_completed(define_calls):
            res.append(future.result())
    return res


def future_Processes():
    """Tester primalité avec Futures en multi-process."""
    with concurrent.futures.ProcessPoolExecutor() as executor:
        define_calls = (executor.submit(is_prime, i) for i in a)
        res = []
        for future in concurrent.futures.as_completed(define_calls):
            res.append(future.result())
    return res


if __name__ == "__main__":
    # 10 tests sur le même calcul
    a = [67280421310721 for _ in range(10)]
    print("\nVérification 10 fois de la primalité de 67280421310721")
    for f in [sequentiel,
              future_Threads,
              future_Processes]:
        start = time.time()
        print("\n", f.__name__, ":")
        result = zip(a, f())
        # for nb, prime in res:
        #    print(nb, prime)
        end = time.time()
        print("{:.2f}s".format(end - start))
