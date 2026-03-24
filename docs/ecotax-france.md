# L'Éco-participation en France

## Qu'est-ce que c'est ?

L'éco-participation (aussi appelée **éco-taxe** ou **contribution environnementale**) est une contribution financière obligatoire ajoutée au prix de vente de certains produits. Elle finance la collecte, le tri et le recyclage des produits en fin de vie.

Elle est encadrée par le principe de **Responsabilité Élargie des Producteurs (REP)**, issu de la directive européenne 2008/98/CE, transposé en droit français dans le **Code de l'environnement** (article L541-10 et suivants), renforcé par la **Loi AGEC** (Anti-Gaspillage pour une Économie Circulaire) du 10 février 2020.

---

## Les principales filières REP

### 1. DEEE — Déchets d'Équipements Électriques et Électroniques
- **Produits concernés** : appareils électroménagers, TV, ordinateurs, téléphones, lampes, etc.
- **Éco-organismes agréés** : Eco-systèmes, Ecologic, Récylum (lampes), OCAD3E
- **Base légale** : Décret n°2005-829 du 20 juillet 2005
- Les montants varient de quelques centimes à plusieurs euros selon le produit

### 2. Éco-mobilier
- **Produits concernés** : meubles (canapés, tables, chaises, matelas, etc.)
- **Éco-organisme** : Éco-mobilier
- **Base légale** : Décret n°2012-22 du 6 janvier 2012

### 3. Citeo (ex-Eco-Emballages)
- **Produits concernés** : emballages ménagers, papiers graphiques
- **Éco-organisme** : Citeo
- Financé principalement par les entreprises qui mettent les emballages sur le marché (pas toujours visible sur la facture consommateur)

### 4. Autres filières
- **Pneumatiques** : Aliapur
- **Piles et accumulateurs** : Corepile, Screlec
- **Médicaments** : Cyclamed
- **Textiles** : Refashion (ex-Eco-TLC)
- **Véhicules hors d'usage** : filière automobile

---

## Obligations légales pour les entreprises

### Affichage obligatoire
Depuis le **1er janvier 2006** (DEEE) et étendu aux autres filières, l'éco-participation doit être **affichée séparément** du prix de vente HT sur :
- Les étiquettes en magasin
- Les catalogues et sites e-commerce
- Les **factures** (ligne distincte)

> ⚠️ Elle ne doit **pas** être incluse dans le prix HT sans mention explicite — c'est une obligation de transparence envers le consommateur.

### Traitement comptable et fiscal

| Aspect | Règle |
|--------|-------|
| **TVA** | L'éco-participation est soumise à la TVA au même taux que le produit principal |
| **Facturation** | Doit apparaître comme ligne distincte sur la facture |
| **Comptabilisation** | En général comptabilisée en **charges** (compte 6xx) ou reversée à l'éco-organisme |
| **Prix de vente** | Le montant est fixé par l'éco-organisme, le vendeur le répercute à l'identique |

### Qui est redevable ?
- Le **producteur** ou **importateur** qui met le produit sur le marché français adhère à un éco-organisme agréé et lui verse une contribution
- Le **distributeur** répercute cette contribution sur le prix de vente au consommateur final

---

## Montants (exemples DEEE 2024)

| Catégorie | Exemple de produit | Montant éco-part. |
|-----------|-------------------|-------------------|
| Gros électroménager | Lave-linge | 0,40 € – 1,50 € |
| Petit électroménager | Grille-pain | 0,04 € – 0,20 € |
| Écrans | TV 55" | 0,20 € – 1,50 € |
| Informatique | Ordinateur portable | 0,10 € – 0,45 € |
| Lampes | Ampoule LED | 0,01 € – 0,05 € |

> Les montants exacts sont publiés par chaque éco-organisme et révisés périodiquement.

---

## Dans Odoo (account_ecotax)

Le module `account_ecotax` implémente cette logique :

1. **Classification** (`account.ecotax.classification`) : définit le type d'éco-taxe
   - *Fixed* : montant fixe par unité (ex: 0,50 €/unité)
   - *Weight based* : montant calculé au poids (ex: 0,04 €/kg)

2. **Affectation produit** : chaque produit se voit attribuer une ou plusieurs classifications

3. **Facture** : le montant total d'éco-participation apparaît séparément sous le total des taxes ("Including Eco Part")

---

## Ressources utiles

- [ADEME — filières REP](https://www.ademe.fr/expertises/dechets/elements-transversaux/filieres-a-responsabilite-elargie-du-producteur/)
- [Eco-systèmes (DEEE)](https://www.eco-systemes.fr)
- [Éco-mobilier](https://www.eco-mobilier.fr)
- [Citeo](https://www.citeo.com)
- [Légifrance — L541-10](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000041599099)
- [Loi AGEC](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000041553759)
