import sqlite3
from datetime import datetime
from sklearn.linear_model import LinearRegression
from fpdf import FPDF

DB_NAME = "stock.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            categorie TEXT NOT NULL,
            prix_unitaire REAL NOT NULL,
            quantite_stock INTEGER NOT NULL,
            seuil_alerte INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER NOT NULL,
            quantite_vendue INTEGER NOT NULL,
            montant_total REAL NOT NULL,
            date_vente TEXT NOT NULL,
            FOREIGN KEY (produit_id) REFERENCES produits(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_facture TEXT NOT NULL,
            total_facture REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ligne_facture (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facture_id INTEGER NOT NULL,
            produit_id INTEGER NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL,
            montant_ligne REAL NOT NULL,
            FOREIGN KEY (facture_id) REFERENCES factures(id),
            FOREIGN KEY (produit_id) REFERENCES produits(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================
# PRODUITS
# =========================
def ajouter_produit(nom, categorie, prix_unitaire, quantite_stock, seuil_alerte):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO produits (nom, categorie, prix_unitaire, quantite_stock, seuil_alerte)
        VALUES (?, ?, ?, ?, ?)
    """, (nom, categorie, prix_unitaire, quantite_stock, seuil_alerte))

    conn.commit()
    conn.close()


def afficher_produits():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produits ORDER BY id ASC")
    produits = cursor.fetchall()

    conn.close()
    return produits


def get_produit_by_id(id_produit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produits WHERE id = ?", (id_produit,))
    produit = cursor.fetchone()

    conn.close()
    return produit


def rechercher_produits(mot_cle):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM produits
        WHERE nom LIKE ? OR categorie LIKE ?
        ORDER BY id ASC
    """, (f"%{mot_cle}%", f"%{mot_cle}%"))

    resultats = cursor.fetchall()
    conn.close()
    return resultats


def modifier_produit(id_produit, nom, categorie, prix_unitaire, quantite_stock, seuil_alerte):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE produits
        SET nom = ?, categorie = ?, prix_unitaire = ?, quantite_stock = ?, seuil_alerte = ?
        WHERE id = ?
    """, (nom, categorie, prix_unitaire, quantite_stock, seuil_alerte, id_produit))

    conn.commit()
    conn.close()


def supprimer_produit(id_produit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produits WHERE id = ?", (id_produit,))

    conn.commit()
    conn.close()


# =========================
# STOCK
# =========================
def ajouter_entree_stock(id_produit, quantite_ajoutee):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nom, quantite_stock
        FROM produits
        WHERE id = ?
    """, (id_produit,))
    produit = cursor.fetchone()

    if not produit:
        conn.close()
        return "Produit introuvable."

    if quantite_ajoutee <= 0:
        conn.close()
        return "La quantité ajoutée doit être supérieure à 0."

    nom, quantite_stock = produit
    nouveau_stock = quantite_stock + quantite_ajoutee

    cursor.execute("""
        UPDATE produits
        SET quantite_stock = ?
        WHERE id = ?
    """, (nouveau_stock, id_produit))

    conn.commit()
    conn.close()

    return f"Entrée de stock enregistrée. Nouveau stock de '{nom}' = {nouveau_stock}"


# =========================
# VENTES
# =========================
def enregistrer_vente(produit_id, quantite_vendue):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nom, prix_unitaire, quantite_stock
        FROM produits
        WHERE id = ?
    """, (produit_id,))
    produit = cursor.fetchone()

    if not produit:
        conn.close()
        return "Produit introuvable."

    _, nom, prix_unitaire, quantite_stock = produit

    if quantite_vendue <= 0:
        conn.close()
        return "La quantité vendue doit être supérieure à 0."

    if quantite_vendue > quantite_stock:
        conn.close()
        return "Stock insuffisant. Vente impossible."

    nouveau_stock = quantite_stock - quantite_vendue
    montant_total = prix_unitaire * quantite_vendue
    date_vente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO ventes (produit_id, quantite_vendue, montant_total, date_vente)
        VALUES (?, ?, ?, ?)
    """, (produit_id, quantite_vendue, montant_total, date_vente))

    cursor.execute("""
        UPDATE produits
        SET quantite_stock = ?
        WHERE id = ?
    """, (nouveau_stock, produit_id))

    conn.commit()
    conn.close()

    return f"Vente enregistrée avec succès. Nouveau stock de '{nom}' = {nouveau_stock}"


