"""Vérificateur indépendant : contrôle qu'une solution est valide et calcule sa distance."""


def verifier(inst, tournees):
    """tournees : liste de tournées, chacune une liste de noeuds [0, c1, c2, ..., 0].
    Lève une AssertionError si la solution est invalide, sinon renvoie la distance totale."""
    vus = []
    total = 0
    for t in tournees:
        assert t[0] == 0 and t[-1] == 0, "une tournée doit commencer et finir au dépôt"
        charge = sum(inst.demandes[c] for c in t)
        assert charge <= inst.capacite, f"capacité dépassée ({charge} > {inst.capacite})"
        total += sum(inst.dist[a][b] for a, b in zip(t, t[1:]))
        vus.extend(t[1:-1])
    assert sorted(vus) == list(range(1, inst.n)), "chaque client doit être visité exactement une fois"
    return total