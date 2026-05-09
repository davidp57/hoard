# Changelog utilisateur — Hoard 🐦

Journal des changements visibles par l'utilisateur, sans jargon technique.

---

## [Non publié]

### Nouveautés
- **4 niveaux de seek configurables** : les boutons de saut, les raccourcis clavier, les swipes et les double-taps utilisent désormais quatre durées réglables dans les Paramètres (court, moyen, long, très long — 10 s / 30 s / 60 s / 120 s par défaut).
- **Raccourcis clavier étendus** : Shift+← / → (seek moyen), Ctrl+← / → (seek long), Alt+← / → (seek très long), A (aspect ratio), PageDown / PageUp (vidéo suivante/précédente), I / O (marqueurs IN/OUT), C (découpe), D (déplacement), Suppr (supprimer), S (position initiale du dossier), ? (aide).
- **Confirmation visuelle de chaque seek** : un toast apparaît après chaque saut (bouton, clavier ou swipe) pour indiquer le delta réel.
- **Modaux compatibles plein écran** : les fenêtres Déplacer, Découper, Supprimer et l'aide clavier restent visibles au-dessus du plein écran natif du navigateur.
- **Contrôles plein écran discrets** : le mouvement de la souris ne révèle les contrôles qu'en bas de l'écran (10 %), pour ne pas déranger pendant la lecture.
- **Option désactiver le transcodage** : nouveau réglage dans Paramètres → Player. Quand il est désactivé, Hoard envoie toujours le flux original sans transcodage — utile si votre NAS est lent ou si votre navigateur lit nativement le format.

---

## [v2.0.0] — 2026-04-06

### Nouveautés
- Téléchargement vidéo depuis une URL web (YouTube, etc.) via un bookmarklet ou un champ de saisie direct.
- File d'attente de téléchargements séquentiels avec suivi en temps réel.
- Accès sécurisé en HTTPS natif (configurable via certificat).

---

## [v1.0.0] — 2026-04-05

### Nouveautés
- Navigation dans les dossiers de votre NAS depuis un navigateur web.
- Indicateurs visuels d'état de lecture : non vu, en cours (barre + %), vu.
- Lecteur vidéo intégré avec gestes tactiles, raccourcis clavier et reprise automatique.
- Déplacement de fichiers vers des dossiers prédéfinis.
- Suppression de fichiers avec confirmation.
- Application web installable (PWA) sur iPad et laptop.
