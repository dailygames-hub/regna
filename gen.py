#!/usr/bin/env python3
"""
Generatore di puzzle per REGNA (genere "Star Battle" a una stella / regine).

Regole: griglia N x N divisa in N zone. Una regina per riga, per colonna e per zona;
due regine non possono toccarsi, nemmeno in diagonale (solo le otto caselle intorno).

Per ogni puzzle:
  1. si piazza una soluzione valida a caso;
  2. si fanno crescere le zone attorno alle regine;
  3. si verifica che la soluzione sia unica;
  4. un risolutore "umano" misura la difficoltà usando solo deduzioni logiche;
     se deve tirare a indovinare il puzzle viene scartato.

Uso: python3 gen.py            -> genera puzzles.json (728 puzzle, 104 settimane)
     python3 gen.py 20         -> genera solo 20 puzzle (prova rapida)
Senza dipendenze esterne.
"""
import json, random, sys, time
from itertools import combinations

# ---------------------------------------------------------------- calendario
# Il giorno 1 di Daily Games (27 settembre 2026) è una domenica: la sequenza parte da lì.
# (dimensione, fascia di difficoltà) per domenica, lunedì, ..., sabato
WEEK = [
    (9, "hard"),    # domenica
    (7, "easy"),    # lunedì
    (7, "easy+"),   # martedì
    (8, "easy"),    # mercoledì
    (8, "medium"),  # giovedì
    (8, "medium+"), # venerdì
    (8, "hard"),    # sabato
]
WEEKS = 104

# fasce: (livello massimo di tecnica richiesto, numero minimo e massimo di passi "non banali")
# punteggio di difficoltà = passi non banali + 4 per ogni livello oltre il 2
def score(level, steps):
    return steps + 4 * max(0, level - 2)

BANDS = {
    "easy":    (0, 1),
    "easy+":   (2, 3),
    "medium":  (3, 5),
    "medium+": (5, 8),
    "hard":    (8, 60),
}

# ---------------------------------------------------------------- utilità
def neighbors(r, c, n):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                rr, cc = r + dr, c + dc
                if 0 <= rr < n and 0 <= cc < n:
                    yield rr, cc

def attacks(a, b):
    """True se due caselle non possono ospitare entrambe una regina (stessa riga/colonna o adiacenti)."""
    (r1, c1), (r2, c2) = a, b
    return r1 == r2 or c1 == c2 or (abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1)

# ---------------------------------------------------------------- 1. soluzione casuale
def random_placement(n, rnd):
    cols = [None] * n
    used = set()
    def rec(r):
        if r == n:
            return True
        order = list(range(n)); rnd.shuffle(order)
        for c in order:
            if c in used: continue
            if r > 0 and abs(cols[r - 1] - c) <= 1: continue
            cols[r] = c; used.add(c)
            if rec(r + 1): return True
            used.discard(c)
        return False
    rec(0)
    return cols  # cols[r] = colonna della regina nella riga r

# ---------------------------------------------------------------- 2. crescita delle zone
def grow_regions(n, cols, rnd):
    region = [[-1] * n for _ in range(n)]
    for r in range(n):
        region[r][cols[r]] = r
    # pesi diversi per avere zone grandi e zone piccole
    weights = [rnd.choice([0.15, 0.4, 1.0, 1.0, 2.0, 3.5]) for _ in range(n)]
    free = n * n - n
    while free:
        # zone che hanno almeno una casella libera adiacente
        frontier = {}
        for r in range(n):
            for c in range(n):
                if region[r][c] == -1: continue
                for rr, cc in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):
                    if 0 <= rr < n and 0 <= cc < n and region[rr][cc] == -1:
                        frontier.setdefault(region[r][c], []).append((rr, cc))
        regs = list(frontier)
        z = rnd.choices(regs, weights=[weights[k] for k in regs])[0]
        rr, cc = rnd.choice(frontier[z])
        region[rr][cc] = z
        free -= 1
    return region

# ---------------------------------------------------------------- 3. unicità
def count_solutions(n, region, limit=2):
    cells_by_region = {}
    for r in range(n):
        for c in range(n):
            cells_by_region.setdefault(region[r][c], []).append((r, c))
    cols = [None] * n; used_c = set(); used_z = set(); found = 0
    def rec(r):
        nonlocal found
        if found >= limit: return
        if r == n:
            found += 1; return
        for c in range(n):
            if c in used_c: continue
            z = region[r][c]
            if z in used_z: continue
            if r > 0 and abs(cols[r-1] - c) <= 1: continue
            cols[r] = c; used_c.add(c); used_z.add(z)
            rec(r + 1)
            used_c.discard(c); used_z.discard(z)
    rec(0)
    return found

