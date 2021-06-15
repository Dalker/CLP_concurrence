"""
Test de concurrence avec futures.

Plusieurs requêtes sont envoyées de manière parallèle à l'OS
et les résultats traités au fur et à mesure de leur retour.

Author: Dalker (daniel.kessler@dalker.org)
Date: 2021.03.20
"""

import bisect
import sys
import time
import concurrent.futures


WORDS = ("clause", "concurrent", "expression", "future", "grammar", "language",
         "list", "semantics", "sentence", "syntax", "type", "word")


def local_define(word):
    """Trouver la définition la plus courante d'un mot dans un fichier."""
    with open(f"defs/{word}.txt") as thefile:
        definition = thefile.readline()
    return (word, definition)


def sequential_defs():
    """Demander des définitions de manière séquentielle, dans l'ordre."""
    defs = []
    for word in WORDS:
        defs.append(local_define(word))
    return defs


def concurrent_defs_endsort():
    """
    Demander des définitions de manière concurrente.

    Dans cette variante, on les remet dans l'ordre à la fin.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        define_calls = (executor.submit(local_define, word) for word in WORDS)
        defs = []
        for future in concurrent.futures.as_completed(define_calls):
            defs.append(future.result())
    return sorted(defs)


def concurrent_defs_insert():
    """
    Demander des définitions de manière concurrente.

    Dans cette variante, on les classe au fur et à mesure, par insertion.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        define_calls = (executor.submit(local_define, word) for word in WORDS)
        resultats = []
        for future in concurrent.futures.as_completed(define_calls):
            res = future.result()
            bisect.insort(resultats, res)
    return resultats


def time_this(test, name=None):
    """Tester la vitesse d'une fonction."""
    start = time.time()
    res = test()
    elapsed = time.time() - start
    if name is not None:
        print("-=", name, "faite en", elapsed, "s =-")
        for w, d in res:
            print(w, ":", d)
        print()
    return elapsed


def comparative_test(n_tests, m_tests=1):
    """Comparer la performance d'appels à url séquentiels vs. concurrents."""
    if m_tests > 1:
        print("* {} séries de {} tests alternés de chaque sans affichage *:"
              .format(n_tests, m_tests))
    else:
        print(f"* {n_tests} tests alternés sans affichage *:")
    print("              séq.   cc.end cc.ins")
    gtot1 = gtot2 = gtot3 = 0
    for n in range(n_tests):
        tot1 = tot2 = tot3 = 0
        for _ in range(m_tests):
            tot1 += time_this(sequential_defs)*1000
            tot2 += time_this(concurrent_defs_endsort)*1000
            tot3 += time_this(concurrent_defs_insert)*1000
        gtot1 += tot1
        gtot2 += tot2
        gtot3 += tot3
        print("    Temps {:2d}: {:.4f} {:.4f} {:.4f}".format(n+1,
                                                             tot1/m_tests,
                                                             tot2/m_tests,
                                                             tot3/m_tests))
    print("Temps moyens: {:.4f} {:.4f} {:.4f}".format(gtot1/(n_tests*m_tests),
                                                      gtot2/(n_tests*m_tests),
                                                      gtot3/(n_tests*m_tests)))


def print_usage():
    """Afficher les options en ligne de commande du programme."""
    print(sys.argv[0], ":",
          "demander des définitions à un dictionnaire local")
    print("OPTIONS")
    print("  seq : méthode séquentielle")
    print("  end : méthode concurrente avec tri à la fin de tous les threads")
    print("  ins : méthode concurrente avec insertion triée dès arrivée")
    print("  <N> : effectuer N tests comparatifs de durée des trois méthodes")
    print("  <N> <M>: effectuer N séries de M tests")


if __name__ == "__main__":
    try:
        choice = sys.argv[1]
    except IndexError:
        print_usage()
        exit()
    if choice == 'seq':
        time_this(sequential_defs, "Méthode séquentielle")
    elif choice == 'end':
        time_this(concurrent_defs_endsort,
                  "Méthode concurrente avec sort final")
    elif choice == 'ins':
        time_this(concurrent_defs_insert, "Méthode concurrente avec insertion")
    else:
        try:
            n = int(choice)
        except ValueError:
            print_usage()
        else:
            comparative_test(n)
