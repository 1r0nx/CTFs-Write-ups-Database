#!/usr/bin/env python3
"""
Maze God — résout 1000 labyrinthes 18x18 (agent 'o' en (1,1), sortie 'E').
Communication avec le serveur via pwntools ; résolution par BFS.
Renvoie une suite de moves L/R/U/D (1 case par move).
"""
from pwn import remote
from collections import deque

HOST, PORT = "chal.sigpwny.com", 3502
MOVES = {'U':(-1,0), 'D':(1,0), 'L':(0,-1), 'R':(0,1)}

def solve_maze(grid):
    R, C = len(grid), len(grid[0])
    start = goal = None
    for i in range(R):
        for j in range(C):
            if grid[i][j] == 'o': start = (i, j)
            elif grid[i][j] == 'E': goal = (i, j)
    q = deque([start]); prev = {start: None}
    while q:
        cur = q.popleft()
        if cur == goal: break
        for m, (dy, dx) in MOVES.items():
            ny, nx = cur[0] + dy, cur[1] + dx
            if 0 <= ny < R and 0 <= nx < C and grid[ny][nx] != '#' and (ny, nx) not in prev:
                prev[(ny, nx)] = (cur, m); q.append((ny, nx))
    path = []; c = goal
    while prev[c] is not None:
        pc, m = prev[c]; path.append(m); c = pc
    return ''.join(reversed(path))

def main():
    r = remote(HOST, PORT)
    for i in range(1, 1001):
        r.recvuntil(b"<<< Maze")      # entête du labyrinthe
        r.recvline()                  # fin de la ligne "<<< Maze i"
        grid = []
        for _ in range(18):           # 18 lignes, chacune préfixée d'un espace
            line = r.recvline().decode("utf-8", "replace").rstrip("\r\n")
            if line.startswith(" "):
                line = line[1:]
            grid.append(line)
        r.recvuntil(b"End >>>")        # fin du bloc
        r.sendline(solve_maze(grid).encode())
        if i % 100 == 0:
            print(f"[+] {i}/1000")
    print(r.recvall(timeout=10).decode("utf-8", "replace"))  # -> le flag

if __name__ == "__main__":
    main()
