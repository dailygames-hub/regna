# REGNA

Puzzle di logica: una regina in ogni riga, in ogni colonna e in ogni zona colorata, senza che due regine si tocchino (nemmeno in diagonale). Un tocco mette una X, un secondo la regina, un terzo svuota; trascinando si segnano molte X. Timer, annulla, ricomincia, X automatiche opzionali, puzzle del giorno e allenamento a 7×7, 8×8 e 9×9. Interfaccia in italiano e inglese.

Pubblicato su https://dailygames-hub.github.io/regna/ come parte di Daily Games.

## I puzzle

`puzzles.js` contiene 728 puzzle (104 settimane) generati da `gen.py` e ordinati secondo il calendario, a partire da domenica 27 settembre 2026 (giorno 1). Ogni giorno della settimana ha dimensione e difficoltà fisse:

| giorno | lato | fascia |
|---|---|---|
| lunedì, martedì | 7 | facile, facile + |
| mercoledì | 8 | facile |
| giovedì, venerdì | 8 | media, media + |
| sabato | 8 | difficile |
| domenica | 9 | difficile |

Il puzzle del giorno è il numero del giorno modulo 728, quindi finito il ciclo riparte dal primo restando allineato alla settimana. Per rigenerare o allungare la sequenza: `python3 gen.py` (crea `puzzles.json`, circa 3 minuti, nessuna dipendenza), poi incolla il contenuto in `puzzles.js` nel formato `window.REGNA_PUZZLES = [...]`. Cambiando il seme casuale in fondo a `gen.py` si ottiene una sequenza diversa.

Ogni puzzle è verificato: soluzione unica e risolvibile con sole deduzioni logiche (un risolutore "umano" con tecniche di livello crescente misura la difficoltà; i puzzle che richiederebbero di tirare a indovinare vengono scartati).

## Cose da personalizzare

Nel blocco `CONFIG` in cima allo script di `index.html`: `NAME`, `SITE_URL` (aggiunto al testo condiviso), `EPOCH` (la data del giorno 1, che deve restare una domenica per mantenere l'allineamento settimanale) e `PALETTE` (i colori delle zone).

## Fonti e licenze

- Codice e puzzle: licenza MIT (vedi `LICENSE`).
- Carattere: [Gabarito](https://github.com/naipefoundry/gabarito) di Naipe Foundry, SIL Open Font License 1.1 (`fonts/OFL.txt`), sottoinsieme latino.
- Meccanica del genere di puzzle "Star Battle" a una stella; nome, grafica, codice e puzzle sono originali.

## File

```
index.html    il gioco
puzzles.js    i 728 puzzle del calendario
gen.py        generatore e verificatore dei puzzle
game.json     scheda per la landing page di Daily Games
preview.svg   anteprima per la landing page
favicon.svg   icona
fonts/        carattere Gabarito e licenza
```
