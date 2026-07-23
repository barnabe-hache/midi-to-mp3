# Guide méthodologique — Créer et déployer un site web full-stack (de zéro à la production)

> Ce document est un **guide personnel réutilisable**. Il retrace, étape par étape, la méthode complète suivie pour construire et déployer Notewave (convertisseur MIDI → MP3), depuis l'initialisation du projet jusqu'à la mise en ligne avec nom de domaine et HTTPS. L'objectif est de pouvoir reprendre ce document comme trame pour un futur projet similaire (une app web avec backend Python/API + frontend + déploiement VPS), sans avoir à tout redécouvrir.
>
> Pour le contexte spécifique au projet Notewave (arborescence exacte, décisions techniques précises, état d'avancement), voir `CONTEXT.md` — ce README-ci est volontairement généraliste et méthodologique.

---

## Table des matières

1. [Vue d'ensemble de la stack technique](#1-vue-densemble-de-la-stack-technique)
2. [Phase 1 — Initialisation du projet et Git](#2-phase-1--initialisation-du-projet-et-git)
3. [Phase 2 — Setup du backend (API Python)](#3-phase-2--setup-du-backend-api-python)
4. [Phase 3 — Setup du frontend (Vue.js)](#4-phase-3--setup-du-frontend-vuejs)
5. [Phase 4 — Développement itératif (logique métier)](#5-phase-4--développement-itératif-logique-métier)
6. [Phase 5 — Limites d'usage et robustesse (avant mise en ligne)](#6-phase-5--limites-dusage-et-robustesse-avant-mise-en-ligne)
7. [Phase 6 — Landing page statique (SEO)](#7-phase-6--landing-page-statique-seo)
8. [Phase 7 — Design et identité visuelle](#8-phase-7--design-et-identité-visuelle)
9. [Phase 8 — Préparer le code pour la production](#9-phase-8--préparer-le-code-pour-la-production)
10. [Phase 9 — Dockerisation du backend](#10-phase-9--dockerisation-du-backend)
11. [Phase 10 — Déploiement sur VPS (avec IP, avant domaine)](#11-phase-10--déploiement-sur-vps-avec-ip-avant-domaine)
12. [Phase 11 — Nom de domaine, DNS et HTTPS](#12-phase-11--nom-de-domaine-dns-et-https)
13. [Phase 12 — Workflow de mise à jour continue](#13-phase-12--workflow-de-mise-à-jour-continue)
14. [Phase 13 — SEO avancé](#14-phase-13--seo-avancé)
15. [Phase 14 — Analytics simple](#15-phase-14--analytics-simple)
16. [Sécurité — check-list à ne pas sauter avant une vraie mise en production](#16-sécurité--check-list-à-ne-pas-sauter-avant-une-vraie-mise-en-production)
17. [Bugs rencontrés et leçons apprises](#17-bugs-rencontrés-et-leçons-apprises)
18. [Check-list rapide pour un nouveau projet similaire](#18-check-list-rapide-pour-un-nouveau-projet-similaire)

---

## 1. Vue d'ensemble de la stack technique

Pour un projet de type "outil web avec traitement côté serveur" (fichiers uploadés, calcul, fichier généré en retour), la stack suivante a fait ses preuves :

| Couche | Techno | Pourquoi |
|---|---|---|
| Frontend (page interactive) | Vue 3 + TypeScript + Vite | Réactivité nécessaire dès qu'il y a un état complexe (formulaires liés, affichage conditionnel, appels API asynchrones). Vite = build rapide, dev server avec hot-reload. |
| Landing page (page vitrine) | HTML/CSS pur, sans framework | Aucune interactivité complexe nécessaire ; meilleur pour le SEO (contenu directement dans le HTML, pas besoin d'exécuter du JS pour que Google le voie) ; zéro dépendance, zéro build. |
| Backend / API | Python + FastAPI | Rapide à écrire, typé (Pydantic), documentation interactive auto-générée (`/docs`), asynchrone nativement (utile pour les tâches longues), écosystème Python riche si calcul/traitement de fichiers. |
| Conteneurisation backend | Docker | Empaquette le code + toutes ses dépendances système (binaires externes inclus) dans une image portable, indépendante de l'OS hôte. Essentiel dès que le backend dépend de binaires non-Python. |
| Reverse proxy / serveur web | Nginx | Sert les fichiers statiques (landing, frontend buildé), redirige les requêtes API vers le conteneur backend, gère HTTPS. Standard de l'industrie, gratuit, très documenté. |
| Hébergement | VPS (Hostinger, ou équivalent : OVH, Contabo, DigitalOcean...) | Contrôle total, coût prévisible et bas, adapté dès que le backend fait du vrai calcul (élimine les solutions serverless "légères" qui limitent le temps d'exécution). |
| HTTPS | Let's Encrypt via Certbot | Gratuit, renouvellement automatique, standard. |
| Nom de domaine | N'importe quel registrar (Namecheap, OVH, Hostinger, Cloudflare Registrar...) | Comparer les prix, pas de différence technique majeure. |
| Analytics | Cloudflare Web Analytics | Gratuit, sans cookie (pas de bandeau RGPD nécessaire), suffisant pour un simple comptage de trafic. |

### Principe directeur : ne pas sur-ingénierer au démarrage

Tout au long du projet, la règle a été : **ajouter de la complexité seulement quand elle devient nécessaire**, pas par anticipation. Exemples concrets de ce principe appliqué :
- Pas de base de données tant qu'aucune fonctionnalité ne l'exige réellement (comptes utilisateurs, crédits payants) — tout le traitement MIDI→MP3 reste **stateless** (aucune donnée utilisateur stockée).
- Pas de système de connexion/compte tant que rien ne le justifie (pas de compte tant que tout est gratuit et illimité).
- Déploiement **manuel** plutôt qu'un pipeline CI/CD complexe — justifié pour un projet solo à ce stade, garde le contrôle total et la simplicité de compréhension.

Ce principe est à garder en tête pour un futur projet : commencer simple, complexifier seulement quand un besoin réel apparaît.

---

## 2. Phase 1 — Initialisation du projet et Git

### Structure de dossier recommandée (mono-repo)

Pour un projet avec landing page + outil + backend, structure en 3 dossiers séparés à la racine :

```
mon-projet/
├── .gitignore
├── README.md
├── docker-compose.yml
├── backend/
├── frontend/
└── landing/
```

### Commandes d'initialisation

```powershell
mkdir mon-projet
cd mon-projet
git init
mkdir backend
mkdir frontend
mkdir landing
```

### `.gitignore` type pour ce genre de projet

```
# Python
backend/venv/
__pycache__/
*.pyc
backend/.env

# Node / Vue
frontend/node_modules/
frontend/dist/

# Fichiers système
.DS_Store
Thumbs.db

# Editeurs
.vscode/
.idea/
```

Point important : les fichiers `.env` contenant de la configuration sensible ou spécifique à l'environnement (URLs, origines CORS...) doivent être ignorés par Git — voir section dédiée plus bas sur la gestion des `.env`.

### Rituel Git de base à connaître

| Commande | Usage |
|---|---|
| `git status` | Voir ce qui a changé depuis le dernier commit |
| `git add .` | Préparer tous les fichiers modifiés pour le prochain commit |
| `git commit -m "message clair"` | Créer un point de sauvegarde dans l'historique |
| `git push` | Envoyer les commits vers le dépôt distant (GitHub) |
| `git pull` | Récupérer les derniers commits depuis le dépôt distant |
| `git log --oneline` | Voir l'historique condensé des commits |

### Créer le dépôt distant (GitHub)

1. Créer un compte sur https://github.com si besoin
2. "New repository" → nom du projet → **Private** (recommandé par défaut, peut être rendu public plus tard si le code n'a rien de sensible) → ne cocher aucune case d'initialisation (pas de README/gitignore auto, le projet local en a déjà)
3. Relier le repo local :
```powershell
git remote add origin https://github.com/TON_USERNAME/nom-du-repo.git
git branch -M main
git push -u origin main
```
4. GitHub demandera une authentification — depuis 2021, GitHub n'accepte plus le mot de passe classique en ligne de commande, il faut un **Personal Access Token** (généré depuis Settings → Developer settings → Personal access tokens) utilisé à la place du mot de passe.

**Piège Windows à connaître** : Windows est insensible à la casse dans les noms de fichiers (`Piano.sf2` == `piano.sf2`), contrairement à Linux (le VPS). Si tu renommes un fichier en changeant juste la casse, `git add .` peut ne rien détecter. Solution : utiliser `git mv ancien_nom nouveau_nom` explicitement, éventuellement en passant par un nom temporaire si le renommage direct échoue.

---

## 3. Phase 2 — Setup du backend (API Python)

### Créer l'environnement virtuel

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate
```

Si erreur de politique d'exécution PowerShell : lancer PowerShell **en administrateur** une fois et faire :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### `requirements.txt` de base pour une API FastAPI

```
fastapi
uvicorn[standard]
python-multipart
python-dotenv
```
(ajouter les libs spécifiques au projet ensuite — traitement de fichiers, calcul, etc.)

```powershell
pip install -r requirements.txt
```

### Structure de dossiers backend recommandée

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py               ← point d'entrée FastAPI
│   ├── limiter.py            ← rate limiting (si besoin, voir Phase 5)
│   ├── routers/               ← un fichier par domaine fonctionnel (endpoints)
│   ├── services/               ← logique métier pure, découplée des endpoints
│   └── models/                 ← schémas Pydantic (validation des requêtes/réponses)
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env                        ← config locale, jamais commité
└── .env.example                 ← modèle documenté, commité
```

Le découpage `routers/` (endpoints HTTP) vs `services/` (logique métier) permet de tester/réutiliser la logique indépendamment du framework web, et de garder chaque fichier court et lisible.

### `main.py` minimal de départ

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # à rendre configurable, voir Phase 8
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

**Le CORS est essentiel dès le départ** : un navigateur bloque par défaut les requêtes entre origines différentes (ex: `localhost:5173` → `localhost:8000`). Sans ce middleware, toutes les requêtes frontend→backend échoueront silencieusement avec une erreur CORS visible uniquement dans la console développeur.

### Lancer le serveur de dev

```powershell
uvicorn app.main:app --reload --port 8000
```

Vérifier `http://localhost:8000/health` et `http://localhost:8000/docs` (documentation interactive Swagger générée automatiquement — très utile pour tester chaque endpoint au fur et à mesure, sans avoir besoin du frontend).

---

## 4. Phase 3 — Setup du frontend (Vue.js)

### Prérequis : Node.js

Télécharger la version **LTS** depuis https://nodejs.org. Vérifier :
```powershell
node --version
npm --version
```

### Créer le projet avec Vite

```powershell
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm run dev
```

Le serveur de dev tourne par défaut sur `http://localhost:5173`.

### Structure de composants recommandée

```
frontend/src/
├── App.vue                 ← composant racine, orchestre l'état global
├── main.ts
├── style.css                ← design tokens (couleurs, typo) en variables CSS
├── components/                ← un composant par bloc d'UI réutilisable/isolable
├── composables/
│   └── useApi.ts              ← TOUS les appels au backend centralisés ici
└── types/
    └── index.ts                ← types TypeScript partagés (évite la duplication)
```

**Principe clé** : centraliser tous les appels HTTP dans un seul fichier (`useApi.ts`). Les composants ne font jamais `fetch` directement — ils appellent des fonctions exportées par ce fichier. Avantage concret : le jour où l'URL du backend change (déploiement), un seul fichier à modifier.

### Design tokens — variables CSS dès le départ

Poser un système de variables CSS dans `style.css` dès le début évite d'avoir des couleurs/tailles codées en dur partout dans les composants :

```css
:root {
  --color-bg: #F5F5F3;
  --color-surface: #FFFFFF;
  --color-ink: #16181D;
  --color-ink-muted: #5B6169;
  --color-border: #E2E4E8;
  --color-signal: #2F6F5E;   /* couleur d'accent principale */
  --font-display: 'Nom de police', sans-serif;
  --font-body: 'Nom de police', sans-serif;
  --radius-sm: 8px;
  --radius-md: 14px;
}
```

Chaque composant Vue référence ensuite `var(--color-signal)` etc. dans son `<style scoped>` — cohérence visuelle garantie, changement de thème centralisé.

---

## 5. Phase 4 — Développement itératif (logique métier)

Méthode suivie tout du long, à reproduire :

1. **Un endpoint backend à la fois**, testé isolément via Swagger (`/docs`) avant de brancher le frontend dessus. Ça isole immédiatement si un bug vient du backend ou du frontend.
2. **Un composant frontend à la fois**, branché sur son endpoint, testé visuellement avant de passer au suivant.
3. **Toujours prévoir un état de chargement / erreur** pour chaque action asynchrone (upload, traitement, etc.) — ne jamais supposer que l'action réussira instantanément.
4. **Logger les erreurs serveur en détail** (`traceback.print_exc()` côté Python) pour que les messages d'erreur dans le terminal soient exploitables, plutôt que des messages génériques du type "Internal Server Error" sans plus de détail.

### Exemple de pattern d'endpoint robuste (Python/FastAPI)

```python
@router.post("")
async def mon_endpoint(fichier: UploadFile = File(...)):
    if not fichier.filename.lower().endswith((".ext_attendue",)):
        raise HTTPException(400, "Message clair pour l'utilisateur")

    try:
        # logique métier ici
        ...
    except HTTPException:
        raise
    except Exception as e:
        print("=== ERREUR ===")
        traceback.print_exc()
        raise HTTPException(500, f"Erreur serveur: {e}")
```

### Gestion des fichiers temporaires (traitement stateless)

Si le projet traite des fichiers sans les stocker durablement (comme Notewave), utiliser `tempfile.TemporaryDirectory()` en Python — supprime automatiquement tout son contenu à la fin du bloc `with`, garantissant qu'aucune trace ne persiste sur le serveur après une requête.

```python
with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_dir_path = Path(tmp_dir)
    # tous les fichiers intermédiaires ici
    # tout est supprimé automatiquement à la sortie du bloc
```

---

## 6. Phase 5 — Limites d'usage et robustesse (avant mise en ligne)

Avant d'exposer un backend qui fait du calcul réel au public, mettre en place, même en version gratuite :

### Rate limiting (limiter le nombre de requêtes par utilisateur/IP)

```powershell
pip install slowapi
```

```python
# limiter.py — fichier séparé pour éviter les imports circulaires
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

```python
# main.py
from app.limiter import limiter
from slowapi.errors import RateLimitExceeded

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Limite atteinte, réessaie plus tard."})
```

```python
# routers/mon_router.py
from app.limiter import limiter

@router.post("")
@limiter.limit("10/day")
async def mon_endpoint(request: Request, ...):  # request: Request est OBLIGATOIRE en premier paramètre
    ...
```

### Limite de taille de fichier uploadé

```python
MAX_SIZE_BYTES = 4 * 1024 * 1024  # 4 Mo

content = await fichier.read()
if len(content) > MAX_SIZE_BYTES:
    raise HTTPException(413, "Fichier trop volumineux")
await fichier.seek(0)  # remet le curseur au début pour la lecture suivante
```

### Timeout sur un traitement potentiellement long

```python
import asyncio

try:
    resultat = await asyncio.wait_for(
        asyncio.to_thread(fonction_bloquante_synchrone, arg1, arg2),
        timeout=90.0,
    )
except asyncio.TimeoutError:
    raise HTTPException(504, "Traitement trop long, annulé")
```

`asyncio.to_thread` est nécessaire si la fonction appelée est du code **synchrone/bloquant** (appels à des binaires externes, calcul lourd) — sans ça, `asyncio.wait_for` ne peut pas réellement interrompre l'exécution.

---

## 7. Phase 6 — Landing page statique (SEO)

### Pourquoi séparer la landing du reste

Une page d'accueil orientée SEO n'a généralement besoin d'aucune interactivité complexe — HTML/CSS pur est préférable à un framework JS pour deux raisons : Google indexe plus facilement du contenu déjà présent dans le HTML brut (pas besoin d'exécuter du JS pour le "voir"), et ça évite d'alourdir inutilement une simple page vitrine.

### Structure minimale

```
landing/
├── index.html
├── style.css
├── robots.txt
├── sitemap.xml
└── assets/
    └── (images, logos, démos audio/vidéo...)
```

### Éléments SEO indispensables dans le `<head>`

```html
<title>Titre clair avec le mot-clé principal</title>
<meta name="description" content="Description en 1-2 phrases, avec les mots-clés naturellement intégrés." />
<link rel="canonical" href="https://tondomaine.com/" />
<link rel="icon" type="image/svg+xml" href="assets/logo.svg" />

<!-- Open Graph : contrôle l'aperçu quand le lien est partagé (réseaux sociaux, Slack, etc.) -->
<meta property="og:type" content="website" />
<meta property="og:url" content="https://tondomaine.com/" />
<meta property="og:title" content="Même titre ou variante" />
<meta property="og:description" content="Même description ou variante" />
<meta property="og:image" content="https://tondomaine.com/assets/og-image.png" />  <!-- 1200x630px -->
```

### Données structurées (schema.org) — aide Google à afficher des résultats enrichis

Exemple pour une FAQ (peut apparaître directement dans les résultats de recherche Google sous forme de questions dépliables) :

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question exacte",
      "acceptedAnswer": { "@type": "Answer", "text": "Réponse complète en une phrase claire." }
    }
  ]
}
</script>
```

### `robots.txt` et `sitemap.xml`

```
# robots.txt
User-agent: *
Allow: /
Sitemap: https://tondomaine.com/sitemap.xml
```

```xml
<!-- sitemap.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://tondomaine.com/</loc>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

### Contenu textuel qui aide vraiment le SEO

- Un seul `<h1>` par page, hiérarchie `<h2>`/`<h3>` logique
- Une section FAQ (excellent pour le référencement longue traîne — les gens tapent des questions complètes dans Google)
- Des attributs `alt` descriptifs sur toutes les images
- Éviter le contenu dupliqué (d'où l'intérêt du `rel="canonical"`, surtout si le site répond à la fois sur `tondomaine.com` et `www.tondomaine.com`)

### Accélérer l'indexation avec Google Search Console (gratuit)

1. https://search.google.com/search-console → ajouter la propriété avec le domaine
2. Vérification via un enregistrement DNS TXT (ajouté chez le registrar du domaine)
3. Une fois vérifié : "Inspection d'URL" → soumettre l'URL principale → demander l'indexation

Sans ça, Google peut mettre plusieurs semaines à découvrir un site tout neuf sans aucun lien externe pointant vers lui. Avec la demande d'indexation manuelle, ça peut être pris en compte en quelques heures à quelques jours.

---

## 8. Phase 7 — Design et identité visuelle

### Méthode suivie : s'inspirer d'un site existant plutôt que partir de zéro

Identifier un site dont le style plaît (disposition, couleurs, typographie, ambiance générale), en extraire les patterns réutilisables (header sticky flouté, formes décoratives en arrière-plan, cartes avec effet de survol, etc.), puis les adapter avec sa propre palette de couleurs et son propre contenu — plutôt que de copier tel quel.

### Éléments qui donnent un rendu "pro" à moindre effort

- **Header sticky avec effet de flou** (`backdrop-filter: blur(...)`) qui reste visible au scroll
- **Formes décoratives en arrière-plan** : cercles flous en dégradé, opacité faible (0.2-0.35), positionnés en `fixed`, `z-index: -1`, `pointer-events: none` pour ne jamais interférer avec les clics
- **Micro-interactions au survol** : légère élévation (`transform: translateY(-2px)`) + ombre portée sur les cartes/boutons, transition douce (`transition: transform 0.15s ease`)
- **Dégradés subtils** sur les CTA plutôt que des couleurs plates
- **Une palette réduite mais cohérente** : 1 couleur d'accent principale + 1 secondaire, décliné en versions "soft" (fond très clair de la même teinte) pour les états sélectionnés/survol

### Éviter les patterns trop génériques ("ça fait IA")

- Éviter les grilles de cartes avec icône-carrée + titre + texte pour lister des features — préférer une liste éditoriale numérotée avec liseré, plus distinctive
- Éviter les CTA finaux en pleine largeur avec fond dégradé plein écran — souvent trop imposant, préférer une carte neutre avec juste le bouton en accent

### Outils de design gratuits

Figma (gratuit pour un usage individuel) reste la référence si on veut maquetter avant de coder. Mais pour un projet simple, itérer directement en code (comme fait ici) avec des retours visuels rapides fonctionne très bien aussi, surtout avec l'aide d'un assistant IA pour proposer et ajuster rapidement.

---

## 9. Phase 8 — Préparer le code pour la production

Avant tout déploiement, remplacer les valeurs codées en dur par de la configuration.

### Frontend (Vite) — variables d'environnement

```
# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000
```
```
# frontend/.env.production
VITE_API_BASE_URL=/api
```

Utilisation dans le code :
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
```

Vite choisit automatiquement le bon fichier selon la commande (`npm run dev` → `.env.development`, `npm run build` → `.env.production`). Le `/api` en production correspond au préfixe que Nginx redirigera en interne vers le backend (voir Phase 10) — évite d'exposer directement l'adresse et le port du backend.

Ces fichiers `.env.*` (sans données sensibles) peuvent être commités sans risque — c'est utile pour que la config soit versionnée avec le code.

### Backend (FastAPI) — variables d'environnement sensibles/spécifiques au serveur

```
# backend/.env (jamais commité)
CORS_ORIGINS=http://localhost:5173
```
```
# backend/.env.example (commité, sert de modèle)
CORS_ORIGINS=http://localhost:5173
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
```

Le `.split(",")` permet de mettre plusieurs origines séparées par des virgules si besoin (ex: avec et sans `www`).

---

## 10. Phase 9 — Dockerisation du backend

### Pourquoi conteneuriser (surtout si le backend dépend de binaires système)

Un backend Python qui appelle des binaires externes (ffmpeg, un moteur de rendu, etc.) ne peut pas se réduire à un simple `pip install` sur le serveur — il faut aussi installer ces binaires au niveau système. Docker permet d'empaqueter **tout ça ensemble** (Python + dépendances + binaires système) dans une image portable, construite une fois, déployable identiquement sur n'importe quelle machine ayant juste Docker installé.

### `backend/Dockerfile` type

```dockerfile
FROM python:3.11-slim

# Binaires système nécessaires (adapter selon le projet)
RUN apt-get update && apt-get install -y \
    nom-du-binaire-1 \
    nom-du-binaire-2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Utilisateur non-root : bonne pratique de sécurité
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `backend/.dockerignore`

```
venv/
__pycache__/
*.pyc
.env
.git/
```

### `docker-compose.yml` (racine du projet)

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "127.0.0.1:8000:8000"   # accessible seulement en local sur le serveur, Nginx fait le proxy
    env_file:
      - ./backend/.env
    restart: unless-stopped
```

`restart: unless-stopped` relance automatiquement le conteneur en cas de crash ou de redémarrage du serveur — important en production.

**Note sur le port** : `"127.0.0.1:8000:8000"` restreint l'accès au localhost du serveur uniquement (pas exposé publiquement) — c'est Nginx qui fera ensuite le lien entre l'extérieur et ce port interne. Pendant les tests initiaux, on peut temporairement utiliser juste `"8000:8000"` pour tester sans Nginx, mais il faut sécuriser avant la mise en production réelle.

### Commandes de base Docker Compose

```bash
docker compose up --build -d    # build + lance en arrière-plan
docker compose ps               # état des conteneurs
docker compose logs -f          # logs en direct (Ctrl+C pour sortir de l'affichage, ne stoppe pas le conteneur)
docker compose down             # arrête et supprime les conteneurs
```

**Point clé à retenir** : `docker compose up --build` ne rebuild que si le `Dockerfile`, les fichiers copiés (`COPY . .`), ou les dépendances ont changé. **Il faut TOUJOURS `--build` après une modification du code backend** — le conteneur ne "voit" pas les changements de fichiers après coup, il tourne sur la version figée au moment du build. En revanche, aucun rebuild n'est nécessaire pour du contenu qui n'est pas conteneurisé (landing statique, frontend Vue) — ces parties sont juste des fichiers copiés directement, pas de Docker impliqué pour elles.

---

## 11. Phase 10 — Déploiement sur VPS (avec IP, avant domaine)

Il est tout à fait viable (et recommandé) de valider le déploiement complet via l'**adresse IP du VPS** avant même d'acheter un nom de domaine — ça permet d'isoler et de résoudre les problèmes d'infrastructure sans attendre la propagation DNS. Seul HTTPS (Let's Encrypt) nécessite un vrai domaine et doit donc attendre la phase suivante.

### 1. Connexion SSH

```powershell
ssh root@IP_DU_VPS
```

### 2. Mise à jour du système + installation de Docker

```bash
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
docker --version
docker compose version
docker run hello-world   # test que Docker fonctionne
```

### 3. Installation de Nginx

```bash
apt install nginx -y
systemctl status nginx   # doit afficher "active (running)"
```

Tester `http://IP_DU_VPS` depuis un navigateur → doit afficher la page par défaut de Nginx.

### 4. Pare-feu de base (ufw)

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
ufw status
```

`OpenSSH` est indispensable pour ne pas se couper l'accès SSH soi-même — piège classique à éviter.

### 5. Installer Git et cloner le repo

```bash
apt install git -y
git clone https://github.com/TON_USERNAME/ton-repo.git
cd ton-repo
```

Pour un repo privé, GitHub demandera un **Personal Access Token** en guise de mot de passe.

### 6. Créer le `.env` du backend directement sur le serveur

Ce fichier n'existe jamais dans Git — il doit être créé manuellement, une seule fois, sur chaque nouvel environnement :

```bash
cd backend
nano .env
```
Contenu (adapter l'IP/domaine) :
```
CORS_ORIGINS=http://IP_DU_VPS
```
Sauvegarder avec `nano` : `Ctrl+O` → `Entrée` → `Ctrl+X`.

### 7. Lancer le backend

```bash
cd ..   # retour à la racine du projet
docker compose up --build -d
docker compose logs -f    # vérifier "Uvicorn running on http://0.0.0.0:8000"
```

### 8. Installer Node.js (nécessaire pour builder le frontend Vue sur le serveur)

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
apt install -y nodejs
node --version
```

### 9. Builder le frontend et déployer les fichiers statiques

```bash
cd frontend
npm install
npm run build              # génère frontend/dist/
cd ..

mkdir -p /var/www/ton-projet/landing
mkdir -p /var/www/ton-projet/app

cp -r landing/* /var/www/ton-projet/landing/
cp -r frontend/dist/* /var/www/ton-projet/app/
```

### 10. Configurer Nginx comme routeur

```bash
nano /etc/nginx/sites-available/ton-projet
```

```nginx
server {
    listen 80;
    server_name IP_DU_VPS;

    # Landing page à la racine
    location / {
        root /var/www/ton-projet/landing;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # Outil/app en sous-dossier
    location /app {
        alias /var/www/ton-projet/app;
        index index.html;
        try_files $uri $uri/ /app/index.html;   # important pour les apps single-page
    }

    # API backend en proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;      # le "/" final retire le préfixe /api avant transmission
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Piège à éviter** : bien vérifier que le nom du fichier créé avec `nano` correspond exactement au nom utilisé dans la commande `ln -s` suivante — une divergence silencieuse ici (créer un fichier sous un nom différent de celui qu'on croit) fait qu'on édite un fichier qui n'est jamais réellement chargé par Nginx.

```bash
ln -s /etc/nginx/sites-available/ton-projet /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default   # retire la page par défaut
nginx -t                               # vérifie la syntaxe AVANT de recharger
systemctl reload nginx                 # ⚠️ étape facile à oublier — sans elle, les changements ne sont jamais appliqués
```

**Piège à connaître (Vite + sous-dossier)** : si l'app Vue est servie depuis un sous-chemin comme `/app` (pas la racine `/`), il faut le déclarer explicitement dans `vite.config.ts`, sinon les fichiers JS/CSS générés seront référencés avec des chemins absolus depuis la racine et ne se chargeront jamais (page blanche sans erreur visible à l'écran, juste des 404 dans la console développeur) :

```typescript
// vite.config.ts
export default defineConfig({
  base: '/app/',   // doit correspondre exactement au sous-chemin utilisé dans Nginx
  plugins: [vue()],
})
```

Puis rebuild (`npm run build`) et recopier `dist/*` vers le dossier servi par Nginx.

### 11. Fermer l'accès public au port du backend (si testé ouvert au départ)

```bash
ufw delete allow 8000   # si cette règle avait été ajoutée pour des tests
```
Et s'assurer que `docker-compose.yml` utilise bien `"127.0.0.1:8000:8000"` (voir Phase 9).

---

## 12. Phase 11 — Nom de domaine, DNS et HTTPS

### Achat du domaine

N'importe quel registrar fiable (Namecheap, OVH, Cloudflare Registrar, Hostinger...). Vérifier la disponibilité du nom souhaité, comparer les prix (souvent proches, sauf pour certaines extensions premium).

### Configuration DNS — pointer le domaine vers le VPS

Dans l'interface de gestion DNS du registrar, ajouter deux enregistrements de type **A** :

| Type | Host | Valeur | 
|---|---|---|
| A | `@` | IP du VPS |
| A | `www` | IP du VPS |

Propagation DNS : de quelques minutes à quelques heures. Vérifier avec :
```powershell
nslookup tondomaine.com
```

### Mettre à jour Nginx pour utiliser le domaine

```bash
nano /etc/nginx/sites-available/ton-projet
```
Remplacer `server_name IP_DU_VPS;` par :
```nginx
server_name tondomaine.com www.tondomaine.com;
```
```bash
nginx -t
systemctl reload nginx
```

### Mettre à jour le `.env` du backend (CORS)

```bash
cd ~/ton-projet/backend
nano .env
```
```
CORS_ORIGINS=https://tondomaine.com,https://www.tondomaine.com
```
```bash
cd ..
docker compose up -d    # pas besoin de --build, seul le .env a changé
```

### Activer HTTPS avec Certbot (Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d tondomaine.com -d www.tondomaine.com
```

Certbot demande un email (alertes d'expiration), fait accepter les CGU, propose une redirection automatique HTTP→HTTPS (accepter), puis modifie automatiquement la config Nginx pour écouter en HTTPS (port 443) avec le certificat généré.

Vérifier le renouvellement automatique (le certificat expire tous les 90 jours, mais Certbot installe une tâche de renouvellement automatique) :
```bash
systemctl status certbot.timer   # doit être "active"
```

### Tests finaux

- `https://tondomaine.com` → cadenas HTTPS visible, contenu correct
- `http://tondomaine.com` (sans le "s") → doit rediriger automatiquement vers HTTPS
- `https://tondomaine.com/app` (ou équivalent) → l'outil doit fonctionner de bout en bout

---

## 13. Phase 12 — Workflow de mise à jour continue

### Principe (déploiement manuel, choix assumé pour un projet solo)

Après chaque modification testée en local et poussée sur GitHub :

**Sur le PC local**, avant de pousser :
```powershell
git add .
git commit -m "message clair"
git push
```

**Sur le VPS**, selon ce qui a changé :

| Modifié | Commandes sur le VPS |
|---|---|
| Backend (Python) | `git pull` puis `docker compose up --build -d` |
| Frontend (Vue) | `git pull` puis `cd frontend && npm run build && cp -r dist/* /var/www/ton-projet/app/` |
| Landing (HTML/CSS statique) | `git pull` puis `cp -r landing/* /var/www/ton-projet/landing/` |
| `.env` backend | Modifier **directement sur le VPS** (jamais via Git) puis `docker compose up -d` (sans `--build`) |

En cas de doute sur ce qui a changé, il est possible (et sans danger, juste un peu plus long) de systématiquement tout refaire :
```bash
cd ~/ton-projet
git pull
docker compose up --build -d
cd frontend && npm install && npm run build && cp -r dist/* /var/www/ton-projet/app/ && cd ..
cp -r landing/* /var/www/ton-projet/landing/
nginx -t && systemctl reload nginx
```

### Pourquoi rester manuel (pour l'instant)

Pour un projet solo à faible fréquence de déploiement, un pipeline CI/CD automatisé (GitHub Actions, etc.) ajoute de la complexité de configuration et de débogage sans bénéfice proportionnel. Cette étape devient pertinente si la fréquence de déploiement augmente significativement, ou si plusieurs personnes contribuent au projet.

---

## 14. Phase 13 — SEO avancé (une fois le site en ligne)

- **Google Search Console** : vérifier la propriété du domaine (enregistrement DNS TXT), soumettre le sitemap, demander l'indexation explicite des pages principales via "Inspection d'URL"
- Interpréter les résultats de l'inspection d'URL :
  - "Cette URL est sur Google" = bon signe, page indexée
  - "Sitemaps : Erreur de traitement temporaire" = normal si le sitemap n'a pas encore été soumis formellement, pas forcément bloquant
  - "Aucune page d'origine détectée" = normal pour un site neuf sans lien externe pointant vers lui, se résorbe avec le temps et la visibilité
- Le classement sur des requêtes précises prend du temps (semaines) même une fois indexé — c'est lié à l'autorité du domaine (ancienneté, liens entrants) plus qu'à la seule qualité technique du SEO

---

## 15. Phase 14 — Analytics simple

### Pour le trafic (visites) : Cloudflare Web Analytics

Gratuit, sans cookie (pas de bandeau RGPD nécessaire) — suffisant pour un simple comptage de trafic sans complexité.

1. Compte gratuit sur https://dash.cloudflare.com
2. Section "Web Analytics" → ajouter le domaine → récupérer le script fourni
3. Coller le script juste avant `</body>` sur chaque page à suivre (landing ET app si besoin)

### Pour un comptage d'actions métier simple (ex: conversions réussies) : logs applicatifs

Pas besoin d'outil dédié pour un besoin aussi simple — un simple print/log côté backend, comptable via les logs Docker :

```python
print(f"EVENEMENT_SUCCES detail={quelque_chose}")
```

```bash
docker compose logs backend | grep -c "EVENEMENT_SUCCES"
```

Limite à connaître : ces logs ne sont pas un historique durable garanti (peuvent être purgés selon la configuration Docker). Suffisant pour un comptage ponctuel/indicatif ; si un vrai historique fiable dans la durée devient nécessaire, c'est le signe qu'une vraie base de données devient pertinente.

---

## 16. Sécurité — check-list à ne pas sauter avant une vraie mise en production

Points déjà couverts par la méthode ci-dessus :
- [x] Port du backend restreint à `127.0.0.1` (jamais exposé publiquement directement)
- [x] Conteneur Docker tournant en utilisateur non-root
- [x] Pare-feu actif (`ufw`) avec seulement les ports nécessaires ouverts
- [x] Rate-limiting + limite de taille de fichier + timeout sur les endpoints coûteux
- [x] `.env` jamais commité dans Git
- [x] HTTPS actif avec renouvellement automatique

Points identifiés mais **volontairement reportés** (à ne pas oublier pour une mise en production plus sérieuse ou si le trafic grossit) :
- [ ] **SSH par clé uniquement** (désactiver l'authentification par mot de passe) — c'est statistiquement le point d'entrée n°1 exploité sur un VPS, à traiter en priorité si le site prend de l'ampleur
- [ ] **Fail2ban** — bloque automatiquement une IP après plusieurs échecs de connexion SSH
- [ ] **`unattended-upgrades`** — applique automatiquement les patchs de sécurité critiques du système Ubuntu
- [ ] Limites de ressources (CPU/mémoire) sur le conteneur Docker, pour éviter qu'un fichier malveillant ne fasse planter tout le serveur
- [ ] `server_tokens off;` dans la config Nginx (cache la version exacte de Nginx affichée dans les headers de réponse)

---

## 17. Bugs rencontrés et leçons apprises

Une compilation des problèmes concrets rencontrés pendant ce projet — utile pour ne pas retomber dans les mêmes pièges sur un futur projet.

| Symptôme | Cause | Leçon générale |
|---|---|---|
| Erreur 500 générique sans détail | Exception Python non catchée, pas de log de traceback | Toujours entourer la logique métier d'un `try/except` avec `traceback.print_exc()` pour avoir un vrai message exploitable dans les logs serveur |
| `subprocess` échoue avec un binaire externe alors qu'il fonctionne en ligne de commande | Le terminal où tourne le serveur a été ouvert **avant** l'installation/mise à jour du PATH système | Toujours redémarrer complètement le terminal/service après une modification du PATH |
| Erreur "illegal option at this place" avec un outil en ligne de commande | Ordre des arguments incorrect (certains outils exigent que les options précèdent les arguments positionnels) | Toujours vérifier l'ordre exact attendu dans la doc de l'outil, ne pas supposer un ordre "logique" |
| Fichiers `.SF2` (majuscules) invisibles alors que présents | `Path.glob("*.sf2")` est sensible à la casse sous Linux (pas sous Windows) | Ne jamais compter sur le comportement Windows par défaut pour la casse des fichiers ; comparer explicitement en minuscule (`f.suffix.lower() == ".ext"`) dans le code pour un comportement cohérent cross-plateforme |
| `git add .` ne détecte aucun changement après un renommage de fichier (casse seulement) | Windows insensible à la casse dans les noms de fichiers, contrairement à Git/Linux | Utiliser `git mv ancien nouveau` explicitement pour un renommage de casse, éventuellement via un nom temporaire intermédiaire |
| Son avec grésillement sur les notes fortes | Gain audio forcé trop élevé en amont du pipeline, créant un écrêtage numérique irréversible avant même les étapes de traitement suivantes | Ne jamais compenser un problème de niveau audio avec un gain arbitraire en début de chaîne — laisser une étape de normalisation dédiée gérer le niveau final, et utiliser un vrai limiteur (pas une simple division par le pic) en sécurité anti-clipping |
| Bruit de fond façon "souffle" sur des fichiers à dynamique faible/nuancée uniquement | Rendu audio en entier 16-bit trop tôt dans le pipeline → bruit de quantification proportionnellement plus audible sur un signal faible | Conserver un format flottant (float) tout au long du pipeline de traitement audio, ne convertir en entier qu'à l'étape d'export final |
| Page blanche sans erreur visible après déploiement d'une SPA en sous-dossier | Chemins absolus générés par l'outil de build (Vite) pointant vers la racine du domaine au lieu du sous-dossier réel | Toujours configurer explicitement le `base path` de l'outil de build quand l'app n'est pas servie depuis la racine du domaine |
| Changement de configuration Nginx sans effet visible | Oubli de `systemctl reload nginx` après modification du fichier de config | Le réflexe `nginx -t && systemctl reload nginx` doit devenir systématique après CHAQUE modification de config Nginx |
| Sliders/éléments qui débordent du cadre sur mobile, dans une grille CSS | `min-width: auto` par défaut sur les éléments de grille/flex, qui empêche un `<input type="range">` de rétrécir sous sa taille intrinsèque | Ajouter explicitement `min-width: 0` sur les conteneurs flex/grid contenant des éléments qui doivent pouvoir rétrécir en dessous de leur taille naturelle |
| Erreur `invalid hostPort` dans `docker-compose.yml` | Faute de frappe (point au lieu de deux-points) dans la syntaxe `IP:PORT:PORT` | Toujours vérifier la syntaxe exacte après un copier-coller manuel de fichier de config YAML |

---

## 18. Check-list rapide pour un nouveau projet similaire

Résumé actionnable, dans l'ordre, pour redémarrer un projet du même type de zéro :

1. [ ] Définir la stack (backend Python/FastAPI si calcul serveur, Vue si interactivité complexe côté client, HTML/CSS pur si simple page vitrine)
2. [ ] `git init` + structure de dossiers (`backend/`, `frontend/`, `landing/` selon besoin) + `.gitignore` dès le départ
3. [ ] Créer le repo distant (GitHub), pousser tôt et souvent
4. [ ] Backend : venv, FastAPI minimal avec `/health`, CORS configuré, structure `routers/services/models`
5. [ ] Frontend : Vite + Vue si besoin, design tokens CSS posés dès le départ, `useApi.ts` centralisé
6. [ ] Développer itérativement : un endpoint → testé isolément → branché au frontend → composant testé, avant de passer au suivant
7. [ ] Avant toute mise en ligne : rate-limiting, limite de taille de fichier, timeout sur les traitements longs
8. [ ] Landing SEO en HTML/CSS pur si besoin d'acquisition organique : title/description/canonical/OG/FAQ structurée
9. [ ] Rendre la config production-ready : variables d'environnement (frontend via Vite `.env.*`, backend via `python-dotenv`)
10. [ ] Dockeriser le backend si dépendances système non-Python
11. [ ] VPS : Docker + Nginx + pare-feu, tester via IP avant même d'acheter un domaine
12. [ ] Nginx comme routeur (statique + proxy API), toujours `nginx -t && systemctl reload nginx` après modif
13. [ ] Domaine + DNS + Certbot HTTPS une fois l'IP validée
14. [ ] Workflow de mise à jour clair et documenté (même s'il reste manuel)
15. [ ] Google Search Console + sitemap pour accélérer l'indexation
16. [ ] Analytics minimal (Cloudflare Web Analytics, sans cookie)
17. [ ] Revenir sur la check-list sécurité dès que le trafic ou les enjeux grossissent
