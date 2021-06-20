"""
Implémentation "maison" de Futures minimaux basés sur Thread privée.

Author: Dalker (daniel.kessler@dalker.org)
Date: 2021-06-20
"""
import threading


class FutureNaif:
    """Future implémenté "à la main", avec thread privé."""

    def __init__(self, task):
        """Initialiser un Future."""
        self.done = False  # permettre au "client" de vérifier si c'est fini
        self.result = None  # accès au résultat quand disponible
        self._task = task
        # pas besoin de lock vu que le thread est créé sur place
        # et n'est référencé nulle part ailleurs (privé au Future)
        self.__thread = threading.Thread(target=self._target)
        self.__thread.start()

    def _target(self):
        """Travail à effectuer par le thread dédié."""
        self.result = self._task()
        self.done = True
