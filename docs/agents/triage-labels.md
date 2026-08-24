# Labels de triage → vocabulaire `Status:` local

Ce repo utilise une seule ligne `Status:` (une valeur à la fois). Les cinq rôles de
triage de Matt Pocock s'y projettent ainsi :

| Status        | Emoji | Rôle(s) de triage Matt           |
|---------------|-------|----------------------------------|
| ready         | ⬜    | ready-for-agent                  |
| in-progress   | 🔄    | —                                |
| waiting-human | 🧑    | ready-for-human, needs-info      |
| done          | ✅    | —                                |
| wontfix       | 🚫    | wontfix                          |

États de cycle de vie uniquement (sans équivalent rôle de triage) : `in-progress` 🔄,
`done` ✅.

`needs-triage` n'est pas utilisé — les lots naissent déjà spécifiés, pas triés depuis
des rapports externes bruts. `/to-prd` et `/to-issues` créent les artefacts à
`ready` ⬜.
