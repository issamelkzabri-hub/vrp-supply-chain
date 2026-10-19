"""Étape 4 : heuristique des économies de Clarke et Wright (version parallèle)."""
from pathlib import Path

import pandas as pd

from glouton import plus_proche_voisin
from lecture import lire_instance
from verification import verifier


def clarke_wright(inst):
    n, d = inst.n, inst.dist

    # Départ : chaque client a sa propre tournée aller-retour depuis le dépôt
    routes = {i: [i] for i in range(1, n)}                # id -> clients de la tournée
    route_de = {i: i for i in range(1, n)}                # client -> id de sa tournée
    charge = {i: inst.demandes[i] for i in range(1, n)}   # id -> charge de la tournée

    # Économie de la fusion de i et j : s_ij = d(0,i) + d(0,j) - d(i,j), triées de la plus grande à la plus petite
    economies = sorted(
        ((d[0][i] + d[0][j] - d[i][j], i, j)
         for i in range(1, n) for j in range(i + 1, n)),
        reverse=True)

    for s, i, j in economies:
        if s <= 0:
            break                                   # plus aucun gain possible
        ri, rj = route_de[i], route_de[j]
        if ri == rj:
            continue                                # déjà dans la même tournée
        if charge[ri] + charge[rj] > inst.capacite:
            continue                                # la fusion dépasserait la capacité
        a, b = routes[ri], routes[rj]
        if i not in (a[0], a[-1]) or j not in (b[0], b[-1]):
            continue                                # i et j doivent être aux extrémités
        if a[-1] != i:
            a.reverse()                             # on met i à la fin de a
        if b[0] != j:
            b.reverse()                             # et j au début de b
        a.extend(b)                                 # fusion : ... i -> j ...
        for c in b:
            route_de[c] = ri
        charge[ri] += charge[rj]
        del routes[rj], charge[rj]

    return [[0] + r + [0] for r in routes.values()]


if __name__ == "__main__":
    racine = Path(__file__).resolve().parent.parent
    lignes = []
    print(f"{'instance':<11}{'optimum':>8}{'glouton':>9}{'C-W':>7}{'camions':>9}{'utilisés':>9}"
          f"{'écart C-W':>11}{'écart glouton':>15}")
    for fichier in sorted((racine / "data").glob("*.vrp")):
        inst = lire_instance(fichier)
        d_nn = verifier(inst, plus_proche_voisin(inst))
        tournees = clarke_wright(inst)
        d_cw = verifier(inst, tournees)
        e_cw = (d_cw - inst.optimum) / inst.optimum * 100
        e_nn = (d_nn - inst.optimum) / inst.optimum * 100
        print(f"{inst.nom:<11}{inst.optimum:>8}{d_nn:>9}{d_cw:>7}{inst.nb_camions:>9}{len(tournees):>9}"
              f"{e_cw:>10.1f}%{e_nn:>14.1f}%")
        lignes.append({"instance": inst.nom, "clarke_wright": d_cw,
                       "camions_cw": len(tournees), "ecart_cw_pct": round(e_cw, 2)})

    # Ajoute les colonnes Clarke-Wright à results/comparaison.csv s'il existe
    chemin = racine / "results" / "comparaison.csv"
    if chemin.exists():
        df = pd.read_csv(chemin)
        df = df.drop(columns=["clarke_wright", "camions_cw", "ecart_cw_pct"], errors="ignore")
        df = df.merge(pd.DataFrame(lignes), on="instance", how="left")
        df.to_csv(chemin, index=False)
        print("\nColonnes Clarke-Wright ajoutées à results/comparaison.csv")