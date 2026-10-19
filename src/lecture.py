"""Étape 1 : lecture des instances CVRP au format TSPLIB (jeu A d'Augerat)."""
import math
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Instance:
    nom: str
    capacite: int      # capacité de chaque camion
    nb_camions: int    # nombre de camions annoncé dans le fichier
    optimum: int       # distance optimale connue (référence)
    coords: list       # coords[i] = (x, y) ; indice 0 = dépôt
    demandes: list     # demandes[i] = demande du noeud i ; demandes[0] = 0
    dist: list         # dist[i][j] = distance arrondie entre les noeuds i et j

    @property
    def n(self):
        """Nombre de noeuds, dépôt inclus."""
        return len(self.coords)


def distance(a, b):
    """Distance euclidienne arrondie à l'entier le plus proche (convention EUC_2D de TSPLIB)."""
    return int(math.hypot(a[0] - b[0], a[1] - b[1]) + 0.5)


def lire_instance(chemin):
    nom = capacite = nb_camions = optimum = dimension = None
    coords, demandes = [], []
    section = None  # section du fichier dans laquelle on se trouve

    for ligne in Path(chemin).read_text().splitlines():
        ligne = ligne.strip()
        if not ligne or ligne == "EOF":
            continue

        # 1) Changement de section ?
        if ligne.startswith("NODE_COORD_SECTION"):
            section = "coords"
        elif ligne.startswith("DEMAND_SECTION"):
            section = "demandes"
        elif ligne.startswith("DEPOT_SECTION"):
            section = "depot"

        # 2) Sinon, on lit la ligne selon la section courante
        elif section is None:  # en-tête : lignes "CLE : valeur"
            cle, valeur = [s.strip() for s in ligne.split(":", 1)]
            if cle == "NAME":
                nom = valeur
            elif cle == "DIMENSION":
                dimension = int(valeur)
            elif cle == "CAPACITY":
                capacite = int(valeur)
            elif cle == "COMMENT":
                nb_camions = int(re.search(r"No of trucks:\s*(\d+)", valeur).group(1))
                optimum = int(re.search(r"Optimal value:\s*(\d+)", valeur).group(1))
        elif section == "coords":  # "numéro x y"
            _, x, y = ligne.split()
            coords.append((float(x), float(y)))
        elif section == "demandes":  # "numéro demande"
            _, q = ligne.split()
            demandes.append(int(q))
        # section "depot" : le dépôt est le noeud 1 (indice 0), rien à lire

    # Vérifications de cohérence
    assert len(coords) == dimension, "nombre de coordonnées différent de DIMENSION"
    assert len(demandes) == dimension, "nombre de demandes différent de DIMENSION"
    assert demandes[0] == 0, "le dépôt doit avoir une demande nulle"

    dist = [[distance(a, b) for b in coords] for a in coords]
    return Instance(nom, capacite, nb_camions, optimum, coords, demandes, dist)


if __name__ == "__main__":
    # Test : lit toutes les instances de data/ et affiche un résumé
    dossier = Path(__file__).resolve().parent.parent / "data"
    print(f"{'instance':<11}{'noeuds':>7}{'capa':>6}{'demande':>9}{'optimum':>9}"
          f"{'camions':>9}{'min':>5}{'d(0,1)':>8}")
    for fichier in sorted(dossier.glob("*.vrp")):
        inst = lire_instance(fichier)
        total = sum(inst.demandes)
        camions_min = math.ceil(total / inst.capacite)
        print(f"{inst.nom:<11}{inst.n:>7}{inst.capacite:>6}{total:>9}{inst.optimum:>9}"
              f"{inst.nb_camions:>9}{camions_min:>5}{inst.dist[0][1]:>8}")