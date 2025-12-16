# crawl-scrap-analyse-site-web

## TL;DR
Ce projet propose un pipeline **crawl → scrape → métriques** pour auditer la structure et le contenu d’un site web.
- **Entrée** : une URL “seed” (point de départ) ou une liste d’URLs
- **Sorties** : pages HTML sauvegardées + extraction texte + indicateurs par page dans un CSV
- **Use cases** : audit de structure (titres H1–H6), densité de contenu (paragraphes/longueur), cartographie des liens internes/externes

## Démarrage rapide
```bash
# 1) Crawling : collecte des URLs + sauvegarde HTML
python scripts/crawl-site-save-html.py

# 2) Scraping + métriques : extraction titres/paragraphes/liens + génération CSV
python scripts/scraping_fichiers_html.py
```

## Description

Ce projet a pour objectif de crawler, scraper et analyser des sites web afin d'extraire des informations clés telles que les titres, paragraphes et liens. Les données collectées sont ensuite traitées et sauvegardées pour des analyses approfondies, avec des métriques calculées pour chaque page visitée.
Le projet inclut également des outils pour générer des rapports basés sur les données extraites, faciliter la navigation et maintenir un suivi des sites explorés.

## Contexte

Avec 10 ans d'expérience dans le secteur des ONG, le constat est clair : les associations ont besoins d'outils performants à moindres coûts pour l'ensemble des processus métiers. 
C'est cela qui m'a amené à parfaire mes compétences en analyse de données et à imaginer ce projet en parallèle de ma formation de Data Analyst afin de mettre en oeuvre et améliorer mes compétences en scraping. 

La partie du projet développée actuellement (analyses à partir du code html des pages) sera être complété avec des analyses de performances des pages via l'outil Lighthouse. Pour un usage sur son propre site web, cela pourrait également être complété avec les analyses du traffic sur le site (Google Analytics ou Matomo). 

## Fonctionnalités principales

1. Crawling
    Collecte les URLs à partir d'un point de départ (seed).
    Enregistre les pages visitées pour éviter les doublons.

2. Scraping
    Extraction de données HTML structurées :
        Titres (H1-H6)
        Paragraphes
        Liens internes et externes
    Stockage des données dans des fichiers texte datés.

3. Analyse des pages web
    Calcul de statistiques :
        Nombre de titres par niveau (H1-H6)
        Nombre total de paragraphes et de caractères
        Nombre de liens (internes et externes)
        Longueur moyenne des titres

4. Rapports Lighthouse (en cours de développement)
    Génération de rapports JSON pour auditer les performances des pages web.

5. Gestion des URLs
    Gestion des fichiers CSV pour suivre :
        Les URLs à visiter
        Les URLs déjà visitées
    Mise à jour automatique après chaque traitement.

## Arborescence du projet

```
CRAWL-SCRAP-ANALYSE-SITE-WEB/
├── data/ (dans .gitignore)
│   ├── html_pages/               # Contient les fichiers HTML téléchargés
│   ├── rapports_lighthouse_json/ # Rapports JSON générés par Lighthouse
│   ├── text_pages/               # Fichiers texte générés après scraping
│   ├── test_urls.csv             # Fichier de test avec un sous-ensemble d'URLs
│   ├── urls_to_visit.csv         # Liste des URLs à visiter
│   ├── visited_urls.csv          # Liste des URLs déjà visitées
│   ├── visited_urls_updated.csv  # Liste mise à jour après chaque exécution
│   ├── logs.txt                  # Journalisation des erreurs et des processus (en cours de développement)
├── scripts/
│   ├── crawl-site-save-html.py   # Script pour crawler et sauvegarder les pages HTML
│   ├── scraping_fichiers_html.py # Script pour scraper et analyser les pages HTML
│   ├── lighthouse.py             # Script pour analyser les performances des pages sur Lighthouse (Google)
├── analyses/
│   ├── tableau-de-bord-site-web.ipbx
├── .env                          # Variables d'environnement (ex. : clés API)
├── .gitignore                    # Fichiers à exclure du contrôle de version
├── LICENSE                       # Licence du projet
├── README.md                     # Documentation principale
```

## Installation
### Prérequis

- Python 3.8 ou plus
- pip pour la gestion des dépendances
- Google Chrome (nécessaire pour Lighthouse)
- Node.js (pour utiliser Lighthouse en CLI)

## Étapes d'installation

1. Cloner le dépôt
```
git clone https://github.com/votre-utilisateur/CRAWL-SCRAP-ANALYSE-SITE-WEB.git
cd CRAWL-SCRAP-ANALYSE-SITE-WEB
```

2. Créer un environnement virtuel
```
python -m venv env
source env/bin/activate  # Sur Linux/Mac
env\Scripts\activate     # Sur Windows
```

3. Installer les dépendances
```
pip install -r requirements.txt
```

4. Configurer les variables d'environnement
Créez un fichier .env dans le dossier principal pour y ajouter des configurations spécifiques, comme des clés API ou des chemins personnalisés.

## Utilisation
1. Crawling et téléchargement des pages HTML

Lancez le script crawl-site-save-html.py pour explorer les URLs depuis l'url initiale ou le fichier urls_to_visit.csv. Le script télécharge les pages HTML.
```
python scripts/crawl-site-save-html.py
```

2. Scraping des données HTML

Lancez le script scraping_fichiers_html.py pour extraire les titres, paragraphes et liens depuis les fichiers HTML, générer les fichiers texte correspondants et calculer les indicateurs.
```
python scripts-test/scraping_fichiers_html.py
```

3. Analyse des performances des pages (en cours de développement)

Utilisez lighthouse.py pour générer des rapports JSON Lighthouse pour chaque URL visitée.
```
python scripts-test/lighthouse.py
```

4. Importer le fichier 'visited_urls_updated.csv' / Actualiser la source de données dans le fichier Power BI 'tableau-de-bord-site-web.ipbx' (en cours de développement)


## Contribution

Les contributions sont les bienvenues ! Suivez les étapes ci-dessous pour proposer des améliorations :

1. Forkez ce dépôt.

2. Créez une branche pour vos modifications.
```
git checkout -b feature/ma-fonctionnalite
```

3. Faites vos changements et validez-les.
```
git commit -m "Ajout d'une nouvelle fonctionnalité"
```

4. Poussez vos changements sur votre fork.
```
git push origin feature/ma-fonctionnalite
```

5. Créez une Pull Request vers la branche principale.

# Licence

Ce projet est sous licence MIT. Consultez le fichier LICENSE pour plus d'informations.

# Auteure

Alice Gontier