def afficher_historique_ventes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT v.id, p.nom, v.quantite_vendue, v.montant_total, v.date_vente
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        ORDER BY v.date_vente ASC
    """)

    ventes = cursor.fetchall()
    conn.close()
    return ventes


def afficher_historique_par_date():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT v.id, p.nom, v.quantite_vendue, v.montant_total, v.date_vente
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        ORDER BY date(v.date_vente) ASC, v.id ASC
    """)

    resultats = cursor.fetchall()
    conn.close()
    return resultats


def compter_ventes_par_produit():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.nom, COUNT(v.id) AS nombre_ventes,
               COALESCE(SUM(v.quantite_vendue), 0) AS quantite_totale_vendue
        FROM produits p
        LEFT JOIN ventes v ON p.id = v.produit_id
        GROUP BY p.id, p.nom
        ORDER BY nombre_ventes DESC, p.id ASC
    """)

    resultats = cursor.fetchall()
    conn.close()
    return resultats


def historique_produit_pour_ia(produit_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date(date_vente) AS jour, SUM(quantite_vendue) AS quantite_totale
        FROM ventes
        WHERE produit_id = ?
        GROUP BY date(date_vente)
        ORDER BY jour ASC
    """, (produit_id,))

    resultats = cursor.fetchall()
    conn.close()
    return resultats


# =========================
# IA - RÉGRESSION LINÉAIRE
# =========================
def predire_consommation(produit_id, jours_a_predire=1):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nom, quantite_stock
        FROM produits
        WHERE id = ?
    """, (produit_id,))
    produit = cursor.fetchone()

    if not produit:
        conn.close()
        return None

    nom_produit, stock_actuel = produit

    cursor.execute("""
        SELECT date(date_vente) AS jour, SUM(quantite_vendue) AS quantite_totale
        FROM ventes
        WHERE produit_id = ?
        GROUP BY date(date_vente)
        ORDER BY jour ASC
    """, (produit_id,))

    historique = cursor.fetchall()
    conn.close()

    if not historique:
        return {
            "produit": nom_produit,
            "stock_actuel": stock_actuel,
            "jours_historiques": 0,
            "moyenne_journaliere": 0,
            "prediction_totale": 0,
            "rupture": False,
            "quantite_a_commander": 0,
            "message": "Aucun historique de vente disponible pour ce produit."
        }

    quantites = [ligne[1] for ligne in historique]
    jours_historiques = len(quantites)

    if jours_historiques == 1:
        moyenne_journaliere = float(quantites[0])
        prediction_totale = round(moyenne_journaliere * jours_a_predire, 2)
    else:
        X = [[i] for i in range(jours_historiques)]
        y = quantites

        modele = LinearRegression()
        modele.fit(X, y)

        futures = [[jours_historiques + i] for i in range(jours_a_predire)]
        predictions = modele.predict(futures)

        predictions = [max(0, float(p)) for p in predictions]
        prediction_totale = round(sum(predictions), 2)
        moyenne_journaliere = round(sum(quantites) / jours_historiques, 2)

    rupture = prediction_totale > stock_actuel

    if rupture:
        quantite_a_commander = round(prediction_totale - stock_actuel, 2)
        message = "Risque de rupture détecté."
    else:
        quantite_a_commander = 0
        message = "Stock suffisant pour la période prédite."

    return {
        "produit": nom_produit,
        "stock_actuel": stock_actuel,
        "jours_historiques": jours_historiques,
        "moyenne_journaliere": moyenne_journaliere,
        "prediction_totale": prediction_totale,
        "rupture": rupture,
        "quantite_a_commander": quantite_a_commander,
        "message": message
    }


# =========================
# FACTURATION
# =========================
def creer_facture(lignes):
    conn = get_connection()
    cursor = conn.cursor()

    total_facture = 0
    lignes_preparees = []

    for ligne in lignes:
        produit_id = ligne["produit_id"]
        quantite = ligne["quantite"]

        cursor.execute("""
            SELECT id, nom, prix_unitaire, quantite_stock
            FROM produits
            WHERE id = ?
        """, (produit_id,))
        produit = cursor.fetchone()

        if not produit:
            conn.close()
            return "Produit introuvable dans la facture."

        _, nom, prix_unitaire, quantite_stock = produit

        if quantite <= 0:
            conn.close()
            return f"Quantité invalide pour le produit {nom}."

        if quantite > quantite_stock:
            conn.close()
            return f"Stock insuffisant pour le produit {nom}."

        montant_ligne = prix_unitaire * quantite
        total_facture += montant_ligne

        lignes_preparees.append({
            "produit_id": produit_id,
            "nom": nom,
            "quantite": quantite,
            "prix_unitaire": prix_unitaire,
            "montant_ligne": montant_ligne,
            "nouveau_stock": quantite_stock - quantite
        })

    date_facture = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO factures (date_facture, total_facture)
        VALUES (?, ?)
    """, (date_facture, total_facture))

    facture_id = cursor.lastrowid

    for ligne in lignes_preparees:
        cursor.execute("""
            INSERT INTO ligne_facture (facture_id, produit_id, quantite, prix_unitaire, montant_ligne)
            VALUES (?, ?, ?, ?, ?)
        """, (
            facture_id,
            ligne["produit_id"],
            ligne["quantite"],
            ligne["prix_unitaire"],
            ligne["montant_ligne"]
        ))

        cursor.execute("""
            UPDATE produits
            SET quantite_stock = ?
            WHERE id = ?
        """, (ligne["nouveau_stock"], ligne["produit_id"]))

        cursor.execute("""
            INSERT INTO ventes (produit_id, quantite_vendue, montant_total, date_vente)
            VALUES (?, ?, ?, ?)
        """, (
            ligne["produit_id"],
            ligne["quantite"],
            ligne["montant_ligne"],
            date_facture
        ))

    conn.commit()
    conn.close()

    return f"Facture créée avec succès. ID facture = {facture_id}, total = {round(total_facture, 2)}"


