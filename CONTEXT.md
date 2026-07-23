# CONTEXT.md — État actuel du projet Notewave

> Ce document décrit l'état **actuel et précis** du projet, pas son historique de construction (voir `README.md` pour la méthode générale suivie). Il est destiné à être lu en entier au début d'une nouvelle conversation pour repartir avec tout le contexte nécessaire, sans redécouverte ni suppositions incorrectes.

---

## 1. Résumé du projet

**Notewave** est une application web gratuite qui convertit des fichiers MIDI en MP3 avec un son de piano naturel, des effets de studio configurables (reverb, filtres, compression) et une normalisation de volume adaptée aux plateformes de streaming (Spotify, YouTube, Instagram).

- **Landing page (SEO)** : https://notewaveapp.com
- **Outil de conversion** : https://notewaveapp.com/app
- **Cible utilisateur** : pianistes qui créent des MIDI et veulent les uploader sur Instagram/YouTube/Spotify, ou toute personne partant d'un MIDI trouvé en ligne voulant un rendu naturel, sans connaissance technique requise.
- **Modèle actuel** : 100% gratuit, illimité (sauf garde-fous techniques : 10 conversions/jour/IP, 4 Mo max par fichier MIDI), sans compte, sans base de données.
- **Traitement audio 100% stateless** : aucun fichier utilisateur n'est stocké durablement, tout passe par des dossiers temporaires supprimés automatiquement après chaque requête.

---

## 2. Arborescence complète du repo local

```
midi-to-mp3/                              (nom du repo GitHub : barnabe-hache/midi-to-mp3)
├── .gitignore
├── README.md                              ← guide méthodologique général (process de A à Z)
├── CONTEXT.md                              ← ce fichier
├── docker-compose.yml
│
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env                                ← PAS commité (voir section 6)
│   ├── .env.example                         ← commité, modèle documenté
│   ├── requirements.txt
│   ├── generate_demo_midi.py                ← script one-shot ayant généré app/assets/demo_scale.mid
│   ├── venv/                                 ← ignoré par git
│   │
│   ├── soundfonts/                            ← fichiers .sf2 / .SF2 des pianos disponibles (assets versionnés)
│   │   └── (plusieurs fichiers .sf2 et .SF2 déposés par l'utilisateur)
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py                            ← point d'entrée FastAPI, CORS, rate limiter, routers
│       ├── limiter.py                          ← instance slowapi Limiter (fichier séparé pour éviter import circulaire)
│       │
│       ├── assets/
│       │   └── demo_scale.mid                  ← gamme de démo (do majeur) utilisée par /preview
│       │
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── soundfonts.py                    ← GET /soundfonts
│       │   ├── convert.py                        ← POST /convert (endpoint principal, rate-limited)
│       │   └── preview.py                         ← POST /preview (écoute piano seul, ou piano+effets)
│       │   (render.py a été supprimé lors du nettoyage — n'existe plus)
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── midi_render.py                     ← rendu MIDI+SF2 → WAV via binaire fluidsynth
│       │   ├── effects.py                          ← Pedalboard : Compressor, Reverb, HighpassFilter, LowpassFilter
│       │   ├── normalize.py                         ← pyloudnorm (LUFS) + Pedalboard Limiter anti-clipping
│       │   └── export.py                             ← pydub : WAV → MP3 320kbps
│       │
│       └── models/
│           ├── __init__.py
│           └── schemas.py                           ← EffectsParams (Pydantic), SoundfontInfo, SoundfontListResponse
│
├── frontend/
│   ├── index.html                              ← title "Notewave — MIDI to MP3", favicon = logo.svg
│   ├── package.json
│   ├── vite.config.ts                            ← contient `base: '/app/'` (essentiel, voir section 8)
│   ├── tsconfig.json
│   ├── .env.development                           ← VITE_API_BASE_URL=http://localhost:8000
│   ├── .env.production                             ← VITE_API_BASE_URL=/api
│   ├── node_modules/                                ← ignoré par git
│   ├── dist/                                         ← généré par npm run build, ignoré par git
│   │
│   └── src/
│       ├── main.ts
│       ├── App.vue                                  ← composant racine, orchestre tout l'état de l'outil
│       ├── style.css                                 ← design tokens + blobs de fond
│       │
│       ├── assets/
│       │   └── logo.svg                              ← logo Notewave (identique à landing/assets/logo.svg)
│       │
│       ├── components/
│       │   ├── AppHeader.vue                          ← header sticky flouté avec logo + nom
│       │   ├── MidiDropzone.vue                         ← drag & drop / sélection fichier .mid
│       │   ├── PianoSelector.vue                          ← liste soundfonts + upload custom .sf2 + "Play sample"
│       │   ├── EffectsPanel.vue                             ← sliders reverb/damping/wet/dry/compression + filtres
│       │   ├── InfoTooltip.vue                                ← bulle d'aide au survol (icône "?")
│       │   ├── ConversionProgress.vue                           ← barre de progression upload + traitement
│       │   └── ResultPlayer.vue                                  ← lecteur audio résultat + bouton téléchargement
│       │
│       ├── composables/
│       │   └── useApi.ts                                          ← TOUS les appels HTTP au backend, centralisés
│       │
│       └── types/
│           └── index.ts                                            ← Soundfont, EffectsParams, DEFAULT_EFFECTS_PARAMS,
│                                                                        ConversionStatus, SelectedPiano
│
└── landing/
    ├── index.html                                    ← page unique, SEO complet (voir section 9)
    ├── style.css
    ├── robots.txt
    ├── sitemap.xml
    │
    └── assets/
        ├── logo.svg                                    ← identique à frontend/src/assets/logo.svg
        ├── demo.mid                                      ← fichier MIDI d'exemple pour la comparaison
        ├── demo-ourtool.mp3                                ← même MIDI converti avec Notewave
        ├── demo-basictool.mp3                                ← même MIDI converti avec un outil basique concurrent
        ├── Spotify_logo.svg
        ├── Youtube_logo.svg
        ├── Instagram_logo.svg
        └── og-image.png                                        ← ⚠️ RÉFÉRENCÉ dans le HTML mais jamais créé/confirmé
                                                                     (voir section 12, point ouvert)
```