# ---------------------------------------------------------------- 4. risolutore logico
def logic_solve(n, region):
    """Risolve con tecniche umane. Ritorna (risolto, livello_max, passi_non_banali) oppure None se si blocca."""
    cand = [[True] * n for _ in range(n)]
    queens = set()
    zone_cells = {}
    for r in range(n):
        for c in range(n):
            zone_cells.setdefault(region[r][c], []).append((r, c))
    max_level = 0
    hard_steps = 0

    def place(r, c):
        queens.add((r, c))
        for i in range(n):
            cand[r][i] = False; cand[i][c] = False
        for rr, cc in zone_cells[region[r][c]]:
            cand[rr][cc] = False
        for rr, cc in neighbors(r, c, n):
            cand[rr][cc] = False
        cand[r][c] = False

    def candidates_of(cells):
        return [(r, c) for r, c in cells if cand[r][c]]

    def groups():
        """tutte le unità (righe, colonne, zone) con le loro caselle."""
        for r in range(n): yield ("row", r, [(r, c) for c in range(n)])
        for c in range(n): yield ("col", c, [(r, c) for r in range(n)])
        for z, cells in zone_cells.items(): yield ("zone", z, cells)

    def unit_has_queen(kind, key):
        for (r, c) in queens:
            if kind == "row" and r == key: return True
            if kind == "col" and c == key: return True
            if kind == "zone" and region[r][c] == key: return True
        return False

    while len(queens) < n:
        progressed = False
        # livello 1: casella unica in un'unità
        for kind, key, cells in groups():
            if unit_has_queen(kind, key): continue
            cs = candidates_of(cells)
            if len(cs) == 0: return None
            if len(cs) == 1:
                place(*cs[0]); progressed = True; max_level = max(max_level, 1); break
        if progressed: continue
        # livello 1: zona confinata in una riga/colonna -> elimina il resto della riga/colonna
        for z, cells in zone_cells.items():
            if unit_has_queen("zone", z): continue
            cs = candidates_of(cells)
            rows = {r for r, _ in cs}; colsz = {c for _, c in cs}
            if len(rows) == 1:
                r = next(iter(rows))
                for c in range(n):
                    if cand[r][c] and region[r][c] != z: cand[r][c] = False; progressed = True
            if len(colsz) == 1:
                c = next(iter(colsz))
                for r in range(n):
                    if cand[r][c] and region[r][c] != z: cand[r][c] = False; progressed = True
            if progressed: max_level = max(max_level, 1); break
        if progressed: continue
        # livello 1 bis: riga/colonna i cui candidati stanno tutti in una zona -> quella zona resta confinata lì
        for kind, key, cells in groups():
            if kind == "zone" or unit_has_queen(kind, key): continue
            cs = candidates_of(cells)
            zs = {region[r][c] for r, c in cs}
            if len(zs) == 1:
                z = next(iter(zs))
                for r, c in zone_cells[z]:
                    if cand[r][c] and (r, c) not in cs: cand[r][c] = False; progressed = True
                if progressed: max_level = max(max_level, 1); break
        if progressed: continue
        # livello 2: una casella attaccata da tutti i candidati di un'altra zona non può avere la regina
        for r in range(n):
            for c in range(n):
                if not cand[r][c]: continue
                for z, cells in zone_cells.items():
                    if z == region[r][c] or unit_has_queen("zone", z): continue
                    cs = candidates_of(cells)
                    if cs and all(attacks((r, c), x) for x in cs):
                        cand[r][c] = False; progressed = True; break
                if progressed: break
            if progressed: break
        if progressed: max_level = max(max_level, 2); hard_steps += 1; continue
        # livello 3/4: k zone i cui candidati occupano solo k righe (o colonne) -> quelle righe appartengono a loro
        open_zones = [z for z in zone_cells if not unit_has_queen("zone", z)]
        for k in (2, 3):
            for combo in combinations(open_zones, k):
                for axis in ("row", "col"):
                    lines = set()
                    for z in combo:
                        for r, c in candidates_of(zone_cells[z]):
                            lines.add(r if axis == "row" else c)
                    if len(lines) != k: continue
                    for line in lines:
                        cells = [(line, c) for c in range(n)] if axis == "row" else [(r, line) for r in range(n)]
                        for r, c in cells:
                            if cand[r][c] and region[r][c] not in combo:
                                cand[r][c] = False; progressed = True
                    if progressed: break
                if progressed: break
            if progressed:
                max_level = max(max_level, 3 if k == 2 else 4); hard_steps += 1; break
        if progressed: continue
        # livello 3/4 duale: k righe (o colonne) i cui candidati stanno in sole k zone
        for k in (2, 3):
            for axis in ("row", "col"):
                open_lines = [i for i in range(n) if not unit_has_queen(axis, i)]
                for combo in combinations(open_lines, k):
                    zs = set()
                    for line in combo:
                        cells = [(line, c) for c in range(n)] if axis == "row" else [(r, line) for r in range(n)]
                        zs |= {region[r][c] for r, c in candidates_of(cells)}
                    if len(zs) != k: continue
                    for z in zs:
                        for r, c in zone_cells[z]:
                            line = r if axis == "row" else c
                            if cand[r][c] and line not in combo:
                                cand[r][c] = False; progressed = True
                    if progressed: break
                if progressed: break
            if progressed:
                max_level = max(max_level, 3 if k == 2 else 4); hard_steps += 1; break
        if progressed: continue
        return None  # servirebbe tirare a indovinare
    return True, max_level, hard_steps

