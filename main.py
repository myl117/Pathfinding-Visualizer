import pygame
import math
from queue import PriorityQueue
from node import Node

# setup pygame window
WIDTH = HEIGHT = 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinding Visualizer (A* algorithm)")

# init rgb colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
AZURE = (0, 128, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)

def h(p1, p2):
  x1, y1 = p1
  x2, y2 = p2
  return abs(x1 - x2) + abs(y1 - y2)

def visualize_path(came_from, current, draw): 
  while current in came_from:
    current = came_from[current]
    current.make_path()
    draw()

def algorithm(draw, grid, start, end):
  count = 0
  open_set = PriorityQueue()
  open_set.put((0, count, start))
  came_from = {}
  g_score = {node: float("inf") for row in grid for node in row}
  g_score[start] = 0
  f_score = {node: float("inf") for row in grid for node in row}
  f_score[start] = h(start.get_position(), end.get_position())

  # flash clone of open_set var
  open_set_clone = {start}

  while not open_set.empty():
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
    
    # sync with clone
    current = open_set.get()[2]
    open_set_clone.remove(current)

    if current == end:
      visualize_path(came_from, end, draw)

      # repaint start and end nodes
      start.make_start()
      end.make_end()
      
      return True

    for neighbour in current.neighbours:
      temp_g_score = g_score[current] + 1

      if temp_g_score < g_score[neighbour]:
        came_from[neighbour] = current
        g_score[neighbour] = temp_g_score
        f_score[neighbour] = temp_g_score + h(neighbour.get_position(), end.get_position())
        if neighbour not in open_set_clone:
          count += 1
          open_set.put((f_score[neighbour], count, neighbour))
          open_set_clone.add(neighbour)
          neighbour.make_open()

    draw()

    if current != start:
      current.make_closed()

  return False

def build_grid(rows, width):
  grid = []
  gap = width // rows

  for i in range(rows):
    grid.append([])
    for j in range(rows):
      node = Node(i, j, gap, rows)
      grid[i].append(node) 

  return grid


def draw_grid(win, rows, width):
  gap = width // rows
  for i in range(rows):
    pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    
    for j in range(rows):
      pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
  win.fill(WHITE)

  for row in grid:
    for node in row:
      node.draw(win)

  draw_grid(win, rows, width)
  pygame.display.update() 

def get_clicked_position(pos, rows, width):
  gap = width // rows
  y, x = pos

  row = y // gap
  col = x // gap

  return row, col

def main(win, width):
  ROWS = 100
  grid = build_grid(ROWS, width)
  
  start = None
  end = None

  run = True
  started = False

  while run:
    draw(win, grid, ROWS, width)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        run = False

      if started:
        continue

      if pygame.mouse.get_pressed()[0]: # left mouse click
        # get click pos
        pos = pygame.mouse.get_pos()
        row, col = get_clicked_position(pos, ROWS, width)
        node = grid[row][col]

        # if start and end nodes have not yet been placed
        if not start and node != end:
          print('placed start')
          start = node
          start.make_start()

        elif not end and node != start:
          print('placed end')
          end = node
          end.make_end()

        elif node != end and node != start:
          print('placed obstacle')
          node.make_obstacle()
            
      elif pygame.mouse.get_pressed()[2]: # right mouse click
        pos = pygame.mouse.get_pos()
        row, col = get_clicked_position(pos, ROWS, width)
        node = grid[row][col]

        node.reset()

        if node == start:
          start = None
        elif node == end:
          end = None

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE and start and end:
          # update neighbours (incase user adds obstacles)
          for row in grid:
            for node in row:
              node.update_neighbours(grid)

          algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

  pygame.quit()

main(WIN, WIDTH)
