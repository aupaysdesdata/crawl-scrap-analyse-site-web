from bs4 import BeautifulSoup       # analyser et extraire facilement des éléments des fichiers HTML
import pandas as pd                 # manipuler des fichiers de données comme les fichiers CSV
import os                           # gérer les chemins et vérifier l'existence des répertoires/fichiers
from datetime import datetime       # récupérer la date actuelle pour nommer les fichiers générés
from urllib.parse import urlparse, urljoin

# Variables globales
html_dir = "./data/html_pages" # Répertoire où sont stockés les fichiers HTML à analyser
file_urls = "./data/visited_urls.csv"  # Chemin du fichier CSV contenant les URLs visitées et leurs chemins correspondants vers les fichiers HTML (généré grâce au script 'crawl-site-save-html.py')


# Définition de la fonction principale : 
    # Traiter les fichiers HTML en blocs (chunks) pour éviter les problèmes de mémoire
    # Extraire les informations des fichiers HTML, générer des fichiers texte et mettre à jour le CSV

def scrape_and_update(file_urls, chunk_size=100):
    chunk_index = 0                    # Identifiant du bloc traité (utile pour afficher les logs)
    current_date = datetime.today().strftime('%Y-%m-%d')  # Formatage de la date du jour pour nommer les fichiers générés

    # Initialisation de la boucle pour traiter les chunks
    for chunk in pd.read_csv(file_urls, chunksize=chunk_size): # Lecture du fichier CSV file_urls par blocs (chunksize=100) pour limiter la quantité de données chargées en mémoire à la fois
        print(f"Traitement du chunk {chunk_index}...")

        # Préparation du répertoire de sortie
        output_text_dir = "./data/text_pages" # Répertoire où seront sauvegardés les fichiers texte générés
        if not os.path.exists(output_text_dir): # Si le répertoire n'existe pas, il est créé
            os.makedirs(output_text_dir) 

        # Ajout de colonnes nécessaires dans le DataFrame
        columns_to_add = [
            "text_file_path", "h1_count", "h2_count", "h3_count", "h4_count", "h5_count", "h6_count",
            "paragraph_count", "link_count", "internal_link_count", "external_link_count",
            "paragraph_character_count", "average_title_length"
        ]

        # Définit des colonnes supplémentaires dans le DataFrame chunk pour stocker les statistiques extraites des fichiers HTML (comme le nombre de titres, de paragraphes, etc.)
        for col in columns_to_add:
            if col not in chunk.columns:
                chunk[col] = None

        # Boucle pour chaque URL dans le chunk
        for index, row in chunk.iterrows(): # Parcourt chaque ligne du DataFrame chunk
            # Vérification de l'existence du fichier HTML
            html_file_path = row.get('html_file_path') # Récupère le chemin du fichier HTML pour chaque URL dans la colonne html_file_path
            if not html_file_path or not os.path.exists(html_file_path): # Si le fichier HTML n'existe pas, la ligne est ignorée
                print(f"Fichier HTML manquant pour {row.get('urls')}.")
                continue
            
            # Charge le contenu HTML du fichier dans un objet BeautifulSoup pour permettre son analyse
            try:
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
            except Exception as e:
                print(f"Erreur lors de la lecture de {html_file_path}: {e}")
                continue
            
            # Génération du fichier texte et initialisation des variables
            
            # Génère un nom de fichier unique pour chaque URL basé sur la date et le nom de domaine
            base_name = row['urls'].replace("http://", "").replace("https://", "").replace("/", "_") 
            text_file_path = os.path.join(output_text_dir, f"{current_date}_{base_name}.txt")

            # Initialise des variables pour compter les éléments comme les titres, paragraphes, liens, etc.
            formatted_text = []
            h_counts = {f"h{i}_count": 0 for i in range(1, 7)}
            paragraph_count = 0
            paragraph_character_count = 0
            link_count = 0
            internal_link_count = 0
            external_link_count = 0
            title_lengths = []

            # Extraction des éléments HTML
            if soup.body: # Analyse tous les éléments de la balise <body> du fichier HTML
                for element in soup.body.find_all():
                    tag_name = element.name

                    # Titres (H1-H6)
                    # Compte chaque titre par niveau et enregistre la longueur du texte
                    if tag_name in [f'h{i}' for i in range(1, 7)]:
                        level = int(tag_name[1])
                        text = element.get_text(strip=True)
                        formatted_text.append(f"{'#' * level} {text}\n")
                        h_counts[f"h{level}_count"] += 1
                        title_lengths.append(len(text))

                    # Paragraphes
                    # Extrait les textes des balises <p> et calcule le nombre total de paragraphes et de caractères.
                    elif tag_name == "p":
                        text = element.get_text(strip=True)
                        formatted_text.append(f"\n{text}\n")
                        paragraph_count += 1
                        paragraph_character_count += len(text)

                    # Liens
                    # Extrait les liens (balise <a>) et distingue les liens internes des liens externes
                    # Classification interne/externe basée sur le domaine de la page
                    elif tag_name == "a" and element.has_attr("href"):
                        href = element["href"].strip()
                        text = element.get_text(strip=True)
                    
                        # Ignorer les ancres et liens non web
                        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
                            continue
                    
                        formatted_text.append(f"[{text}]({href})\n")
                        link_count += 1
                    
                        # Déterminer interne/externe à partir du domaine de la page courante
                        page_url = row.get("urls", "")
                        base_netloc = urlparse(page_url).netloc
                    
                        abs_url = urljoin(page_url, href)
                        link_netloc = urlparse(abs_url).netloc
                    
                        # Interne si lien relatif OU même domaine
                        if link_netloc == "" or link_netloc == base_netloc:
                            internal_link_count += 1
                        else:
                            external_link_count += 1

            # Sauvegarde du texte formaté
            final_text = "\n".join(formatted_text)

            with open(text_file_path, 'w', encoding='utf-8') as f: # Crée et sauvegarde un fichier texte avec le contenu analysé
                f.write(final_text)

            # Mise à jour des statistiques dans le DataFrame
            chunk.at[index, 'text_file_path'] = text_file_path
            for key, value in h_counts.items():
                chunk.at[index, key] = value
            chunk.at[index, 'paragraph_count'] = paragraph_count
            chunk.at[index, 'link_count'] = link_count
            chunk.at[index, 'internal_link_count'] = internal_link_count
            chunk.at[index, 'external_link_count'] = external_link_count
            chunk.at[index, 'paragraph_character_count'] = paragraph_character_count
            chunk.at[index, 'average_title_length'] = (
                sum(title_lengths) / len(title_lengths) if title_lengths else 0
            )

        # Sauvegarde du chunk mis à jour
        output_csv = file_urls.replace(".csv", "_updated.csv") # Sauvegarde le chunk modifié dans un fichier CSV avec le suffixe _updated
        chunk.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)
        print(f"Chunk {chunk_index} sauvegardé dans {output_csv}.")
        chunk_index += 1

# Appel de la fonction
scrape_and_update(file_urls) # Exécute la fonction avec le chemin vers le fichier CSV des URLs visitées