def afficher_factures():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date_facture, total_facture
        FROM factures
        ORDER BY id ASC
    """)

    factures = cursor.fetchall()
    conn.close()
    return factures


def afficher_details_facture(facture_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date_facture, total_facture
        FROM factures
        WHERE id = ?
    """, (facture_id,))
    facture = cursor.fetchone()

    if not facture:
        conn.close()
        return None

    cursor.execute("""
        SELECT p.nom, lf.quantite, lf.prix_unitaire, lf.montant_ligne
        FROM ligne_facture lf
        JOIN produits p ON lf.produit_id = p.id
        WHERE lf.facture_id = ?
    """, (facture_id,))

    lignes = cursor.fetchall()
    conn.close()

    return {
        "facture": facture,
        "lignes": lignes
    }


# =========================
# EXPORT PDF
# =========================
def exporter_facture_pdf(facture_id):
    details = afficher_details_facture(facture_id)

    if details is None:
        return None

    facture = details["facture"]
    lignes = details["lignes"]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)

    pdf.cell(0, 10, text="FACTURE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, text=f"ID facture : {facture[0]}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Date : {facture[1]}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, text=f"Total : {facture[2]}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(60, 8, text="Produit", border=1)
    pdf.cell(30, 8, text="Quantite", border=1)
    pdf.cell(40, 8, text="Prix unitaire", border=1)
    pdf.cell(40, 8, text="Montant", border=1, new_x="LMARGIN", new_y="NEXT")

    for ligne in lignes:
        pdf.cell(60, 8, text=str(ligne[0]), border=1)
        pdf.cell(30, 8, text=str(ligne[1]), border=1)
        pdf.cell(40, 8, text=str(ligne[2]), border=1)
        pdf.cell(40, 8, text=str(ligne[3]), border=1, new_x="LMARGIN", new_y="NEXT")

    nom_fichier = f"facture_{facture_id}.pdf"
    pdf.output(nom_fichier)
    return nom_fichier