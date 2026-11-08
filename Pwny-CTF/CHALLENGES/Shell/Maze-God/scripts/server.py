#!/usr/bin/env python3
import string
import random

N_PASSWORDS = 1000
WALL = '#'
GOAL = 'E'
EMPTY = ' '
AGENT = 'o'

def adjacent(cell):
  i,j = cell
  for (y,x) in ((1,0), (0,1), (-1, 0), (0,-1)):
    yield (i+y, j+x), (i+2*y, j+2*x)

def gen_maze(width, height):
  width += 2 
  height += 2
  rows, cols = height, width

  maze = {}

  spaceCells = set()
  connected = set()
  walls = set()

  # Initialize with grid.
  for i in range(rows):
    for j in range(cols):
      if (i%2 == 1) and (j%2 == 1):
        maze[(i,j)] = EMPTY
      else:
        maze[(i,j)] = WALL 

  # Fill in border.
  for i in range(rows):
    maze[(i,0)] = WALL
    maze[(i,cols-1)] = WALL
  for j in range(cols):
    maze[(0,j)] = WALL
    maze[(rows-1,j)] = WALL

  for i in range(rows):
    for j in range(cols):
      if maze[(i,j)] == EMPTY:
        spaceCells.add((i,j))
      if maze[(i,j)] == WALL:
        walls.add((i,j))

  # Prim's algorithm to knock down walls.
  originalSize = len(spaceCells)
  connected.add((1,1))
  while len(connected) < len(spaceCells):
    doA, doB = None, None
    cns = list(connected)
    random.shuffle(cns)
    for (i,j) in cns:
      if doA is not None: break
      for A, B in adjacent((i,j)):
        if A not in walls: 
          continue
        if (B not in spaceCells) or (B in connected):
          continue
        doA, doB = A, B
        break
    A, B = doA, doB
    maze[A] = EMPTY
    walls.remove(A)
    spaceCells.add(A)
    connected.add(A)
    connected.add(B)

  # Insert character and goals.
  TL = (1,1)
  BR = (rows-2, cols-2)
  if rows % 2 == 0:
    BR = (BR[0]-1, BR[1])
  if cols % 2 == 0:
    BR = (BR[0], BR[1]-1)

  maze[TL] = AGENT
  maze[BR] = GOAL

  lines = []
  for i in range(rows):
    lines.append(''.join(maze[(i,j)] for j in range(cols)))
  #print(lines)
  return lines

def print_maze(maze,i=0):
    print("<<< Maze "+str(i))
    for line in maze:
        print(" " + line)
    print("             End >>>")

def valid_move(maze,pos,move):
    if move == None:
        return False
    endpos = tuple(map(sum,zip(pos,move)))
    endVal = maze[endpos[0]][endpos[1]] 
    if endVal == '#':
        print("Hit Wall!")
        return False
    elif endVal == 'E' or endVal == ' ' or endVal == 'o':
        return True

LEFT = (0,-1)
RIGHT = (0,1)
UP = (-1,0)
DOWN = (1,0)
def check_solution(maze,solution,start):
    pos = start
    for action in solution:
        move = None
        if action == 'L':
            move = LEFT
        elif action == 'R':
            move = RIGHT
        elif action == 'U':
            move = UP
        elif action == 'D':
            move = DOWN
        else:
            return False
        #print(action,pos,move)
        if not valid_move(maze,pos,move):
            return False
        pos = tuple(map(sum,zip(pos,move)))
    return maze[pos[0]][pos[1]] == 'E'
        

def main():
    print("Can you escape from the 1000 layer maze!?")
    print("Solution format L R U D (Left Right Up Down)")

    with open("flag.txt", "r") as flag_file:
        flag = flag_file.read()

    for i in range(1,1001):
        cur_maze = gen_maze(16,16)
        print_maze(cur_maze,i)
        attempt = input()
        if not check_solution(cur_maze, attempt, (1,1)):
            print("Wrong!")
            exit()
        else:
            print("Level Pass!")
        
    print(f"Thanks so much! Here's your prize: {flag}")
        
if __name__ == "__main__":
    main()