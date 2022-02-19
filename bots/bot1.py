import sys

import random

import heapq

#import numpy as np


from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

'''
This bot randomly builds one building per turn (on a valid tile).
Note that your bot may build multiple structures per turn, as long as you can afford them.
'''

'''
def compute_passabilities(map, team):
  """
  Computes grid of cumulative passabilities for given team.
  -1 denotes impossible.
  """
  h = len(map)
  w = len(map[0])
  out = np.ones((h, w), dtype=np.float) * -1
  frontier = [
      (0, i, j)
      for i in range(h)
      for j in range(w)
      if map[i][j].structure is not None and map[i][j].structure.team == team
  ]
  while len(frontier) > 0:
      cost, i, j = heapq.heappop(frontier)
      if out[i, j] != -1:
          continue
      out[i, j] = cost
      for _i, _j in ((-1, 0), (1, 0), (0, 1), (0, -1)):
          if 0 <= i+_i < h and 0 <= j+_j < w and out[i+_i][j+_j] == -1 and map[i+_i][j+_j].structure is None:
              new_item = (
                  cost + map[i+_i][j+_j].passability,
                  i+_i,
                  j+_j
              )
              heapq.heappush(frontier, new_item)
  return out
'''

class MyPlayer(Player):

  def __init__(self):
    # print("Init")
    self.turn = 0

    return

  def is_valid(self, i, j, width, height):
    return i >= 0 and i < width and j >= 0 and j < height

  def find_prev_guys(self, map, player_info):
    # Return [(tx,ty, length)] (path to cell)
    prev_guys = [[(-1, -1) for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

    # populate existing 
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        st = map[i][j].structure
        if st is not None:
          if st.team == player_info.team:
            prev_guys[i][j] = (i,j,0)
    
    # bag of things to pop off
    dones = [[False for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]
    todos = []
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        if prev_guys[i][j] == (i,j,0):
          todos.append((i,j))
          dones[i][j] = True

    # pop off
    ind = 0
    while ind < len(todos):
      i,j = todos[ind]
      d = prev_guys[i][j][2]
      explores = [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]
      explores = list(filter(lambda x: self.is_valid(x[0], x[1], self.WIDTH, self.HEIGHT), explores))
      explores = list(filter(lambda x: not dones[x[0]][x[1]], explores))
      for exp in explores:
        a,b = exp[0], exp[1]
        todos.append((a,b))
        dones[a][b] = True
        prev_guys[a][b] = (i,j, d + 1)
      ind += 1
    
    return prev_guys

  def try_build_one(self, curr_money, prev_guys, map, player_info):
    # returns new money and whether or not it built
    has_built = False

    #out = compute_passabilities(map, player_info.team)
    #print(out)
    #breakpoint()

    best_d = 10000
    best_pos = (-1,-1)
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        if map[i][j].population > 0 and map[i][j].structure is None:
          d = prev_guys[i][j][2]
          if best_d > d:
            best_d = d
            best_pos = (i,j)
    if best_pos != (-1, -1):
      i,j = best_pos
      path = []
      d = best_d
      while d > 0:
        path.append((i,j))
        a,b = prev_guys[i][j][0], prev_guys[i][j][1]
        d = prev_guys[i][j][2]
        i,j = a,b
      for k in range(len(path))[::-1]:
        tx,ty = path[k]
        if k != 0:
          cost = map[tx][ty].passability * 10
          if cost < curr_money:
            curr_money -= cost
            self.build(StructureType.ROAD, tx, ty)
            has_built = True
        else:
          cost = map[tx][ty].passability * 250
          if cost < curr_money:
            curr_money -= cost
            self.build(StructureType.TOWER, tx, ty)
            has_built = True 
    
    return (curr_money, has_built)




  def play_turn(self, turn_num, map, player_info):

    self.WIDTH = len(map)
    self.HEIGHT = len(map[0])

    # find tiles on my team
    my_structs = []
    for x in range(self.WIDTH):
      for y in range(self.HEIGHT):
        st = map[x][y].structure
        # check the tile is not empty
        if st is not None:
          # check the structure on the tile is on my team
          if st.team == player_info.team:
            my_structs.append(st)
    
    # find prev_guys
    prev_guys = self.find_prev_guys(map, player_info)

    curr_money = player_info.money
    
    done = False
    while not done:
      curr_money, has_built = self.try_build_one(curr_money, prev_guys, map, player_info)
      done = not has_built 
    

    # call helper method to build randomly
    #self.try_random_build(map, my_structs, player_info)

    # randomly bid 1 or 2
    self.set_bid(random.randint(1, 2))

    return


  ''' Helper method for trying to build a random structure'''
  def try_random_build(self, map, my_structs, player_info):
      # choose a type of structure to build
      # build a tower for every 4 roads
      if len(my_structs) % 5 == 4:
          build_type = StructureType.TOWER
      else:
          build_type = StructureType.ROAD

      # identify the set of tiles that we can build on
      valid_tiles = []

      # look for a empty tile that is adjacent to one of our structs
      for x in range(self.MAP_WIDTH):
          for y in range(self.MAP_HEIGHT):
              # check this tile contains one of our structures
              st = map[x][y].structure
              if st is None or st.team != player_info.team:
                  continue
              # check if any of the adjacent tiles are open
              for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                  (nx, ny) = (st.x + dx, st.y + dy)
                  # check if adjacent tile is valid (on the map and empty)
                  if 0 <= nx < self.MAP_WIDTH and 0 <= ny < self.MAP_HEIGHT:
                      if map[nx][ny].structure is None:
                          cost = build_type.get_base_cost() * map[nx][ny].passability
                          # check if my team can afford this structure
                          if player_info.money >= cost:
                              # attempt to build
                              valid_tiles.append((nx, ny))

      # choose a random tile to build on
      if(len(valid_tiles) > 0):
          tx, ty = random.choice(valid_tiles)
          self.build(build_type, tx, ty)