---

## 3. Arborescence sur le VPS (différences avec le repo local)

Serveur : **VPS Hostinger, Ubuntu**, IP publique (voir config Nginx/DNS pour la valeur exacte actuelle).

```
/root/midi-to-mp3/                    ← clone git du repo (structure identique au repo local ci-dessus)
├── backend/.env                       ← créé MANUELLEMENT sur le serveur, jamais via git (voir section 6)
└── frontend/dist/                      ← généré sur le serveur via `npm run build`, jamais commité

/var/www/midi-to-mp3/                 ← fichiers statiques réellement servis par Nginx
├── landing/                            ← copie de ~/midi-to-mp3/landing/*
└── app/                                 ← copie de ~/midi-to-mp3/frontend/dist/*

/etc/nginx/sites-available/midi-to-mp3   ← fichier de config Nginx (voir contenu exact section 7)
/etc/nginx/sites-enabled/midi-to-mp3     → symlink vers le fichier ci-dessus
                                            (le fichier "default" a été supprimé de sites-enabled)

/etc/letsencrypt/...                   ← certificats HTTPS gérés automatiquement par Certbot
                                          (renouvellement auto via systemd timer `certbot.timer`)
```

**Important** : le nom du repo GitHub et du dossier cloné est `midi-to-mp3` (PAS `notewave`) — le nom de marque "Notewave" n'a été choisi qu'après la création initiale du repo. Tous les chemins sur le VPS (`/var/www/midi-to-mp3/...`, le fichier Nginx `sites-available/midi-to-mp3`) utilisent ce nom technique `midi-to-mp3`, à ne pas confondre avec le nom de marque affiché aux utilisateurs ("Notewave") ni avec le nom de domaine (`notewaveapp.com`).

---

## 4. Backend — détail de l'architecture et du pipeline

### Endpoints exposés (préfixe `/api/` ajouté par Nginx en production, absent en dev local)

