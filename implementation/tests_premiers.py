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
import threading
import concurrent.futures


class MyFuture:
    """Future implémenté "à la main" à partir de locks."""

    def __init__(self, func, *param):
        """Inintialiser le future."""
        self.result = None
        self.done = False
        self.lock = threading.Condition()
        self.thread = threading.Thread(target=self.wrapper, args=(func, param))
        self.thread.setName("FutureThread")
        self.thread.start()

    def wrapper(self, func, param):
        """Run the actual function and let us housekeep around it."""
        self.lock.acquire()
        try:
            self.result = func(*param)
        except Exception as err:
            self.result = f"Exception {err} raised within Future"
        self.done = True
        self.lock.notify()
        self.lock.release()


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


def futureThreadsWithLocks_test():
    """Tester primalité avec "Futures" réalisés avec locks (à la main)."""
    res = []
    futures = [MyFuture(is_prime, a[i]) for i in range(len(a))]
    # acquérir les résultats au fur et à mesure qu'ils sont complétés
    while futures:
        for f in futures:
            if f.done:
                res.append(f.result)
                futures.remove(f)
        time.sleep(.001)  # éviter de ralentir le cpu avec tests trop fréquents
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
    with concurrent.futures.ProcessPoolExecutor() as process_executor:
        define_processes = (process_executor.submit(is_prime, i) for i in a)
        res = []
        for future in concurrent.futures.as_completed(define_processes):
            res.append(future.result())
    return res


if __name__ == "__main__":
    # 10 tests sur le même calcul
    a = [67280421310721 for _ in range(10)]
    for f in [seq_test,
              futureThreadsWithLocks_test,
              future_Threads_import_test,
              future_Processes_import_test]:
        start = time.time()
        print("\nJe vérifie les nombres premiers avec la fonction", f.__name__)
        res = zip(a, f())
        # for nb, prime in res:
        #    print(nb, prime)
        end = time.time()
        print("\n", "Time elapsed:", end - start)
