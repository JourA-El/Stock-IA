from database import (
    create_tables,
    ajouter_produit,
    afficher_produits,
    get_produit_by_id,
    rechercher_produits,
    modifier_produit,
    supprimer_produit,
    ajouter_entree_stock,
    enregistrer_vente,
    afficher_historique_ventes,
    afficher_historique_par_date,
    compter_ventes_par_produit,
    historique_produit_pour_ia,
    predire_consommation,
    creer_facture,
    afficher_factures,
    afficher_details_facture,
    exporter_facture_pdf
)


def afficher_liste(produits):
    if not produits:
        print("\nAucun produit trouvé.")
        return

    for produit in produits:
        etat = "Disponible"
        if produit[4] == 0:
            etat = "RUPTURE"
        elif produit[4] <= produit[5]:
            etat = "STOCK FAIBLE"

        print(
            f"ID: {produit[0]} | Nom: {produit[1]} | "
            f"Catégorie: {produit[2]} | Prix: {produit[3]} | "
            f"Stock: {produit[4]} | Seuil: {produit[5]} | État: {etat}"
        )


def afficher_liste_produits():
    produits = afficher_produits()
    print("\n--- LISTE DES PRODUITS ---")
    afficher_liste(produits)


def afficher_historique():
    ventes = afficher_historique_ventes()

    if not ventes:
        print("\nAucune vente enregistrée.")
        return

    print("\n--- HISTORIQUE DES VENTES ---")
    for vente in ventes:
        print(
            f"ID Vente: {vente[0]} | Produit: {vente[1]} | "
            f"Quantité: {vente[2]} | Montant: {vente[3]} | Date: {vente[4]}"
        )


def afficher_historique_par_date_console():
    resultats = afficher_historique_par_date()

    if not resultats:
        print("\nAucune vente enregistrée.")
        return

    print("\n--- HISTORIQUE DES VENTES PAR DATE ---")
    for ligne in resultats:
        print(
            f"ID Vente: {ligne[0]} | Produit: {ligne[1]} | "
            f"Quantité: {ligne[2]} | Montant: {ligne[3]} | Date: {ligne[4]}"
        )


def afficher_statistiques_ventes_produits():
    resultats = compter_ventes_par_produit()

    if not resultats:
        print("\nAucune donnée disponible.")
        return

    print("\n--- NOMBRE DE FOIS QU'UN PRODUIT A ÉTÉ VENDU ---")
    for ligne in resultats:
        print(
            f"ID Produit: {ligne[0]} | Nom: {ligne[1]} | "
            f"Nombre de ventes: {ligne[2]} | Quantité totale vendue: {ligne[3]}"
        )


def afficher_historique_ia():
    afficher_liste_produits()
    produit_id = int(input("ID du produit pour préparer l'historique IA : "))

    donnees = historique_produit_pour_ia(produit_id)

    if not donnees:
        print("Aucune donnée historique disponible pour ce produit.")
        return

    print("\n--- HISTORIQUE PRÉPARÉ POUR L'IA ---")
    for ligne in donnees:
        print(f"Date: {ligne[0]} | Quantité totale vendue: {ligne[1]}")


def analyser_et_predire_produit():
    afficher_liste_produits()
    produit_id = int(input("ID du produit à analyser : "))

    historique = historique_produit_pour_ia(produit_id)

    print("\n--- ANALYSE DE L'HISTORIQUE ---")
    if not historique:
        print("Aucun historique disponible pour ce produit.")
        return

    for ligne in historique:
        print(f"Date : {ligne[0]} | Quantité vendue : {ligne[1]}")

    jours = int(input("\nNombre de jours à prédire : "))

    resultat = predire_consommation(produit_id, jours)

    if resultat is None:
        print("Produit introuvable.")
        return

    print("\n--- RÉSULTAT DE LA PRÉDICTION ---")
    print(f"Produit : {resultat['produit']}")
    print(f"Stock actuel : {resultat['stock_actuel']}")
    print(f"Nombre de jours historiques analysés : {resultat['jours_historiques']}")
    print(f"Moyenne journalière vendue : {resultat['moyenne_journaliere']}")
    print(f"Quantité prévue pour {jours} jour(s) : {resultat['prediction_totale']}")
    print(resultat["message"])

    if resultat["rupture"]:
        print(f"Quantité recommandée à commander : {resultat['quantite_a_commander']}")


def afficher_liste_factures():
    factures = afficher_factures()

    if not factures:
        print("\nAucune facture trouvée.")
        return

    print("\n--- LISTE DES FACTURES ---")
    for facture in factures:
        print(f"ID: {facture[0]} | Date: {facture[1]} | Total: {facture[2]}")


def afficher_une_facture():
    facture_id = int(input("ID de la facture : "))
    details = afficher_details_facture(facture_id)

    if details is None:
        print("Facture introuvable.")
        return

    facture = details["facture"]
    lignes = details["lignes"]

    print("\n--- DÉTAIL FACTURE ---")
    print(f"ID facture : {facture[0]}")
    print(f"Date : {facture[1]}")
    print(f"Total : {facture[2]}")
    print("Lignes :")

    for ligne in lignes:
        print(
            f"Produit: {ligne[0]} | Quantité: {ligne[1]} | "
            f"Prix unitaire: {ligne[2]} | Montant: {ligne[3]}"
        )


