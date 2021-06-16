"""
Test comparatif entre différentes méthodes de concurrence.

Ce module compare un "Future fait à la main" à partir de locks avec les Futures
pré-implémentés par Python, en multi-thread et multi-proc, le tout comparé avec
un programme séquentiel.

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


def seq_test():
    """Tester primalité de manière séquentielle."""
    res = []
    for i in range(len(a)):
        res.append(is_prime(a[i]))
    return res


def future_Threads_import_test():
    """Tester primalité avec Futures de librairie standard en multi-thread."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        define_calls = (executor.submit(is_prime, i) for i in a)
        res = []
        for future in concurrent.futures.as_completed(define_calls):
            res.append(future.result())
    return res


def future_Processes_import_test():
    """Tester primalité avec Futures de librairie standard en multi-process."""
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        define_calls = (executor.submit(is_prime, i) for i in a)
        res = []
        for future in concurrent.futures.as_completed(define_calls):
            res.append(future.result())
    return res


if __name__ == "__main__":
    # 10 tests sur le même calcul
    a = [67280421310721 for _ in range(10)]
    for f in [future_Processes_import_test, seq_test,
              future_Threads_import_test]:
        start = time.time()
        print("\nJe vérifie les nombres premiers avec la fonction", f.__name__)
        result = zip(a, f())
        # for nb, prime in res:
        #    print(nb, prime)
        end = time.time()
        print("\n", "Time elapsed:", end - start)
