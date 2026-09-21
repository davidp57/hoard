# Lot FIX-XR-DISPLAY — Hoard utilisable sur lunettes XR en 3840×1080

Status: ⬜ ready
Branch: `fix/xr-display` (à créer)

## Problem Statement

Le lot [FEAT-VR180](../FEAT-VR180/PRD.md) est livré et la lecture VR 180° côte à
côte fonctionne. Restait la vérification qui ne pouvait pas se faire depuis un
poste de bureau : un Steam Deck pilotant les lunettes Viture Beast. Elle a été
faite le **2026-09-21**, et elle a trouvé deux défauts d'usage.

Pour obtenir le mode côte à côte sur les Beast, il faut **pousser la sortie à
3840×1080** — un ratio 32:9, soit exactement deux fois un 16:9. C'est cette
résolution qui révèle les deux problèmes, et aucun des deux n'était visible
autrement.

1. **Le ratio de l'image est faux en mode VR** : « les personnages sont trop
   hauts et trop étroits ». Diagnostic par lecture du code, **à confirmer** : le
   réglage par défaut est `half` (image réétirée par l'afficheur), alors que
   3840×1080 est du **full**-SBS — chaque moitié fait déjà 1920×1080 au bon
   ratio et les Beast ne réétirent rien. En `half`, le champ vertical est calculé
   depuis `1080/3840` au lieu de `1080/1920`, ce qui zoome verticalement d'un
   facteur deux.
2. **L'interface est trop petite** à cette résolution, en particulier les deux
   fenêtres pleine page de la manette : le menu contextuel (**Select**) et la
   carte des boutons (**START**). Elles « doivent s'adapter à la taille de
   l'écran ».

## Ce que la mesure dit déjà

**Sur le ratio** (`frontend/index.html:5701`) :

```js
const perceivedW = !sbs ? w : (vr.sbsLayout === 'half' ? w : w / 2);
let th = tanH, tv = tanH * vh / perceivedW;
```

Le réglage existe (`vr_sbs_layout`, défaut `half`), se bascule à la **touche B du
clavier** (`index.html:6997`, seulement si le mode VR est actif) et depuis
**Select → « 🥽 Image côte à côte »** (`index.html:7086`). Le **bouton B de la
manette** ne fait pas ça — c'est « annuler / fermer » partout, y compris en
lecture. La formulation « touche B » du lot précédent est donc inutilisable sur un
Deck sans clavier, ce qui est précisément la machine visée.

**Sur l'interface**, les deux fenêtres n'ont pas le même défaut :

| Élément | Déclaration | Ce qui cloche à 3840 |
|---|---|---|
| `#gp-menu-box` (Select) | `width: 380px; max-width: 94vw` | largeur **fixe** : 9,9 % de l'écran contre 19,8 % à 1920. `max-width` ne fait jamais grandir. |
| `#gp-overlay-box` (START) | `width: 75vw; max-width: 98vw` | la boîte s'adapte, mais son **contenu est en px fixes** (`font-size: 15px`, onglets `11px`, sections `10px`) : une boîte de 2880 px remplie de texte de 11 px. |

## Solution

**Deviner la disposition côte à côte** plutôt que de demander à l'utilisateur de
la connaître. Le ratio du canvas la donne : proche de 32:9 (deux fois un 16:9) ⇒
`full` ; proche de 16:9 ⇒ `half`. Le réglage explicite reste prioritaire, comme
`vr_mode` prime sur `vr_hint` dans FEAT-VR180.

**Rendre les deux fenêtres proportionnelles à l'écran**, chacune selon son
défaut : une largeur relative pour le menu, une échelle typographique pour les
deux. Ce n'est pas un problème propre au VR — ces fenêtres servent partout — donc
le correctif ne doit pas dégrader les résolutions ordinaires ni le mobile.

## User Stories

1. En tant qu'utilisateur sur Deck + Beast, je veux que l'image côte à côte ait
   les bonnes proportions sans avoir à connaître la différence entre `half` et
   `full`.
2. En tant qu'utilisateur sur un écran très large, je veux que les fenêtres de la
   manette restent lisibles et à l'échelle, sans loucher sur du texte de 11 px
   perdu au milieu de 3840 pixels.

## Découpage

| # | Ticket | Dépend de | Statut |
|---|---|---|---|
| 01 | [BL-126](tickets/01-ui-resolution.md) — Fenêtres manette à l'échelle de l'écran | — | ⬜ |
| 02 | [BL-125](tickets/02-ratio-sbs.md) — Deviner la disposition côte à côte | **BL-126** | ⬜ |

**BL-126 bloque BL-125**, et ce n'était pas prévu : les deux tickets étaient
écrits comme indépendants, avec BL-125 en premier. David l'a corrigé à l'ouverture
— « je ne peux pas faire le test avant d'avoir une fenêtre SELECT plus grande ».

C'est exact et vérifié : à la manette, **tout** passe par le menu Select.
`openSettings()` n'est appelé que depuis le bouton ⚙️ de l'en-tête
(`index.html:1818`, donc au doigt ou au trackpad) et depuis le menu Select
(`index.html:7112`). Il n'existe aucun autre chemin manette vers les réglages, ni
vers la bascule de disposition. La fenêtre illisible est donc celle qui commande
le réglage à vérifier.

Contournements, pour mémoire, si on veut trancher BL-125 avant : le bouton ⚙️ au
doigt ou au trackpad, ou un clavier branché (touche **B**, `index.html:6997`).

## Points tranchés à l'ouverture (2026-09-21)

1. **Le réglage « non étirée » corrige-t-il le ratio ? — indéterminé, et il le
   restera jusqu'à BL-126.** David ne peut pas faire l'essai : la fenêtre qui
   commande le réglage est celle qui est illisible. D'où l'inversion de l'ordre
   ci-dessus. Le diagnostic de BL-125 reste donc une lecture de code non
   confirmée, et son ticket garde son *à vérifier d'abord*.
2. **La détection automatique n'écrase pas un réglage enregistré.** ✅ Le choix
   explicite prime, la devinette ne s'applique qu'en son absence — même règle que
   `vr_mode` face à `vr_hint` dans FEAT-VR180.
3. **BL-126 se limite aux deux fenêtres de la manette.** ✅ Le reste de
   l'interface n'est pas dans ce lot ; le mesurer avant d'envisager de l'élargir.

## Hors périmètre

- **La lecture immersive OpenXR** — écartée par [ADR 0003](../../docs/adr/0003-client-natif.md),
  inchangé.
- **Le choix de la résolution côté système** : 3840×1080 est imposé par les
  Beast pour obtenir le mode SBS, Hoard n'a pas la main dessus.
- **Une refonte responsive complète** de l'interface : écartée au point 3
  ci-dessus. Seules les deux fenêtres de la manette sont dans ce lot.
