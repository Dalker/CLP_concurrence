"""
Comparaisons de durées d'un paquet de tâches concurrentes ou pas.

Catégorie de tâches:
- I/O avec latence (lecture/écriture via SSH)
- calcul intensif (calcul itératif d'une factorielle)

Méthodes pour gérer le paquet de tâche:
- séquentielle
- concurrence par tâches avec:
  - Future avec Threads implémenté "à la main"
  - Future avec ThreadPoolExecutor pré-existant
  - Future avec ProcessPoolExecutor pré-existant

Usage:
  futurs_compares --io [-s]
  futurs_compares --calc [-s]

Options:
  --io: effectuer des tâches I/O avec latence
  --calc: effectuer des tâches de calcul intensif
  -s: montrer le résultat des tâches individuelles

Author: Dalker (daniel.kessler@dalker.org)
Date: 2021.06.20
"""

import concurrent.futures
import docopt
import time

import gentasks
from futurs_naifs import FutureNaif


class Tests:
    """
    Tests comparatifs séquentiel/concurrent/parallèle.

    Attributs:
      - tasker: générateur de tâches
      - n_tasks: nombre de tâches à effectuer dans chaque implémentation
      - show_output: afficher la sortie des tâches? (booléen)
    """

    def __init__(self, tasker, n_tasks=5, show_output=False):
        """Initialiser une batterie de tests."""
        self._tasks = None
        self.tasker = tasker
        self.n_tasks = n_tasks
        self.show_output = show_output

    def run(self):
        """Effectuer les tests."""
        tests = {"séquentielles": self.test_seq,
                 "concurrentes par threads (via futures \"naïfs\")":
                 self.test_futures_naifs,
                 "concurrentes par threads (via futures.ThreadPool)":
                 self.test_thread_pool,
                 "concurrentes par process (via futures.ProcessPool)":
                 self.test_proc_pool,
                 }
        for name, test in tests.items():
            self._tasks = self.tasker(self.n_tasks)
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
        for task in self._tasks:
            res = task()
            if self.show_output:
                print(res)

    def test_futures_naifs(self):
        """Test de paquet de tâches avec futures "naïfs"."""
        futures = []
        pending = []
        for task in self._tasks:
            future = FutureNaif(task)
            futures.append(future)
            pending.append(future)
        while pending:  # vérifier quels futurs sont complétés
            for future in pending:
                if future.done:
                    pending.remove(future)
            time.sleep(.001)  # lâcher le processus et le processeur un moment
        if self.show_output:
            for future in futures:
                print(future.result)

    def test_thread_pool(self):
        """Test de paquet de tâches avec futures et thread pool."""
        futures = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for task in self._tasks:
                futures.append(executor.submit(task))
        if self.show_output:
            for future in futures:
                print(future.result())

    def test_proc_pool(self):
        """Test de paquet de tâches avec futures et process pool."""
        futures = []
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for task in self._tasks:
                futures.append(executor.submit(task))
        if self.show_output:
            for future in futures:
                print(future.result())


if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    show = options["-s"]
    n_tasks = 8
    if options["--io"]:
        print("*** Tâches intensives en I/O avec latence ***")
        Tests(gentasks.IOTasks, n_tasks, show_output=show).run()
    elif options["--calc"]:
        print("*** Tâches intensives en calcul ***")
        Tests(gentasks.CalcTasks, n_tasks, show_output=show).run()
