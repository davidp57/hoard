# Hoard — Guide utilisateur

## Présentation

Hoard est un navigateur de fichiers vidéo accessible depuis un navigateur web. Il est conçu pour parcourir un disque réseau (NAS), lire des vidéos directement dans le navigateur et se souvenir de là où tu t'es arrêté.

---

## Interface principale

L'interface est divisée en deux zones :

- **À gauche (ou en plein écran sur mobile) :** le navigateur de fichiers
- **À droite (ou en overlay plein écran sur mobile) :** le player vidéo

### Navigateur de fichiers

Le navigateur affiche le contenu d'un dossier. Un **fil d'Ariane** en haut permet de remonter dans l'arborescence. Le bouton **🏠** ramène à la racine.

Chaque fichier ou dossier est affiché avec :

- Son nom
- Une **icône d'état** de lecture (pour les fichiers vidéo) :
  - Fond neutre → **non vu**
  - Fond jaune + barre de progression + pourcentage → **en cours**
  - Fond vert → **vu** (≥ 90 % regardé)

### Actions sur un fichier

En passant sur un fichier (ou en appuyant longuement sur mobile), des boutons d'action apparaissent :

| Action | Description |
|--------|-------------|
| **▶ Lire** | Ouvre la vidéo dans le player |
| **📁 Déplacer** | Ouvre le modal de déplacement rapide (dossiers épinglés) |
| **🗑 Supprimer** | Supprime le fichier après confirmation |

---

## Player vidéo

### Contrôles

| Élément | Rôle |
|---------|------|
| **Barre de progression** | Indique et contrôle la position dans la vidéo |
| **⏮ / ⏭** | Recule / avance de 30 secondes |
| **◀◀ / ▶▶** | Recule / avance de 10 secondes |
| **▶ / ⏸** | Lecture / Pause |
| **🔊** | Muet/son |
| **Volume** | Curseur de volume |
| **⛶** | Plein écran |

### Reprise automatique

La position est sauvegardée automatiquement toutes les 5 secondes. Lorsque tu ouvres à nouveau un fichier, la lecture reprend là où tu t'es arrêté.

### Marqueurs IN/OUT (découpe)

Des boutons `[IN` et `OUT]` permettent de définir une zone de lecture restreinte (sans modifier le fichier). Le bouton ✂ lance une découpe physique du fichier via ffmpeg.

---

## Gestes tactiles

Les gestes fonctionnent directement sur l'image vidéo.

### Tap simple

| Zone | Action |
|------|--------|
| Centre (haut) | Lecture / Pause |
| Centre (bas, dernière rangée) | Afficher / masquer les contrôles |

### Double-tap

| Zone | Action |
|------|--------|
| Bord gauche (< 20 % de largeur) | Reculer de 30 s |
| Bord droit — tiers bas | Avancer de 30 s |
| Bord droit — tiers médian | Avancer de 60 s |
| Bord droit — tiers haut | Avancer de 90 s |
| Centre | Plein écran |

### Triple-tap

Toggle entre les modes d'affichage **Fit** (image entière visible) et **Fill** (image recadrée).

### Swipe horizontal

Seek progressif dans la vidéo. La **vitesse dépend de la hauteur du doigt** : un swipe en haut de l'écran est plus rapide qu'en bas.

### Swipe vertical

| Zone horizontale | Action |
|-----------------|--------|
| Bord gauche (< 20 %) | Luminosité de l'image |
| Bord droit (> 80 %) | Volume |

---

## Raccourcis clavier

| Touche | Action |
|--------|--------|
| `Espace` | Lecture / Pause |
| `←` | Reculer de 10 s |
| `→` | Avancer de 10 s |
| `↑` | Volume + 10 % |
| `↓` | Volume − 10 % |
| `F` | Plein écran |
| `M` | Muet |

---

## Dossiers rapides (épingles)

Les **dossiers rapides** permettent de déplacer un fichier vers un dossier fréquemment utilisé en deux taps.

- Clique sur l'icône 📌 à côté d'un dossier pour l'épingler / le désépingler.
- Les dossiers épinglés apparaissent dans le modal de déplacement.

---

## Téléchargement de vidéos

Hoard peut télécharger des vidéos depuis le web via **yt-dlp** et les sauvegarder directement sur le NAS.

### Installer la bookmarklet

1. Ouvre les **Paramètres** (bouton ⚙️ dans l'en-tête).
2. Descends jusqu'à la section **Téléchargements**.
3. **Glisse** le lien « 📥 Télécharger avec Hoard » vers ta barre de favoris.

### Télécharger une vidéo

**Depuis n'importe quelle page web** — clique sur la bookmarklet. Hoard s'ouvre dans un nouvel onglet avec l'URL, tes cookies et le titre de la page pré-remplis dans le modal de file de téléchargement. Clique sur **📥 Télécharger** pour lancer.

> **Détection intelligente de la source vidéo** : si un élément `<video>` est en lecture sur la page, la bookmarklet capture son URL source directe au lieu de l'URL de la page. Cela permet de télécharger depuis des sites où yt-dlp n'a pas d'extracteur dédié (Patreon, lecteurs vidéo custom, embeds BunnyCDN, etc.). Le modal affiche un indicateur 🎬 quand une source directe a été détectée. L'URL de la page d'origine est automatiquement envoyée comme en-tête `Referer` pour que les CDN qui vérifient l'origine acceptent la requête.

**Depuis Hoard directement** — clique sur le bouton **📥** dans l'en-tête, colle l'URL et confirme.

**Indication de nom de fichier** : le champ « Nom du fichier » est pré-rempli avec le titre de la page lors de l'utilisation de la bookmarklet. Tu peux le modifier librement avant de lancer le téléchargement. S'il est laissé vide, yt-dlp extrait le titre automatiquement.

### File de téléchargement

Tous les téléchargements sont regroupés dans une file centrale accessible depuis le bouton **📥** dans l'en-tête :

- Un **badge** sur le bouton indique le nombre de téléchargements actifs.
  - Badge jaune = téléchargements en cours.
  - Badge vert = tous terminés (la file contient des éléments à supprimer).
- Clique sur le bouton pour ouvrir le **modal de file de téléchargement**, qui affiche chaque téléchargement avec son nom, sa barre de progression et son statut.
- Clique sur **✕** à côté d'un téléchargement terminé ou en erreur pour le retirer de la file.
- **Les téléchargements continuent même si tu fermes l'onglet** : ils s'exécutent comme des threads en arrière-plan sur le NAS. Quand tu reviens sur Hoard, le widget de file se reconnecte automatiquement aux jobs en cours.

### Paramètres

| Paramètre | Description |
|-----------|-------------|
| **Dossier de téléchargement** | Dossier cible, relatif à `MEDIA_ROOT` (défaut : `Downloads`). Créé automatiquement s'il n'existe pas. |
| **Chemin du fichier cookies** | Chemin absolu vers un fichier `cookies.txt` au format Netscape. Utile pour les sites qui nécessitent une authentification. |

### À propos des cookies

La bookmarklet transmet le `document.cookie` de la page source. Attention : les **cookies HttpOnly ne sont pas accessibles en JavaScript** — pour les sites qui en ont besoin (ex : plateformes de streaming), exporte un fichier `cookies.txt` avec une extension navigateur et renseigne son chemin dans les paramètres.

---

## Disposition responsive

| Écran | Mode |
|-------|------|
| Largeur > 700 px | Vue divisée : liste à gauche, player à droite |
| Largeur ≤ 700 px | Liste plein écran, player en overlay |
