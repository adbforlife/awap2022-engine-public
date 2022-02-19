import sys

import random

import heapq
import math

import numpy as np

import ipdb

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

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
    self.turn = 0
    self.covered_tiles = set()
    return

  def is_valid(self, i, j, width, height):
    return i >= 0 and i < width and j >= 0 and j < height

  def try_build_one(self, curr_money, map, player_info, turns_left):
    # returns new money and whether or not it built
    has_built = False
    ipdb.set_trace()

    out, paths = compute_passabilities(map, player_info.team)
    best_cost = math.inf
    best_pos = (-1,-1)
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        if map[i][j].population > 0 and map[i][j].structure is None and out[i][j] > 0:
          population_increase = 0
          for _i, _j in [(-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 2), (0, 1), (0, -1), (0, -2), (-1, 1), (-1, -1), (1, 1), (1, -1)]:
            if self.is_valid(i+_i, j+_j, self.WIDTH, self.HEIGHT) and (i+_i, j+_j) not in self.covered_tiles:
              population_increase += map[i+_i][j+_j].population
          if population_increase == 0:
            continue
          total_cost = map[i][j].passability * 250 \
            + (out[i][j] - map[i][j].passability) * 10 \
            - population_increase * turns_left
          # (cost of tower) + (cost of roads) - (increase in population) * (turns left)
          if total_cost < best_cost:
            best_cost = total_cost
            best_pos = (i,j)
    # print(best_cost)
    
    if best_pos != (-1, -1):
      i,j = best_pos 
      path = paths[(i,j)]
      for k in range(len(path)):
        tx,ty = path[k]
        if k != len(path) - 1:
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
            for _i, _j in [(-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 2), (0, 1), (0, -1), (0, -2), (-1, 1), (-1, -1), (1, 1), (1, -1)]:
              self.covered_tiles.add((tx+_i, ty+_j))

        
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
    
    curr_money = player_info.money
    
    done = False
    while not done:
      curr_money, has_built = self.try_build_one(curr_money, map, player_info, 250 - turn_num)
      done = not has_built 

    # randomly bid 1 or 2
    self.set_bid(random.randint(1, 2))

    return