def saisir_facture():
    afficher_liste_produits()
    lignes = []

    while True:
        produit_id = int(input("ID du produit à ajouter à la facture : "))
        quantite = int(input("Quantité : "))

        lignes.append({
            "produit_id": produit_id,
            "quantite": quantite
        })

        continuer = input("Ajouter un autre produit ? (o/n) : ").strip().lower()
        if continuer != "o":
            break

    message = creer_facture(lignes)
    print(message)


def exporter_pdf():
    facture_id = int(input("ID de la facture à exporter en PDF : "))
    nom_fichier = exporter_facture_pdf(facture_id)

    if nom_fichier is None:
        print("Facture introuvable.")
    else:
        print(f"PDF généré avec succès : {nom_fichier}")


def main():
    create_tables()

    while True:
        print("\n========== MENU GESTION DE STOCK ==========")
        print("1. Ajouter un produit")
        print("2. Modifier un produit")
        print("3. Supprimer un produit")
        print("4. Afficher la liste des produits")
        print("5. Consulter le stock disponible")
        print("6. Enregistrer une entrée de stock")
        print("7. Rechercher un produit")
        print("8. Enregistrer une vente")
        print("9. Afficher l'historique des ventes")
        print("10. IA : analyser l'historique et prédire la consommation")
        print("11. Créer une facture")
        print("12. Afficher la liste des factures")
        print("13. Afficher les détails d'une facture")
        print("14. Exporter une facture en PDF")
        print("15. Afficher l'historique des ventes par date")
        print("16. Afficher combien de fois chaque produit a été vendu")
        print("17. Afficher l'historique préparé pour l'IA")
        print("18. Quitter")

        choix = input("Choisissez une option : ").strip()

        if choix == "1":
            nom = input("Nom du produit : ").strip()
            categorie = input("Catégorie : ").strip()
            prix_unitaire = float(input("Prix unitaire : "))
            quantite_stock = int(input("Quantité en stock : "))
            seuil_alerte = int(input("Seuil d'alerte : "))

            ajouter_produit(nom, categorie, prix_unitaire, quantite_stock, seuil_alerte)
            print("Produit ajouté avec succès.")

        elif choix == "2":
            afficher_liste_produits()
            id_produit = int(input("ID du produit à modifier : "))

            produit = get_produit_by_id(id_produit)
            if not produit:
                print("Produit introuvable.")
                continue

            nom = input("Nouveau nom : ").strip()
            categorie = input("Nouvelle catégorie : ").strip()
            prix_unitaire = float(input("Nouveau prix unitaire : "))
            quantite_stock = int(input("Nouvelle quantité en stock : "))
            seuil_alerte = int(input("Nouveau seuil d'alerte : "))

            modifier_produit(id_produit, nom, categorie, prix_unitaire, quantite_stock, seuil_alerte)
            print("Produit modifié avec succès.")

        elif choix == "3":
            afficher_liste_produits()
            id_produit = int(input("ID du produit à supprimer : "))

            produit = get_produit_by_id(id_produit)
            if not produit:
                print("Produit introuvable.")
                continue

            supprimer_produit(id_produit)
            print("Produit supprimé avec succès.")

        elif choix == "4":
            afficher_liste_produits()

        elif choix == "5":
            print("\n--- STOCK DISPONIBLE ---")
            afficher_liste_produits()

        elif choix == "6":
            afficher_liste_produits()
            id_produit = int(input("ID du produit : "))
            quantite_ajoutee = int(input("Quantité à ajouter : "))
            message = ajouter_entree_stock(id_produit, quantite_ajoutee)
            print(message)

        elif choix == "7":
            mot_cle = input("Entrez le nom ou la catégorie à rechercher : ").strip()
            resultats = rechercher_produits(mot_cle)
            print("\n--- RÉSULTAT DE LA RECHERCHE ---")
            afficher_liste(resultats)

        elif choix == "8":
            afficher_liste_produits()
            produit_id = int(input("ID du produit vendu : "))
            quantite_vendue = int(input("Quantité vendue : "))
            message = enregistrer_vente(produit_id, quantite_vendue)
            print(message)

        elif choix == "9":
            afficher_historique()

        elif choix == "10":
            analyser_et_predire_produit()

        elif choix == "11":
            saisir_facture()

        elif choix == "12":
            afficher_liste_factures()

        elif choix == "13":
            afficher_une_facture()

        elif choix == "14":
            exporter_pdf()

        elif choix == "15":
            afficher_historique_par_date_console()

        elif choix == "16":
            afficher_statistiques_ventes_produits()

        elif choix == "17":
            afficher_historique_ia()

        elif choix == "18":
            print("Fin du programme.")
            break

        else:
            print("Choix invalide, réessaie.")


if __name__ == "__main__":
    main()