| Méthode | Route | Rôle | Rate limit |
|---|---|---|---|
| GET | `/health` | Vérification simple que le serveur tourne | Non |
| GET | `/soundfonts` | Liste les pianos disponibles (fichiers `.sf2`/`.SF2` dans `backend/soundfonts/`) | Non |
| POST | `/preview` | Rend la gamme de démo (`demo_scale.mid`) avec un soundfont donné, effets optionnels | Non |
| POST | `/convert` | Pipeline complet : MIDI utilisateur → MP3 final | **Oui : 10/day par IP** |

### Pipeline de traitement (`/convert`, fonction `_run_pipeline` dans `convert.py`)

1. **Validation** : extension `.mid`/`.midi`, taille ≤ 4 Mo, parsing JSON des `effects_params`
2. **Résolution du soundfont** : soit `soundfont_id` (fichier prédéfini dans `backend/soundfonts/`), soit `custom_soundfont` uploadé (prioritaire si les deux sont fournis)
3. **Rendu MIDI→WAV** (`services/midi_render.py`) via le binaire `fluidsynth` en sous-processus :
   ```
   fluidsynth -ni -F output.wav -r 44100 -o audio.file.format=float -g 1.0 soundfont.sf2 input.mid
   ```
   — **`float` (pas s16)** pour éviter le bruit de quantification sur les fichiers à dynamique faible/nuancée (MIDI joués sur un vrai clavier)
   — **`-g 1.0`** (gain neutre) — le niveau final est entièrement géré par l'étape de normalisation, pas ici
   — **Ordre des arguments important** : toutes les options (`-F`, `-r`, `-o`, `-g`) doivent précéder les fichiers positionnels (soundfont, midi)
4. **Effets** (`services/effects.py`, via Pedalboard) — ordre de la chaîne :
   - `Compressor` (si `compression_amount > 0`) — `threshold_db = -10 - 30*compression_amount`, `ratio = 1 + 3*compression_amount`
   - `Reverb(room_size, damping, wet_level, dry_level)`
   - `HighpassFilter(cutoff_frequency_hz)` (si activé)
   - `LowpassFilter(cutoff_frequency_hz)` (si activé)
5. **Normalisation** (`services/normalize.py`) :
   - `pyloudnorm` : normalise à la loudness intégrée cible (`target_lufs`, défaut -14.0)
   - Puis `Pedalboard Limiter(threshold_db=-1.0, release_ms=100)` en sécurité anti-clipping (remplace une ancienne méthode par simple division par le pic, qui causait un son écrasé/dur sur les transitoires)
6. **Export MP3** (`services/export.py`, via pydub) : 320 kbps
7. Le tout s'exécute dans `asyncio.wait_for(asyncio.to_thread(...), timeout=90.0)` — timeout de 90s, exécuté dans un thread séparé car le pipeline est du code synchrone/bloquant

### `EffectsParams` (schéma Pydantic, `models/schemas.py`) — bornes de validation

| Champ | Défaut | Min | Max |
|---|---|---|---|
| `room_size` | 0.3 | 0.0 | 1.0 |
| `damping` | 0.5 | 0.0 | 1.0 |
| `wet_level` | 0.15 | 0.0 | 1.0 |
| `dry_level` | 0.85 | 0.0 | 1.0 |
| `highpass_freq` | null | 20.0 | 2000.0 |
| `lowpass_freq` | null | 1000.0 | 20000.0 |
| `compression_amount` | 0.2 | 0.0 | 1.0 |
| `target_lufs` | -14.0 | -30.0 | -6.0 |

Ces mêmes valeurs par défaut sont dupliquées côté frontend dans `frontend/src/types/index.ts` (`DEFAULT_EFFECTS_PARAMS`) — **à garder synchronisées si modifiées**.

### Robustesse déjà en place

- Rate limiting : `slowapi`, clé = IP (`get_remote_address`), `10/day` sur `/convert` uniquement
- Réponse 429 personnalisée en cas de dépassement (message clair côté frontend)
- Taille MIDI max : 4 Mo, vérifiée avant tout traitement
- Timeout de traitement : 90 secondes
- Tous les endpoints ont un `try/except` avec `traceback.print_exc()` pour un debug exploitable via `docker compose logs`
- Fichiers temporaires via `tempfile.TemporaryDirectory()` — suppression garantie après chaque requête, aucune persistance de fichier utilisateur

