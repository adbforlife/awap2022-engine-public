import sys

import random

import heapq

import numpy as np
from copy import deepcopy
from src.game import Tile

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

'''
This bot randomly builds one building per turn (on a valid tile).
Note that your bot may build multiple structures per turn, as long as you can afford them.
'''

def compute_passabilities(map, team):
    """
    Computes grid of cumulative passabilities for given team.
    -1 denotes impossible.
    """
    h = len(map)
    w = len(map[0])
    out = np.ones((h, w), dtype=np.float) * -1
    paths = {}
    frontier = [
        [0, i, j, []]
        for i in range(h)
        for j in range(w)
        if map[i][j].structure is not None and map[i][j].structure.team == team
    ]
    while len(frontier) > 0:
        cost, i, j, path = heapq.heappop(frontier)
        if out[i, j] != -1:
            continue
        out[i, j] = cost
        paths[(i, j)] = path
        for _i, _j in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            if 0 <= i+_i < h and 0 <= j+_j < w and out[i+_i][j+_j] == -1 and map[i+_i][j+_j].structure is None:
                new_item = [
                    cost + map[i+_i][j+_j].passability,
                    i+_i,
                    j+_j,
                    path + [(i+_i, j+_j)]
                ]
                heapq.heappush(frontier, new_item)
    return out, paths


class MyPlayer(Player):

  def __init__(self):
    # print("Init")
    self.turn = 0

    return

  def is_valid(self, i, j, width, height):
    return i >= 0 and i < width and j >= 0 and j < height

  def try_build_one(self, curr_money, m, team):
    # returns new money and whether or not it built
    # modifies m
    has_built = False

    out, paths = compute_passabilities(m, team)
    best_d = 10000
    best_pos = (-1,-1)
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        if m[i][j].population > 0 and m[i][j].structure is None:
          if out[i][j] > 0:
            if out[i][j] < best_d:
              best_d = out[i][j]
              best_pos = (i,j)

    if best_pos != (-1, -1):
      i,j = best_pos 
      path = paths[(i,j)]
      for k in range(len(path)):
        tx,ty = path[k]
        if k != len(path) - 1:
          cost = m[tx][ty].passability * 10
          if cost < curr_money:
            curr_money -= cost
            self.build(StructureType.ROAD, tx, ty)
            m[tx][ty] = Tile(m[tx][ty].x, m[tx][ty].y, m[tx][ty].passability,
              m[tx][ty].population, Structure(StructureType.ROAD, i,j, team))
            has_built = True
        else:
          cost = m[tx][ty].passability * 250
          if cost < curr_money:
            curr_money -= cost
            self.build(StructureType.TOWER, tx, ty)
            m[tx][ty] = Tile(m[tx][ty].x, m[tx][ty].y, m[tx][ty].passability,
              m[tx][ty].population, Structure(StructureType.TOWER, i,j, team))
            has_built = True 
        
    return (curr_money, has_built)


  def play_turn(self, turn_num, map, player_info):
    # print(turn_num)

    self.WIDTH = len(map)
    self.HEIGHT = len(map[0])

    m = [[None for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        m[i][j] = Tile(map[i][j].x, map[i][j].y, map[i][j].passability,
          map[i][j].population, Structure.make_copy(map[i][j].structure))

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
    

    # try targets one by one
    curr_money = player_info.money
    done = False
    while not done:
      curr_money, has_built = self.try_build_one(curr_money, m, player_info.team)
      done = not has_built 
    

    # randomly bid 1 or 2
    self.set_bid(random.randint(4, 6))

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
