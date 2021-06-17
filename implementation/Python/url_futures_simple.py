"""
Test de concurrence avec futures.

Plusieurs requêtes sont envoyées de manière parallèle à un site web
et les résultats traités au fur et à mesure de leur retour.

Author: Dalker (daniel.kessler@dalker.org)
Date: 2021-03-10
"""

import bisect
import requests
import sys
import time
import concurrent.futures as fut


WORDS = ("clause", "concurrent", "expression", "future", "grammar", "language",
         "list", "semantics", "sentence", "syntax", "type", "word")


def remote_define(word):
    """Trouver la définition la plus courante d'un mot en anglais en-ligne."""
    # solliciter une page web pour obtenir la définition du mot demandé
    reqres = requests.get("https://www.merriam-webster.com/dictionary/" + word)
    # extraire la définition de la page web reçue (bidouillage...)
    definition = (reqres.text.replace("\n", " ")
                  .split(r'<span class="num">1')[1]
                  .split(r'</strong>')[1]
                  .split(r'</span')[0]
                  .split(r'<span')[0]
                  .split(r'<strong')[0]
                  .split(r'(see ')[0]
                  .strip())
    return (word, definition)


def sequentiel():
    """Demander des définitions de manière séquentielle."""
    defs = []
    for word in WORDS:
        defs.append(remote_define(word))
    return defs


def concurrent():
    """Demander des définitions de manière concurrente."""
    with fut.ThreadPoolExecutor() as executor:
        define_calls = (executor.submit(remote_define, word) for word in WORDS)
        defs = []
        for future in fut.as_completed(define_calls):
            defs.append(future.result())
    return sorted(defs)


def time_this(test):
    """Chronomètre le temps d'exécution d'une fonction."""
    start = time.time()
    res = test()
    elapsed = time.time() - start
    return elapsed


def comparative_test(n_tests):
    """Comparer la performance d'appels à url séquentiels vs. concurrents."""
    print(f"* {n_tests} tests alternés sans affichage *:")
    print("              séq.   concurrent")
    gtot1 = gtot2 = 0
    for n in range(n_tests):
        tot1 = time_this(sequentiel)
        tot2 = time_this(concurrent)
        gtot1 += tot1
        gtot2 += tot2
        print("    Temps {:2d}: {:.4f} {:.4f}".format(n+1, tot1, tot2))
    print("Temps moyens: {:.4f} {:.4f}".format(gtot1/n_tests, gtot2/n_tests))

if __name__ == "__main__":
    comparative_test(10)
