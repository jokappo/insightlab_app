# InsightLab

InsightLab est une plateforme de surveillance des marches financiers. Elle collecte des historiques et des cotations en continu, calcule des indicateurs de volatilite, produit des predictions et expose les resultats dans un tableau de bord React.

> Ce projet est un outil de demonstration et d'experimentation. Les predictions ne constituent pas un conseil financier.

## Fonctionnalites

- Ingestion historique depuis Yahoo Finance avec `yfinance`.
- Pipeline de nettoyage, calcul de rendements, volatilites glissantes et moyennes mobiles.
- Stockage des donnees brutes et traitees dans PostgreSQL.
- Ingestion temps reel via Kafka.
- Comparaison de modeles Ridge, Random Forest et Gradient Boosting, avec validation temporelle et evaluation sur un jeu de test.
- Predictions de volatilite et alertes basees sur un z-score.
- API REST FastAPI et interface React avec graphiques, alertes et simulation de choc de marche.
- Orchestration quotidienne du pipeline batch avec Apache Airflow.

Les actifs suivis par defaut sont `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `BTC-USD` et `^GSPC`.

## Architecture

```text
Yahoo Finance
		|                         +--> Ingestion batch --> PostgreSQL
		+--> Producer Kafka --> Kafka --> Consumer ------+
																											 |
PostgreSQL --> Nettoyage --> Feature Store --> Modele ML --> Predictions et alertes
																											 |
																								FastAPI --> Dashboard React

Airflow orchestre le pipeline batch quotidien.
```

| Composant | Role | Adresse locale |
| --- | --- | --- |
| PostgreSQL | Data lake relationnel | `localhost:5432` |
| Kafka | Transport des cotations en continu | `localhost:9092` |
| API FastAPI | Donnees, predictions, alertes et simulations | `http://localhost:8000` |
| Documentation API | Swagger UI | `http://localhost:8000/docs` |
| Dashboard React | Interface de suivi | `http://localhost:5173` |
| Airflow | Orchestration du batch | `http://localhost:8080` |

`docker-compose.yml` demarre l'infrastructure (PostgreSQL, Kafka, ZooKeeper et Airflow). L'API, le producteur/consommateur Kafka et le dashboard sont lances separement avec les commandes ci-dessous.

## Prerequis

- Docker Desktop avec Docker Compose.
- Python 3.11 ou plus recent.
- Node.js compatible avec Vite 8 (Node.js 20.19+ ou 22.12+) et pnpm via Corepack.
- Une connexion Internet pour telecharger les donnees Yahoo Finance.

## Demarrage rapide

### 1. Configuration et infrastructure

Depuis la racine du depot, creez le fichier de configuration local s'il n'existe pas :

```powershell
Copy-Item .env.example .env
```

Sur macOS/Linux, utilisez `cp .env.example .env`.

Demarrez PostgreSQL :

```powershell
docker compose up -d postgres
```

Le schema est initialise par `init.sql` au premier demarrage du volume PostgreSQL. Pour lancer aussi Kafka et Airflow, demarrez toute l'infrastructure :

```powershell
docker compose up -d
```

Airflow est alors disponible sur `http://localhost:8080` avec les identifiants locaux `admin` / `admin`. Cette configuration est reservee au developpement local.

### 2. Environnement Python

Dans un terminal a la racine du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn pandas numpy yfinance sqlalchemy psycopg2-binary python-dotenv joblib scikit-learn kafka-python
```

Sur macOS/Linux, activez l'environnement avec `source .venv/bin/activate`.

Les dependances Python ne sont pas encore gerees par un fichier `requirements.txt`; la commande ci-dessus installe les paquets utilises par les scripts et l'API.

### 3. Executer le pipeline batch

Lancez les scripts dans cet ordre. L'ingestion recupere les donnees historiques, puis le traitement prepare les indicateurs et les features necessaires a l'entrainement :

```powershell
python ingestion/batch_ingest.py
python processing/clean_transform.py
python features/feature_store.py
python ml/train_model.py
python ml/predict.py
```

Le modele entraine est enregistre dans `models/volatility_model.joblib`. L'ingestion depend de l'acces Internet et les commandes basees sur PostgreSQL supposent que le conteneur de base de donnees est demarre.

### 4. Lancer l'API

Dans un terminal a la racine, avec l'environnement Python active :

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Verifiez l'API sur `http://localhost:8000/health` et la connexion a PostgreSQL sur `http://localhost:8000/ready`.

