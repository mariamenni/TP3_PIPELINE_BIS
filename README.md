TP3_PIPELINE_BIS – GEO Data Explorer 🌍

1. Présentation du projet

GEO Data Explorer est une application interactive développée en Python avec Streamlit et Plotly, permettant d’explorer des données géographiques enrichies avec des informations démographiques et de qualité de géocodage. 

Le projet inclut un pipeline d’enrichissement géographique et un chatbot intelligent pour interroger le dataset et générer des analyses dynamiques.


L'objectif:

Collecter, enrichir et transformer des adresses géographiques.

Nettoyer et analyser la qualité des données.

Visualiser des informations géographiques et statistiques.

Interagir avec un chatbot pour l’analyse de données.


2. Structure du projet
   
tp2-exploration/
│
├─ .venv/                        # Environnement virtuel Python
├─ data/                          # Données brutes, traitées et rapports
│  ├─ raw/
│  ├─ processed/
│  └─ reports/
├─ notebooks/                     # Notebooks Jupyter
│  ├─ exploration.ipynb           # Exploration et analyses GEO
│  └─ test.ipynb                  # Tests et exécution du pipeline
├─ pipeline/                      # Modules Python du pipeline
│  ├─ fetchers/                   # Fetchers pour APIs
│  ├─ models.py                   # Modèles de données (GeocodingResult, EnrichedAddress)
│  ├─ main.py                     # Script principal du pipeline
│  ├─ transformer.py              # Nettoyage et transformations
│  ├─ quality.py                  # Analyse qualité
│  ├─ storage.py                  # Lecture/écriture de fichiers
│  ├─ enricher.py                 # Enrichissement GEO
│  └─ config.py                   # Configurations et constantes
├─ tests/                         # Tests unitaires avec pytest
├─ utils/                       
│  ├─ charts.py                  # Fonctions de visualisation Plotly (bar, scatter, histogram, geo map…)
│  ├─ chatbot.py                 # Classe DataChatbot pour interaction avec les données
│  ├─ data.py                    # Fonctions de chargement et filtrage de données
├─ .streamlit/                          
│  ├─ config.toml                # Configuration du thème Streamlit
├─ .gitignore
├─ pyproject.toml
├─ main.py
├─ README.md
└─ uv.lock
├─ test_charts.ipynb/            # Notebook pour tester les visualisations
├─ enrichissement_df.ipynb
├─ app_streamlit.ipynb           # Application Streamlit principale

                            
3. Tester les visualisations dans Jupyter Notebook

test_charts.ipynb permet de tester bar chart, scatter plot et cartes géographiques.

enrichissement_df.ipynb montre un exemple d’enrichissement GEO sur une liste d’adresses.



4. Installation et exécution

Cloner le projet :

git clone <repo_url>
cd tp3-exploration


Créer et activer l’environnement virtuel :

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows


Installer les dépendances :

uv install httpx pandas duckdb litellm python-dotenv tenacity tqdm pyarrow pydantic pytest plotly streamlit


lancer 

uv run streamlit run app_streamlit.py


ouvrir le notebooks pour le test :


jupyter notebook notebooks/test_charts.ipynb


5. Visualisations incluses

Carte interactive avec scatter_mapbox (fond sombre ou clair selon le thème).

Histogrammes et bar charts pour statistiques par ville.

Scatter plots pour corrélations entre variables numériques.

Population moyenne par ville.

Matrice de corrélation.


8. chatbot

Interagit avec le dataset via la classe DataChatbot.

Réponses dynamiques aux questions de l’utilisateur.

Suggestions de questions prédéfinies : villes les plus peuplées, corrélations, analyses automatiques.


9. Conclusion

Ce projet illustre :

La mise en place d’un pipeline GEO modulaire et reproductible.

L’intégration de données enrichies et nettoyées pour des analyses interactives.

La visualisation de données géographiques et statistiques via Plotly.

L’utilisation de Streamlit pour créer un dashboard interactif.

L’intégration d’un chatbot pour faciliter l’analyse exploratoire.