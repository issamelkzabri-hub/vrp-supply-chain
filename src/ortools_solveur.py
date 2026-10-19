"""Étape 3 : résolution du CVRP avec OR-Tools (recherche locale guidée)."""
import time
from pathlib import Path

import pandas as pd
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from glouton import plus_proche_voisin
from lecture import lire_instance
from verification import verifier

LIMITE_S = 30  # même limite de temps pour toutes les instances


def resoudre_ortools(inst, nb_camions=None, limite_s=LIMITE_S):
    if nb_camions is None:
        nb_camions = inst.nb_camions

    # 1) Gestionnaire d'index : traduit entre noeuds (0..n-1) et indices internes d'OR-Tools
    manager = pywrapcp.RoutingIndexManager(inst.n, nb_camions, 0)  # 0 = dépôt
    routing = pywrapcp.RoutingModel(manager)

    # 2) Coût d'un arc = distance entre les deux noeuds
    def cout(i, j):
        return inst.dist[manager.IndexToNode(i)][manager.IndexToNode(j)]

    transit = routing.RegisterTransitCallback(cout)
    routing.SetArcCostEvaluatorOfAllVehicles(transit)

    # 3) Contrainte de capacité : la charge cumulée d'un camion reste <= capacité
    def demande(i):
        return inst.demandes[manager.IndexToNode(i)]

    d = routing.RegisterUnaryTransitCallback(demande)
    routing.AddDimensionWithVehicleCapacity(
        d, 0, [inst.capacite] * nb_camions, True, "Capacite")

    # 4) Paramètres de recherche
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = limite_s

    # 5) Résolution
    solution = routing.SolveWithParameters(params)
    if solution is None:
        return None

    # 6) Extraction des tournées
    tournees = []
    for v in range(nb_camions):
        index = routing.Start(v)
        tournee = [0]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            tournee.append(manager.IndexToNode(index))
        if len(tournee) > 2:  # on ignore les camions inutilisés ([0, 0])
            tournees.append(tournee)
    return tournees


if __name__ == "__main__":
    racine = Path(__file__).resolve().parent.parent
    lignes = []
    print(f"Limite de temps OR-Tools : {LIMITE_S} s par instance\n")
    print(f"{'instance':<11}{'optimum':>8}{'glouton':>9}{'ortools':>9}{'camions':>9}"
          f"{'écart opt.':>11}{'gain/glouton':>14}")

    for fichier in sorted((racine / "data").glob("*.vrp")):
        inst = lire_instance(fichier)

        d_glouton = verifier(inst, plus_proche_voisin(inst))

        k = inst.nb_camions
        tournees = resoudre_ortools(inst, k)
        if tournees is None:  # pas de solution avec k camions : on essaie k+1
            k += 1
            tournees = resoudre_ortools(inst, k)
        d_ortools = verifier(inst, tournees)

        ecart = (d_ortools - inst.optimum) / inst.optimum * 100
        gain = (d_glouton - d_ortools) / d_glouton * 100
        print(f"{inst.nom:<11}{inst.optimum:>8}{d_glouton:>9}{d_ortools:>9}{len(tournees):>9}"
              f"{ecart:>10.1f}%{gain:>13.1f}%")
        lignes.append({"instance": inst.nom, "clients": inst.n - 1, "optimum": inst.optimum,
                       "glouton": d_glouton, "ortools": d_ortools,
                       "camions_ortools": len(tournees), "camions_alloues": k,
                       "ecart_optimum_pct": round(ecart, 2), "gain_vs_glouton_pct": round(gain, 2)})

    (racine / "results").mkdir(exist_ok=True)
    pd.DataFrame(lignes).to_csv(racine / "results" / "comparaison.csv", index=False)
    print("\nRésultats enregistrés dans results/comparaison.csv")