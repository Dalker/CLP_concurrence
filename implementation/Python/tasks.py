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

import functools
import math

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
