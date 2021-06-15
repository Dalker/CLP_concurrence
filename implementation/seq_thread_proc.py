"""
Comparaisons de durées d'un paquet de tâches concurrentes ou pas.

Catégories de tâches:
- calcul intensif (calcul itératif d'une factorielle)
- I/O avec latence (lecture/écriture via SSH)

Méthodes pour gérer le paquet de tâche:
- séquentielle
- [concurrence par coroutines] <- désactivé pour l'instant
- concurrence par tâches
- parallèlisme par processus

Author: Dalker (daniel.kessler@dalker.org)
Date: 2021.03.22 -> 2021.06.15
"""

import asyncio
import concurrent.futures as futures
import functools
import math
import time
import sys

import paramiko  # module pour transfert de fichiers via ssh
import monssh  # données privées

WORDS = ("clause", "concurrent", "expression", "future", "grammar", "language",
         "list", "semantics", "sentence", "syntax", "type", "word")


class Tasker:
    """Série de tâches pour tests."""

    MAX_TASKS = 12

    def __init__(self, show_output=False):
        """Initialiser le paquet de tâches."""
        self.show_output = show_output
        self.task_number = 0

    def next_task(self):
        """Obtenir une référence vers la prochaine tâche."""
        raise NotImplementedError

    def reset(self):
        """Recommencer avec la première tâche."""
        self.task_number = 0


class CalcTasks(Tasker):
    """Série de tâches calculatoires."""

    def factorielle(self, n):
        """Calculer une factorielle."""
        res = 1
        for j in range(1, n):
            res *= j
        if self.show_output:
            print(f"fact({n}) = 10^{math.log10(res):.0f}")

    def next_task(self):
        """Tâche calculatoire."""
        self.task_number += 1
        n = 2**10*5*(1+self.task_number)
        return functools.partial(self.factorielle, n)


class IOTasks(Tasker):
    """Série de tâches de lecture/écriture de fichier."""

    def __init__(self, *args, **kwargs):
        """Initialiser les tâches."""
        super().__init__(*args, **kwargs)
        self.words = sorted(WORDS)

    def define(self, n):
        """Definition reading task."""
        word = self.words[n]
        local_file = f"/tmp/{word}.txt"
        remote_file = f"defs/{word}.txt"
        with paramiko.SSHClient() as ssh:
            ssh.load_system_host_keys()
            ssh.connect(monssh.SERVER, username=monssh.USER)
            with ssh.open_sftp() as sftp:
                sftp.get(remote_file, local_file)
                sftp.put(local_file, "re" + remote_file)
        if self.show_output:
            with open(local_file) as fp:
                print(word, ":", fp.read())

    def next_task(self):
        """Tâche I/O."""
        self.task_number += 1
        return functools.partial(self.define, self.task_number - 1)


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
                 # "concurrentes par coroutines (via asyncio)":
                 # self.test_asyncio,
                 "concurrentes par threads (via futures.ThreadPool)":
                 self.test_thread_pool,
                 "concurrentes par processus (via futures.ProcessPool)":
                 self.test_proc_pool,
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

    def test_asyncio(self):
        """Test de paquet de tâches concurrentes avec asyncio."""
        asyncio.run(self.concurrent_tasks_asyncio())

    @staticmethod
    async def concurrent_task_asyncio(task):
        """Do a task in a separate thread (a.k.a. "coroutine")."""
        task()

    async def concurrent_tasks_asyncio(self):
        """Test de paquet de tâches par threads concurrents."""
        await asyncio.wait([asyncio.create_task(
            self.concurrent_task_asyncio(self.tasker.next_task()))
                            for _ in range(self.n_tasks)])

    async def concurrent_tasks_asyncio_gather(self):
        """Test de paquet de tâches par threads concurrents."""
        await asyncio.gather(
            *[self.concurrent_task_asyncio(self.tasker.next_task())
              for _ in range(self.n_tasks)]
        )

    def test_thread_pool(self):
        """Test de paquet de tâches concurrent."""
        with futures.ThreadPoolExecutor() as executor:
            for _ in range(self.n_tasks):
                executor.submit(self.tasker.next_task())

    def test_proc_pool(self):
        """Test de paquet de processus parallèles."""
        with futures.ProcessPoolExecutor() as executor:
            for _ in range(self.n_tasks):
                executor.submit(self.tasker.next_task())

    def test_parallel(self):
        """Test de paquet de tâches parallèles."""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        show = True
        io = False
        calc = False
        if "-io" in sys.argv:
            io = True
        if "-calc" in sys.argv:
            calc = True
    else:
        show = False
        io = True
        calc = True

    if io:
        print("*** I/O Tasks ***")
        Tests(IOTasks, n_tasks=8, show_output=show).run()
    if show is False:
        print()
    if calc:
        print("*** Calc Tasks ***")
        Tests(CalcTasks, n_tasks=8, show_output=show).run()
