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
import concurrent.futures


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


def concurrent_defs_endsort():
    """
    Demander des définitions de manière concurrente.

    Dans cette variante, on les remet dans l'ordre à la fin.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        define_calls = (executor.submit(remote_define, word) for word in WORDS)
        defs = []
        for future in concurrent.futures.as_completed(define_calls):
            defs.append(future.result())
    return sorted(defs)


if __name__ == "__main__":
    dico = concurrent_defs_endsort()
    for word, thedef in dico:
        with open(f"defs/{word}.txt", "w") as thefile:
            thefile.write(thedef)