### 5. Lancer le dashboard

Dans un autre terminal :

```powershell
cd dashboard-react
corepack pnpm install
corepack pnpm dev
```

Ouvrez `http://localhost:5173`. Le dashboard utilise `http://localhost:8000` par defaut. Pour utiliser une autre adresse d'API, definissez `VITE_API_URL` dans un fichier `dashboard-react/.env.local`, par exemple `VITE_API_URL=http://localhost:8000`.

## Ingestion Kafka en continu

Demarrez Kafka (et ZooKeeper, demarre automatiquement comme dependance) :

```powershell
docker compose up -d kafka
```

Avec l'environnement Python active, ouvrez deux terminaux a la racine. Lancez d'abord le consommateur :

```powershell
python ingestion/kafka_consumer.py
```

Puis lancez le producteur :

```powershell
python ingestion/kafka_producer.py
```

Le producteur publie les dernieres cotations Yahoo Finance dans le topic `market-ticks` a intervalles reguliers; le consommateur les ecrit dans `raw_streaming`. Arretez chaque processus avec `Ctrl+C`.

## Orchestration Airflow

Avec les services Docker demarres, ouvrez `http://localhost:8080`, connectez-vous (`admin` / `admin` en configuration locale), puis activez le DAG `insightlab_batch_pipeline`. Le DAG execute quotidiennement, dans l'ordre : ingestion historique, nettoyage, construction du feature store, entrainement et prediction.

## API REST

La documentation interactive complete est disponible sur `http://localhost:8000/docs`.

| Methode | Route | Description |
| --- | --- | --- |
| `GET` | `/health` | Verifie que l'API repond. |
| `GET` | `/ready` | Verifie la connexion a PostgreSQL. |
| `GET` | `/tickers` | Liste les actifs suivis. |
| `GET` | `/processed/{ticker}` | Indicateurs traites pour un actif. |
| `GET` | `/predictions/latest` | Derniere prediction par actif. |
| `GET` | `/predictions/{ticker}` | Historique des predictions d'un actif. |
| `GET` | `/alerts/{ticker}` | Alertes d'un actif. |
| `POST` | `/simulation/market-shock` | Simule un choc de prix, puis renvoie prediction et alertes. |

Exemple de simulation :

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/simulation/market-shock `
	-ContentType 'application/json' `
	-Body '{"ticker":"AAPL","shock_percent":-8}'
```

Le parametre `shock_percent` accepte une valeur comprise entre `-50` et `50`. Une simulation necessite des donnees historiques et un modele utilisable.

## Structure du depot

```text
airflow/dags/       DAG du pipeline batch
alerts/             Detection des alertes de volatilite
api/                API FastAPI
dashboard-react/    Interface React + Vite
features/            Construction du feature store
ingestion/           Ingestion batch et Kafka
ml/                  Entrainement et predictions
models/              Modele serialise
processing/          Nettoyage et indicateurs
config.py            Configuration et actifs suivis
datalake_utils.py    Acces PostgreSQL et fonctions de lecture/ecriture
docker-compose.yml   PostgreSQL, Kafka, ZooKeeper et Airflow
init.sql             Schema initial du Data Lake
```

Les tables principales sont `raw_historical`, `raw_streaming`, `processed`, `features`, `predictions` et `alerts`.

## Depannage et securite

- **L'API ne se connecte pas a PostgreSQL** : verifiez `docker compose ps`, attendez que PostgreSQL soit pret et assurez-vous que les valeurs de `.env` correspondent a celles de `docker-compose.yml`.
- **Le dashboard est vide** : executez d'abord le pipeline batch et verifiez que l'API repond sur `http://localhost:8000/ready`.
- **Un port est deja utilise** : liberez le port concerne ou modifiez le mapping dans `docker-compose.yml` et l'URL configuree pour le client.
- **Kafka ne renvoie aucun message** : lancez le consommateur et le producteur, puis verifiez que Kafka est disponible sur `localhost:9092`.
- Les identifiants Docker et Airflow du depot sont des valeurs de demonstration. Ne les utilisez pas en production; remplacez-les et ne publiez jamais votre fichier `.env`.

## Scripts du dashboard

Depuis `dashboard-react/` :

```powershell
corepack pnpm dev      # serveur de developpement
corepack pnpm build    # compilation de production
corepack pnpm lint     # analyse ESLint
corepack pnpm preview  # apercu de la compilation
```
