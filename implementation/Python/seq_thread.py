"""
Comparaisons de durées d'un paquet de tâches concurrentes ou pas.

Catégorie de tâches:
- I/O avec latence (lecture/écriture via SSH)

Méthodes pour gérer le paquet de tâche:
- séquentielle
- concurrence par tâches avec:
  - Future implémenté "à la main"
  - Future avec ThreadPoolExecutor pré-existant

Author: Dalker (daniel.kessler@dalker.org)
Date: 2021.03.22 -> 2021.06.15
"""

import concurrent.futures as futures
import time
import sys
import threading

import tasks


class Tests:
    """Tests comparatifs séquentiel/concurrent/parallèle."""

    def __init__(self, tasker, n_tasks=5, show_output=False):
        """Initialiser une batterie de tests."""
        self.tasker = tasker(show_output=show_output)
        self.n_tasks = n_tasks
        self.show_output = show_output

    def run(self):
        """Effectuer les tests."""
        tests = {"séquentielles": self.test_seq,
                 "concurrentes par threads (via futures \"naïfs\")":
                 self.test_futures_naifs,
                 "concurrentes par threads (via futures.ThreadPool)":
                 self.test_thread_pool,
                 }
        for name, test in tests.items():
            self.tasker.reset()
            print(f"* test de {self.n_tasks} tâches {name} *")
            start = time.perf_counter()
            test()
            elapsed = time.perf_counter() - start
            if self.show_output:
                print(f"\n----< temps écoulé: {elapsed:.3g} s >----\n")
            else:
                print(f"  temps écoulé: {elapsed:.3g} s")

    def test_seq(self):
        """Test de paquet de tâches séquentiel."""
        for _ in range(self.n_tasks):
            self.tasker.next_task()()

    def test_futures_naifs(self):
        """Test de paquet de tâches avec futures "naïfs"."""
        futures = []
        for _ in range(self.n_tasks):
            futures.append(MyFuture(self.tasker.next_task()))
        while futures:  # ceci est semblable a un "event queue"
            for future in futures:
                if future.done:
                    futures.remove(future)
            time.sleep(.001)  # lâcher le processus et le processeur un moment

    def test_thread_pool(self):
        """Test de paquet de tâches avec futures et thread pool."""
        with futures.ThreadPoolExecutor() as executor:
            for _ in range(self.n_tasks):
                executor.submit(self.tasker.next_task())


class MyFuture:
    """Futures sur threads implémentés "à la main" à partir de locks."""

    def __init__(self, task):
        """Initialiser un Future."""
        self.done = False
        self.result = None
        self._task = task
        # pas besoin de lock vu que le thread est créé sur place
        # et n'est référencé nulle part ailleurs (privé au Future)
        self.__thread = threading.Thread(target=self._target)
        self.__thread.start()

    def _target(self):
        """Travail à effectuer par le thread dédié."""
        self.result = self._task()
        self.done = True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        show = True
    else:
        show = False

    print("*** I/O Tasks ***")
    Tests(tasks.IOTasks, n_tasks=8, show_output=show).run()
