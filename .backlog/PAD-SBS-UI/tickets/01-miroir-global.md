# BL-130 — Le miroir global et sa bascule

Status: ✅ done
Type: feat
Files: `frontend/index.html`, `docs/user-guide.*.md`

## Problem

Le socle du lot : afficher l'application entière deux fois, une par œil, et
pouvoir l'allumer et l'éteindre.

## What to build

### Le miroir

**Un observateur de mutations plutôt qu'un appel à chaque rendu.** BL-127 recopiait
trois boîtes depuis leurs trois fonctions de rendu, ce qui était tenable parce
qu'on connaissait les trois. À l'échelle de l'application, la liste se filtre, se
trie et se rafraîchit toute seule pendant un téléchargement : demander de déclarer
chaque point de rendu garantit qu'on en oubliera un, et **un miroir figé sur un
état périmé est pire que pas de miroir** — on croit lire l'écran et on lit le
passé.

- Le conteneur de l'application est dupliqué dans un miroir **décoratif** :
  `aria-hidden`, `inert`, sans événements de pointeur, et **sans identifiants**
  (des `id` dupliqués masqueraient les originaux pour `getElementById` — c'est le
  piège déjà rencontré en BL-127).
- Les deux copies sont côte à côte, chacune occupant une moitié. `space-around`
  sur exactement deux enfants place leurs centres sur 25 % et 75 % sans calcul.
- **Mesurer le coût avant de le considérer acquis.** Recopier tout le DOM à
  chaque mutation peut coûter cher sur une liste de plusieurs milliers d'entrées ;
  regrouper les mutations d'une même image est probablement nécessaire. Relever
  le temps par recopie sur un gros dossier réel, pas sur trois fichiers de test.

### La bascule

- **Atteignable au clavier et à la manette**, et **sans souris** : c'est une
  machine sans souris qui en a besoin.
- **Réversible même quand l'écran est illisible** — allumer le mode par erreur sur
  un écran normal ne doit pas piéger l'utilisateur. Le même geste l'éteint.
- **Rangé dans `localStorage`**, pas côté serveur : voir le PRD. Le Deck en a
  besoin, l'iPad non, et l'écran de code PIN s'affiche avant que les réglages
  soient chargés.
- **Il apparaît aussi dans les réglages**, pour qu'il soit trouvable par quelqu'un
  qui ignore le raccourci.

## Acceptance criteria

- [x] Le mode allumé, le navigateur de fichiers est lisible dans chaque œil
- [x] La liste reste à jour dans le miroir quand elle change sans action de
      l'utilisateur — tri, filtre, rafraîchissement pendant un téléchargement
- [x] La bascule s'atteint au clavier **et** à la manette, sans souris
- [x] Le même geste éteint le mode
- [x] Le mode survit à un rechargement de la page
- [x] Le mode **ne suit pas** sur un autre appareil
- [x] Le mode éteint, rien ne change : aucun miroir dans le DOM, aucune mesure
      différente d'aujourd'hui
- [x] Le coût d'une recopie est **mesuré** sur un dossier réel, pas estimé

## Ce qu'il ne faut pas rater

**Le drapeau de PAD-VR existe déjà** (`body.vr-sbs-active`, posé pendant une
lecture côte à côte) et les trois éléments que BL-127 duplique s'en servent. Les
deux mécanismes vont se rencontrer : si le mode global est allumé **et** qu'une
lecture côte à côte commence, il ne faut pas dupliquer deux fois. Décider lequel
prime, et le dire.

**L'écran de code PIN est le premier écran** et il s'affiche avant tout le reste.
Si le miroir n'est pas en place à ce moment-là, le mode ne sert à rien : on ne
peut pas entrer son code.

**Ne pas dupliquer les effets de bord.** Un miroir qui recopie du HTML recopie
aussi des `<img>` et des `<iframe>` : autant de requêtes réseau en double. Vérifier
ce que ça coûte sur une liste de vignettes.
