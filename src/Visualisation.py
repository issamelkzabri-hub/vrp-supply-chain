"""Étape 5 : tracé des tournées des trois méthodes sur une instance."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # écrit directement un fichier image
import matplotlib.pyplot as plt

from clarke_wright import clarke_wright
from glouton import plus_proche_voisin
from lecture import lire_instance
from ortools_solveur import resoudre_ortools
from verification import verifier


def tracer(ax, inst, tournees, nom_methode):
    couleurs = plt.get_cmap("tab10")
    for k, t in enumerate(tournees):
        xs = [inst.coords[c][0] for c in t]
        ys = [inst.coords[c][1] for c in t]
        ax.plot(xs, ys, "-", color=couleurs(k % 10), linewidth=1.5)           # la tournée
        ax.plot(xs[1:-1], ys[1:-1], "o", color=couleurs(k % 10), markersize=4)  # ses clients
    x0, y0 = inst.coords[0]
    ax.plot(x0, y0, "*", color="black", markersize=15, zorder=5)               # le dépôt

    distance = verifier(inst, tournees)
    ecart = (distance - inst.optimum) / inst.optimum * 100
    ax.set_title(f"{nom_methode}\ndistance {distance} (+{ecart:.1f} % vs optimum), "
                 f"{len(tournees)} tournées", fontsize=10)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def figure_instance(nom, racine):
    inst = lire_instance(racine / "data" / f"{nom}.vrp")

    t_nn = plus_proche_voisin(inst)
    t_cw = clarke_wright(inst)
    t_or = resoudre_ortools(inst, inst.nb_camions)
    if t_or is None:  # pas de solution avec k camions : on essaie k+1
        t_or = resoudre_ortools(inst, inst.nb_camions + 1)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    tracer(axes[0], inst, t_nn, "Plus proche voisin")
    tracer(axes[1], inst, t_cw, "Clarke-Wright")
    tracer(axes[2], inst, t_or, "OR-Tools (30 s)")
    fig.suptitle(f"{inst.nom} : {inst.n - 1} clients, optimum connu = {inst.optimum}", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.93])

    sortie = racine / "results" / f"tournees_{nom}.png"
    sortie.parent.mkdir(exist_ok=True)
    fig.savefig(sortie, dpi=150)
    plt.close(fig)
    print("Figure enregistrée :", sortie)


if __name__ == "__main__":
    racine = Path(__file__).resolve().parent.parent
    noms = sys.argv[1:] or ["A-n32-k5", "A-n54-k7"]
    for nom in noms:
        figure_instance(nom, racine)