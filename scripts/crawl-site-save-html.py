import requests
from  bs4 import BeautifulSoup
import pandas as pd
import regex as re
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
import os
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AliceGontierCrawler/1.0)"}
REQUEST_TIMEOUT = 10

class Crawler:
       
    def __init__(self,max_pages, urls=[]):
        self.max_pages = max_pages
        self.urls_to_visit = []
        self.visited_urls = []  # Liste des URLs visitées
        self.visited_data = []  # Liste pour stocker les URLs visitées et leurs fichiers HTML
        self.output_html_dir = "./data/html_pages"  # Dossier pour stocker les fichiers HTML 
        # Charger les URLs à visiter depuis un fichier CSV ou les paramètres d'initialisation
        self.load_urls_to_visit(urls)

    def load_urls_to_visit(self, initial_urls):
        """Charge les URLs à visiter depuis un fichier CSV ou une liste d'initialisation."""
        try:
            df = pd.read_csv('./data/urls_to_visit.csv')
            self.urls_to_visit = df['urls'].tolist()
            print("URLs chargées depuis urls_to_visit.csv.")
        except FileNotFoundError:
            self.urls_to_visit = initial_urls
            print("Fichier urls_to_visit.csv introuvable. Utilisation des URLs initiales.")


    def load_visited_urls(self):
        try:
            df = pd.read_csv('./data/visited_urls.csv')
            self.visited_urls = df['urls'].tolist()
        except FileNotFoundError:
            self.visited_urls = []  # Si le fichier n'existe pas encore, retourner une liste vide
    

    def clean_url(self, url):
        """Supprime les paramètres 'utm' de l'URL."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Filtrer les paramètres utm
        cleaned_params = {key: value for key, value in query_params.items() if not key.startswith('utm_')}
        
        # Reconstruire l'URL sans les paramètres utm
        cleaned_url = parsed_url._replace(query=urlencode(cleaned_params, doseq=True))
        return urlunparse(cleaned_url)
    

    def normalize_url(self, url):
        """Normalise l'URL en forçant le schéma HTTPS et en supprimant les fragments et les paramètres utm."""
        cleaned_url = self.clean_url(url)  # Supprime les paramètres utm
        parsed = urlparse(cleaned_url)
        
        # Supprime le slash final pour uniformiser
        path = parsed.path.rstrip('/') if parsed.path != '/' else parsed.path
        normalized = urlunparse(parsed._replace(scheme='https', fragment='', path=path))
        
        return normalized
    

    def add_utm_parameters(self, url, utmsource="analyse", utmmedium="crawl_scrap", utmcampaign=f"{datetime.today().strftime('%Y-%m')}"):
        """Ajoute des paramètres UTM à l'URL."""
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Ajouter ou mettre à jour les paramètres UTM
        query_params.update({
            'utm_source': utmsource,
            'utm_medium': utmmedium,
            'utm_campaign': utmcampaign
        })
        
        # Reconstruire l'URL avec les nouveaux paramètres
        url_with_utm = urlunparse(parsed_url._replace(query=urlencode(query_params, doseq=True)))
        return url_with_utm


    def valid_url(self, url):
        """Vérifie si l'URL est valide et retourne le contenu HTML."""
        try:
            # Ajouter les paramètres UTM avant de faire la requête GET
            url_with_utm = self.add_utm_parameters(url)
            
            # Effectuer la requête GET avec l'URL modifiée
            r = requests.get(url_with_utm, headers=HEADERS, timeout=REQUEST_TIMEOUT)

            # Vérifiez les codes de réponse
            if r.status_code == 200:
                # Si tout est OK, parser le contenu
                soup = BeautifulSoup(r.content, "html.parser")
                return soup
            elif r.status_code == 301 or r.status_code == 302:
                # Si une redirection a été suivie, vous pouvez afficher un message de suivi
                print(f"Redirection suivie vers {r.url} pour {url}")
                soup = BeautifulSoup(r.content, "html.parser")
                return soup
            else:
                # Gestion des autres erreurs HTTP
                print(f"Erreur {r.status_code} pour {url}")
                return None
        except requests.exceptions.TooManyRedirects:
            print(f"Erreur : trop de redirections pour {url}")
            return None
        except requests.exceptions.RequestException as e:
            # Autres erreurs liées aux requêtes
            print(f"Erreur de requête pour {url}: {e}")
            return None
        

    def domaine(self, url):
        domaine = re.search(r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})", url)
        return domaine.group(1) if domaine else None
    

    def get_internal_urls(self, url):
        """Récupère les URLs internes du site."""
        html = self.valid_url(url)
        if not html:
            return

        domaine_site = self.domaine(url)
        for link in html.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            normalized_url = self.normalize_url(full_url)

            # Ajouter uniquement si c'est une URL interne et si elle n'a pas encore été visitée
            if domaine_site in normalized_url and normalized_url not in self.visited_urls:
                self.add_urls_to_visit(normalized_url)


    def add_urls_to_visit(self, url):
        """Ajoute une URL à la liste des URLs à visiter si elle n'est pas encore visitée."""
        if url not in self.urls_to_visit and url not in self.visited_urls:
            self.urls_to_visit.append(url)


    def save_to_csv(self):
        """Sauvegarde les URLs visitées dans un fichier CSV sans écraser les anciennes."""
        # Charger les URLs déjà visitées depuis le fichier CSV, si disponible
        try:
            df_visited = pd.read_csv('./data/visited_urls.csv')
        except FileNotFoundError:
            df_visited = pd.DataFrame(columns=['urls', 'html_file_path'])  # Si le fichier n'existe pas encore, créer un DataFrame vide avec les bonnes colonnes
        
        # Créer un DataFrame à partir des nouvelles URLs visitées
        df_new_visited = pd.DataFrame(self.visited_data, columns=['urls', 'html_file_path'])
        
        # Fusionner les deux DataFrames en concaténant et en supprimant les doublons
        df_all_visited = pd.concat([df_visited, df_new_visited]).drop_duplicates(subset='urls', keep='first')
        
        # Sauvegarder les URLs visitées dans le fichier CSV
        df_all_visited.to_csv('./data/visited_urls.csv', index=False)

        # Sauvegarder les URLs restantes à visiter
        df_to_visit = pd.DataFrame(self.urls_to_visit, columns=['urls'])
        df_to_visit.to_csv('./data/urls_to_visit.csv', index=False)


    def save_html(self, url, soup):
        """Sauvegarde le contenu HTML dans un fichier."""
        base_name = url.replace("http://", "").replace("https://", "").replace("/", "_")
        html_file_path = os.path.join(self.output_html_dir, base_name + ".html")
        
        # Assurez-vous que le dossier existe
        if not os.path.exists("./data/html_pages"):
            os.makedirs("./data/html_pages")

        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        return html_file_path
    

    def run(self):
        """Exécute le crawler."""
        while self.urls_to_visit and len(self.visited_urls) < self.max_pages:
            url = self.urls_to_visit.pop(0)
            print(f"En train de crawler : {url}")

            try:
                # 1. Récupérer le contenu de la page (scraping)
                soup = self.valid_url(url)
                if soup:
                    
                    # 2. Explorer les liens internes de la page (ajouter à la liste des URLs à visiter)
                    self.get_internal_urls(url)

                    # 3. Normaliser l'URL
                    normalized_url = self.normalize_url(url)

                    # 4. Sauvegarder le contenu HTML de la page visitée
                    html_file_path = self.save_html(normalized_url, soup)

                    # 5. Vérifiez si l'URL est déjà visitée avant d'ajouter
                    if normalized_url not in self.visited_urls:
                        self.visited_urls.append(normalized_url)
                        # Sauvegarder l'URL et le chemin vers le fichier HTML
                        self.visited_data.append({'urls': normalized_url, 'html_file_path': html_file_path})
                    
            except Exception as e:
                print(f"Erreur de traitement pour l'URL : {url} | {e}")
        

        self.save_to_csv()
        print(f"Total des URLs visitées : {len(self.visited_urls)}")
        print(f"Liste des URLs visitées sauvegardée dans 'visited_urls.csv'.")


Crawler(max_pages=500, urls=['https://monsiteweb.com/']).run()