# ---------------------------------------------------------------- mutazione delle zone
def connected(cells):
    cells = set(cells)
    if not cells: return True
    start = next(iter(cells)); seen = {start}; stack = [start]
    while stack:
        r, c = stack.pop()
        for nb in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)):
            if nb in cells and nb not in seen:
                seen.add(nb); stack.append(nb)
    return len(seen) == len(cells)

def mutate(n, region, cols, rnd):
    """Sposta una casella di confine in una zona vicina, mantenendo zone connesse e le regine nelle loro zone."""
    queen_cells = {(r, cols[r]) for r in range(n)}
    for _ in range(40):
        r, c = rnd.randrange(n), rnd.randrange(n)
        if (r, c) in queen_cells: continue
        z = region[r][c]
        others = {region[rr][cc] for rr, cc in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)) if 0 <= rr < n and 0 <= cc < n and region[rr][cc] != z}
        if not others: continue
        new = [row[:] for row in region]
        new[r][c] = rnd.choice(list(others))
        old_cells = [(rr, cc) for rr in range(n) for cc in range(n) if new[rr][cc] == z]
        if not old_cells or not connected(old_cells): continue
        return new
    return None

def singles(region):
    """numero di zone formate da una sola casella (troppe rendono il puzzle banale)"""
    sizes = {}
    for row in region:
        for z in row: sizes[z] = sizes.get(z, 0) + 1
    return sum(1 for v in sizes.values() if v == 1)

def evaluate(n, region):
    if count_solutions(n, region) != 1: return None
    res = logic_solve(n, region)
    if not res: return None
    _, level, steps = res
    return level, steps

# ---------------------------------------------------------------- generazione
def make_puzzle(n, band, rnd, max_tries=8000):
    lo, hi = BANDS[band]
    for _ in range(max_tries):
        cols = random_placement(n, rnd)
        region = grow_regions(n, cols, rnd)
        ev = evaluate(n, region)
        if ev is None: continue
        level, steps = ev
        # scalata: mutazioni che aumentano la difficoltà finché non si entra nella fascia
        for _ in range(400):
            sc = score(level, steps)
            if lo <= sc <= hi and singles(region) <= 1:
                return dict(n=n, r="".join(str(region[r][c]) for r in range(n) for c in range(n)),
                            s="".join(str(c) for c in cols), band=band, level=level, steps=steps)
            if sc > hi: break
            cand = mutate(n, region, cols, rnd)
            if cand is None: continue
            ev2 = evaluate(n, cand)
            if ev2 is None: continue
            if score(*ev2) >= sc or (score(*ev2) >= sc - 1 and singles(cand) < singles(region)):
                region, (level, steps) = cand, ev2
    return None

def main():
    total = int(sys.argv[1]) if len(sys.argv) > 1 else WEEKS * 7
    rnd = random.Random(20260927)
    puzzles = []; t0 = time.time()
    seen = set()
    for i in range(total):
        n, band = WEEK[i % 7]
        while True:
            p = make_puzzle(n, band, rnd)
            if p is None:
                raise SystemExit(f"impossibile generare {n}x{n} {band}")
            if p["r"] in seen: continue
            seen.add(p["r"]); break
        puzzles.append(p)
        if (i + 1) % 28 == 0:
            print(f"{i+1}/{total} puzzle, {time.time()-t0:.0f}s", flush=True)
    json.dump(puzzles, open("puzzles.json", "w"), separators=(",", ":"))
    from collections import Counter
    print("fatto:", len(puzzles), "puzzle in", f"{time.time()-t0:.0f}s")
    print(Counter((p["n"], p["band"]) for p in puzzles))

if __name__ == "__main__":
    main()
