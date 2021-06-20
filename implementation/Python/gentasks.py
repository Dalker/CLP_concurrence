"""
Itérateurs fournissant des tâches.

Catégories de tâches:
- calcul intensif (calcul itératif d'une factorielle)
- I/O avec latence (lecture/écriture via SSH)

Author: Dalker (daniel.kessler@dalker.org)
Date: 2021.06.20
"""

import functools
import math

import paramiko  # module pour transfert de fichiers via ssh
import monssh  # données privées

WORDS = ("clause", "concurrent", "expression", "future", "grammar", "language",
         "list", "semantics", "sentence", "syntax", "type", "word")


class GenTasks:
    """
    Générateur de tâches pour tests.

    Attributs:
      - n_tasks: nombre de tâches à effectuer
    """

    MAX_TASKS = 12

    def __init__(self, n_tasks=MAX_TASKS):
        """Initialiser le paquet de tâches."""
        self.n_tasks = n_tasks
        self.__current_task = 0

    def __iter__(self):
        """Se déclarer en tant qu'itérateur."""
        return self

    def __next__(self):
        """Obtenir une référence vers la prochaine tâche."""
        if self.__current_task < self.n_tasks:
            self.__current_task += 1
            return functools.partial(self.task, self.__current_task)
        raise StopIteration

    def task(self, n):
        """Tâche à effectuer."""
        raise NotImplementedError

    def reset(self):
        """Recommencer avec la première tâche."""
        self.task_number = 0


class CalcTasks(GenTasks):
    """Série de tâches calculatoires."""

    def task(self, task_n):
        """Calculer une factorielle."""
        n = 2**10 * 5 * (1+task_n)
        res = 1
        for j in range(1, n):
            res *= j
        return f"fact({n}) = 10^{math.log10(res):.0f}"


class IOTasks(GenTasks):
    """Série de tâches de lecture/écriture de fichier."""

    def __init__(self, *args, **kwargs):
        """Initialiser les tâches."""
        super().__init__(*args, **kwargs)
        self.words = sorted(WORDS)

    def task(self, n):
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
        with open(local_file) as fp:
            result = f"{word} : {fp.read()}"
        return result