### `backend/soundfonts/` — gestion de la casse de fichiers

Le listing (`routers/soundfonts.py`) compare `f.suffix.lower() == ".sf2"` explicitement plutôt que d'utiliser `glob("*.sf2")`, car ce dernier est sensible à la casse sous Linux (le VPS) mais pas sous Windows (poste de dev) — sans ce correctif, les fichiers `.SF2` (majuscules) étaient invisibles en production alors qu'ils apparaissaient en dev local.

L'`id` d'un soundfont retourné par `/soundfonts` correspond exactement à `f.stem` (nom de fichier sans extension, casse d'origine préservée) — c'est ce même `id` qui est renvoyé au serveur dans `/convert` et `/preview` pour retrouver le bon fichier physique.

---

## 5. Frontend (outil `/app`) — état de l'interface et des interactions

### Flux utilisateur complet (dans `App.vue`)

1. Dropzone MIDI (`MidiDropzone.vue`) → émet `file-selected`
2. Sélection piano (`PianoSelector.vue`) → liste chargée depuis `/soundfonts` au montage, bouton "Play sample" par piano (appelle `/preview` sans effets), upload `.sf2` custom possible → émet `piano-selected`
3. Panneau d'effets (`EffectsPanel.vue`) → sliders + champs numériques synchronisés (min/max clampés automatiquement), toggles pour activer/désactiver les filtres passe-haut/passe-bas → émet `params-changed` en continu (watch avec `immediate: true`)
4. Bouton **"Play sample with these effects"** → appelle `/preview` avec le piano sélectionné ET les effets actuels (permet d'entendre le rendu final avant de lancer la vraie conversion)
5. Bouton **"Convert to MP3"** (désactivé tant que fichier + piano ne sont pas sélectionnés) → `convertMidiToMp3()` dans `useApi.ts`, utilise `XMLHttpRequest` (pas `fetch`) pour pouvoir suivre la progression d'upload via `xhr.upload.onprogress`
6. `ConversionProgress.vue` affiche deux phases : `uploading` (pourcentage réel) puis `processing` (barre indéterminée animée, car pas de suivi de progression granulaire possible côté serveur pour cette partie)
7. `ResultPlayer.vue` : lecteur audio + bouton téléchargement. Le nom de fichier téléchargé est calculé dans `App.vue` (`buildDownloadFilename`) : `{nom_original_sans_extension}_notewave.mp3`

### `useApi.ts` — fonctions exposées

- `checkBackendHealth()` — non utilisé activement dans l'UI actuelle (existait pour un ancien indicateur de connexion, potentiellement obsolète)
- `fetchSoundfonts()`
- `previewSoundfont({ soundfontId?, customFile?, effectsParams? })` — `effectsParams` optionnel (absent = juste le piano seul, présent = piano + effets)
- `convertMidiToMp3({ midiFile, soundfontId?, customSoundfont?, effectsParams, onUploadProgress })`

`API_BASE_URL` = `import.meta.env.VITE_API_BASE_URL` (voir section 8 pour les valeurs dev/prod).

### Responsive — état actuel

`EffectsPanel.vue` utilise une mise en page **flexbox** (pas grid) pour les lignes de sliders : libellé à largeur fixe (`flex: 0 0 150px`), slider qui prend l'espace restant (`flex: 1; min-width: 0`), valeur numérique compacte à largeur fixe (`flex: 0 0 56px` ou `68px` pour les Hz). En dessous de `640px`, bascule en colonne (libellé pleine largeur en haut, slider + valeur juste en dessous). Le `min-width: 0` est essentiel — sans lui, les `<input type="range">` dans un conteneur flex/grid refusent de rétrécir sous leur taille intrinsèque et débordent du cadre.

---

## 6. Variables d'environnement — état exact actuel

### `backend/.env` (sur le VPS, PAS dans git)

```
CORS_ORIGINS=https://notewaveapp.com,https://www.notewaveapp.com
```

### `backend/.env` (en local, sur le poste de dev)

```
CORS_ORIGINS=http://localhost:5173
```

### `backend/.env.example` (commité, modèle)

```
CORS_ORIGINS=http://localhost:5173
```

### `frontend/.env.development` (commité)

```
VITE_API_BASE_URL=http://localhost:8000
```

### `frontend/.env.production` (commité)

```
VITE_API_BASE_URL=/api
```

Chargement backend : `python-dotenv`, `load_dotenv()` appelé en haut de `main.py`, lu via `os.getenv("CORS_ORIGINS", ...).split(",")`.

---

## 7. Configuration Nginx actuelle (VPS)

Fichier : `/etc/nginx/sites-available/midi-to-mp3` (symlinké dans `sites-enabled/`).

Après passage de Certbot, la structure exacte du fichier a été **automatiquement modifiée par Certbot** (ajout des directives `listen 443 ssl`, chemins des certificats, redirection HTTP→HTTPS). La version de référence **avant** le passage de Certbot était :

```nginx
server {
    listen 80;
    server_name notewaveapp.com www.notewaveapp.com;

    location / {
        root /var/www/midi-to-mp3/landing;
        index index.html;
        try_files $uri $uri/ =404;
    }

    location /app {
        alias /var/www/midi-to-mp3/app;
        index index.html;
        try_files $uri $uri/ /app/index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Certbot a ensuite ajouté automatiquement le bloc HTTPS (port 443, certificats Let's Encrypt) et la redirection HTTP→HTTPS. **Le contenu exact et actuel du fichier sur le VPS fait foi** en cas de doute — cette version ci-dessus est la base fonctionnelle avant modification automatique par Certbot.

Points clés à ne pas casser si ce fichier est modifié à l'avenir :
- `location /api/` avec le `/` final dans `proxy_pass http://127.0.0.1:8000/;` — c'est ce qui retire le préfixe `/api` avant transmission au backend
- `location /app` avec `try_files $uri $uri/ /app/index.html;` — nécessaire pour que l'app Vue (single-page) fonctionne même en cas de rafraîchissement de page sur une sous-route

---

## 8. Docker — configuration actuelle

`docker-compose.yml` (racine du repo) :

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "127.0.0.1:8000:8000"
    env_file:
      - ./backend/.env
    restart: unless-stopped
```

`backend/Dockerfile` :

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    fluidsynth \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`frontend/vite.config.ts` contient impérativement `base: '/app/'` — sans cette ligne, l'app buildée génère des chemins de assets absolus depuis la racine du domaine et ne charge pas du tout (page blanche silencieuse) quand servie depuis `/app`.

---

## 9. Landing page — contenu et structure actuels

Une seule page (`landing/index.html`), sections dans cet ordre exact :

1. **Header sticky flouté** (logo + "Notewave" + bouton "Try it now" → lien `/app`)
2. **Hero** : badge "🎹 No signup · Unlimited · Free", H1 "Convert MIDI to MP3 with a natural piano sound", CTA "Try it now"
3. **"Hear the difference"** : deux lecteurs audio côte à côte (basic converter vs Notewave), utilise `landing/assets/demo-*.mp3`
4. **"How to convert a MIDI file to MP3"** (3 étapes numérotées) — positionnée juste après la section précédente (déplacée ici sur demande explicite)
5. **"Ready for your favorite platforms"** : logos Spotify/YouTube/Instagram (grayscale → couleur au survol), texte sur la normalisation loudness
6. **"Why Notewave"** : liste éditoriale numérotée (01-04) avec liseré, PAS de cartes à icônes (changé exprès pour éviter un rendu jugé trop générique/"IA")
7. **FAQ** (5 questions) — présente à la fois en HTML visible et en JSON-LD structuré (`schema.org/FAQPage`) pour le SEO
8. **CTA final** : carte neutre (pas de fond dégradé plein, volontairement discret suite à un retour utilisateur), bouton "Try it now"
9. **Footer**

### SEO déjà en place dans le `<head>`

- `<title>` : "Notewave — Free MIDI to MP3 Converter with Natural Piano Sound"
- `<meta name="description">`
- `<link rel="canonical" href="https://notewaveapp.com/" />`
- Open Graph (`og:type`, `og:url`, `og:title`, `og:description`, `og:image`)
- Twitter Card (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`)
- JSON-LD `SoftwareApplication` (prix 0, applicationCategory MultimediaApplication)
- JSON-LD `FAQPage` (les 5 mêmes questions que la section HTML visible)

`landing/robots.txt` et `landing/sitemap.xml` existent et référencent `https://notewaveapp.com/`.

**Statut d'indexation confirmé** : le site est indexé par Google (vérifié via Google Search Console, propriété vérifiée par enregistrement DNS TXT chez le registrar), et apparaît déjà sur des recherches avec mots-clés précis liés au nom "Notewave".

---

## 10. Identité visuelle — design tokens de référence

Palette (variables CSS, dupliquées à l'identique dans `landing/style.css` ET `frontend/src/style.css` — **à garder synchronisées si modifiées**) :

```css
--color-bg: #F5F5F3;
--color-surface: #FFFFFF;
--color-ink: #16181D;
--color-ink-muted: #5B6169;
--color-border: #E2E4E8;
--color-signal: #2F6F5E;
--color-signal-light: #4FA98A;
--color-signal-soft: #E8F0EE;
--color-gold: #E8B94A;
--color-gold-soft: #FBF1DC;
--color-alert: #B5493B;
--color-alert-soft: #F7E9E7;
--gradient-signal: linear-gradient(135deg, var(--color-signal), var(--color-signal-light));
--font-display: 'Space Grotesk', sans-serif;
--font-body: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;
--radius-sm: 8px;
--radius-md: 14px;
--radius-lg: 20px;
```

Polices chargées via Google Fonts (`@import` en haut de chaque `style.css`) : Space Grotesk (titres), Inter (corps), JetBrains Mono (valeurs numériques des paramètres, façon "instrument de mesure").

**Nom** : Notewave (validé, ne pas reproposer d'alternatives sans raison).

**Logo** : SVG en dégradé vert (`--color-signal` → `--color-signal-light`) représentant une croche dont la hampe se prolonge en deux courbes façon onde sonore. Fichier identique dans `landing/assets/logo.svg` et `frontend/src/assets/logo.svg`. Contenu SVG exact :

```svg
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="nwGrad" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#2F6F5E"/>
      <stop offset="1" stop-color="#4FA98A"/>
    </linearGradient>
  </defs>
  <ellipse cx="16" cy="34" rx="7" ry="5.5" transform="rotate(-18 16 34)" fill="url(#nwGrad)"/>
  <rect x="21" y="10" width="3" height="26" rx="1.5" fill="url(#nwGrad)"/>
  <path d="M24 10 C30 8, 30 16, 24 18" stroke="url(#nwGrad)" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M24 16 C34 12, 34 24, 22 24" stroke="url(#nwGrad)" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.6"/>
</svg>
```

Motifs de design établis à respecter pour toute nouvelle UI :
- Header sticky avec `backdrop-filter: blur(14px) saturate(160%)` et fond semi-transparent
- Formes décoratives en arrière-plan (`.bg-blob`) : cercles flous en dégradé, `position: fixed`, `z-index: -1`, `pointer-events: none`, opacité 0.2-0.35
- Micro-interactions systématiques au survol (légère élévation + ombre sur cartes/boutons)
- Listes éditoriales numérotées (liseré + index en `font-mono`) plutôt que des grilles de cartes à icônes pour présenter des features

---

## 11. Analytics et monitoring actuels

- **Cloudflare Web Analytics** : script inséré avant `</body>` sur `landing/index.html` (et potentiellement `frontend/index.html`, à vérifier selon ce qui a été réellement fait). Sans cookie, aucun bandeau RGPD nécessaire.
- **Comptage de conversions** : un `print(f"CONVERSION_SUCCESS filename={...}")` a été ajouté dans `convert.py` juste avant le retour de la réponse finale, consultable via `docker compose logs backend | grep -c "CONVERSION_SUCCESS"`. Mesure les conversions réussies, PAS les téléchargements effectifs (impossible à tracker sans complexité additionnelle, le clic sur "Download" est purement côté client).
- Pas de vraie base de données de monitoring — volontairement minimal, cohérent avec la philosophie "pas de complexité avant qu'elle soit nécessaire".

---

## 12. Points ouverts / non résolus (à traiter consciemment, pas par défaut)

- **`landing/assets/og-image.png`** est référencé dans les balises Open Graph/Twitter Card mais il n'est pas confirmé que ce fichier existe réellement (1200×630px attendu). À vérifier avant de considérer le partage sur réseaux sociaux comme pleinement fonctionnel.
- **Sécurité VPS non renforcée** (décision consciente de l'utilisateur, reportée) : pas de restriction SSH par clé uniquement, pas de Fail2ban, pas de `unattended-upgrades`, pas de limites de ressources sur le conteneur Docker, `server_tokens` de Nginx non désactivé. Voir README.md section 16 pour le détail.
- **`checkBackendHealth()`** dans `useApi.ts` semble ne plus être utilisé activement dans l'UI actuelle (vestige d'un ancien indicateur de connexion affiché en tout début de projet) — à vérifier/nettoyer si on retouche ce fichier.
- **Pas de sitemap dynamique** — le `sitemap.xml` est statique et ne référence qu'une seule URL ; à étoffer si de nouvelles pages sont ajoutées.

---

## 13. Roadmap prévue (ne PAS construire par anticipation, juste être conscient de la direction)

Dans cet ordre de dépendance logique :

1. **Support multi-instruments** dans les MIDI (actuellement : rendu piano seul uniquement, un seul programme MIDI/preset sélectionné par soundfont) — évolution purement backend/traitement audio, n'impose pas de base de données.
2. **Système de crédits gratuits + achat de crédits** — impose l'introduction d'une **vraie base de données** (au minimum : utilisateur, crédits restants, historique d'achats). Le pipeline de traitement audio doit rester stateless (pas de stockage de fichiers), seule la couche "comptes/crédits" introduit un état persistant.
3. **Authentification (compte Google ou équivalent)** — n'a de sens qu'une fois le système de crédits en place (pas besoin de compte tant que tout est gratuit/illimité). Le bouton "Try it now" actuel est explicitement conçu pour devenir un bouton "Connect" à ce moment-là.
4. **Rate-limiting par utilisateur authentifié** plutôt que par IP — remplacera `get_remote_address` dans `limiter.py` par une fonction basée sur l'identité de l'utilisateur connecté.
5. **Paiement** : Stripe pressenti (Checkout + webhooks) pour gérer l'achat de crédits, non implémenté à ce stade.

Architecture pensée pour absorber cette évolution sans réécriture majeure : ajout d'un nouveau service `db` dans `docker-compose.yml` le moment venu, le backend FastAPI s'y connecte, le reste de la structure (routers/services/models, Nginx, Docker du backend) reste inchangé dans son principe.

---

## 14. Ce dont une nouvelle conversation a besoin pour être immédiatement productive

En résumé, pour toute nouvelle fonctionnalité ou modification demandée :
- Le style/design doit respecter les tokens de la section 10 — ne pas en proposer de nouveaux sans raison explicite
- Toute nouvelle route backend doit suivre le pattern `routers/` + `services/` déjà en place, avec gestion d'erreur `try/except` + `traceback.print_exc()`
- Toute nouvelle donnée persistante nécessite d'introduire une base de données — actuellement absente, à ne faire que si réellement nécessaire à la fonctionnalité demandée
- Le déploiement reste **manuel** (pas de CI/CD) — toute nouvelle fonctionnalité livrée doit être accompagnée des commandes exactes à exécuter sur le VPS (`git pull` + rebuild ciblé selon ce qui a changé, voir section 13 du README.md pour le détail exact des commandes)
- Les fichiers `.env` (backend) ne sont jamais à modifier via git — toujours préciser explicitement s'il faut une modification manuelle sur le VPS
- Le nom technique du repo/dossier est `midi-to-mp3`, le nom de marque affiché est `Notewave`, le domaine est `notewaveapp.com` — ne pas mélanger ces trois éléments dans les instructions données
