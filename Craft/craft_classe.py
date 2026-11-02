from .craft_commun import donnees, message, donner_arme

PALIER = 5

ARMES_CLASSE = {
    "Assaut": "fusil_assaut",
    "Tactique": "pistolet_mitrailleur",
    "Sniper": "fusil_precision",
    "Brèche": "fusil_pompe",
}

ARME_DEFAUT = "pistolet"


def arme_de(p):
    nom = getattr(p.classe, "nom", None)

    if isinstance(p.classe, dict):
        nom = p.classe.get("nom")

    return ARMES_CLASSE.get(nom, ARME_DEFAUT)


def verifier(p, n_rouge):
    d = donnees(p)

    if n_rouge < PALIER:
        return False

    if d["arme_classe"]:
        return False

    d["arme_classe"] = True

    arme = arme_de(p)

    donner_arme(p, arme)

    message(
        p,
        f"Nouvelle arme débloquée : {arme}"
    )

    return True