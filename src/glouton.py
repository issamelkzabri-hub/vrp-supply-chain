"""Étape 2 : heuristique gloutonne du plus proche voisin avec capacité."""
from pathlib import Path

from lecture import lire_instance
from verification import verifier


def plus_proche_voisin(inst):
    assert max(inst.demandes) <= inst.capacite, "un client dépasse la capacité d'un camion"

    non_visites = list(range(1, inst.n))  # tous les clients (le dépôt est l'indice 0)
    tournees = []

    while non_visites:                    # tant qu'il reste des clients : nouveau camion
        tournee = [0]                     # le camion part du dépôt
        charge = 0
        actuel = 0

        while True:
            # clients non visités qui rentrent encore dans la capacité restante
            candidats = [c for c in non_visites
                         if charge + inst.demandes[c] <= inst.capacite]
            if not candidats:
                break                     # plus personne ne rentre : on rentre au dépôt
            suivant = min(candidats, key=lambda c: inst.dist[actuel][c])
            tournee.append(suivant)
            charge += inst.demandes[suivant]
            non_visites.remove(suivant)
            actuel = suivant

        tournee.append(0)                 # retour au dépôt
        tournees.append(tournee)

    return tournees


if __name__ == "__main__":
    dossier = Path(__file__).resolve().parent.parent / "data"
    print(f"{'instance':<11}{'camions':>8}{'utilisés':>9}{'distance':>9}{'optimum':>9}{'écart %':>9}")
    for fichier in sorted(dossier.glob("*.vrp")):
        inst = lire_instance(fichier)
        tournees = plus_proche_voisin(inst)
        distance = verifier(inst, tournees)
        ecart = (distance - inst.optimum) / inst.optimum * 100
        print(f"{inst.nom:<11}{inst.nb_camions:>8}{len(tournees):>9}{distance:>9}"
              f"{inst.optimum:>9}{ecart:>8.1f}%")