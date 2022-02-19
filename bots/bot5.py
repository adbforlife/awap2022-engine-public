import sys

import random

import heapq
import math

import numpy as np

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

    Returns:

	out: 
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
    self.covered_tiles = set()
    return

  def is_valid(self, i, j, width, height):
    return i >= 0 and i < width and j >= 0 and j < height

  def try_build_one(self, curr_money, map, player_info, turns_left):
    # returns new money and whether or not it built
    has_built = False
    build_targets = []

    population_increase = np.array([
      [
        map[i][j].population if (i, j) not in self.covered_tiles else 0
        for j in range(self.HEIGHT)
      ]
      for i in range(self.WIDTH)
    ])
    population_increase = np.pad(population_increase, ((2, 2), (2, 2)))
    population_increase = population_increase[2:-2, 2:-2] \
      + population_increase[1:-3, 2:-2] \
      + population_increase[0:-4, 2:-2] \
      + population_increase[3:-1, 2:-2] \
      + population_increase[4:, 2:-2] \
      + population_increase[2:-2, 0:-4] \
      + population_increase[2:-2, 1:-3] \
      + population_increase[2:-2, 3:-1] \
      + population_increase[2:-2, 4:] \
      + population_increase[1:-3, 1:-3] \
      + population_increase[3:-1, 1:-3] \
      + population_increase[1:-3, 3:-1] \
      + population_increase[3:-1, 3:-1]

    out, paths = compute_passabilities(map, player_info.team)
    best_cost = math.inf
    best_pos = (-1,-1)
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        if population_increase[i, j] > 0 and out[i][j] > 0 and map[i][j].structure is None:
          total_cost = map[i][j].passability * 250 \
            + (out[i][j] - map[i][j].passability) * 10 \
            - population_increase[i, j] * turns_left
          # (cost of tower) + (cost of roads) - (increase in population) * (turns left)
          if total_cost < best_cost:
            best_cost = total_cost
            best_pos = (i,j)

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
	    build_targets.append((tx, ty))
            has_built = True
        else:
          cost = map[tx][ty].passability * 250
          if cost < curr_money:
            curr_money -= cost
            self.build(StructureType.TOWER, tx, ty)
	    build_targets.append((tx, ty))
            has_built = True
            for _i, _j in [(-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 2), (0, 1), (0, -1), (0, -2), (-1, 1), (-1, -1), (1, 1), (1, -1)]:
              self.covered_tiles.add((tx+_i, ty+_j))

    out_opp, out_paths_opp = compute_passabilities(map, 1 - player_info.team)
    # For each build target, figure out if bidding necessary
    for build_target in build_targets:
	    pass

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
    curr_money = player_info.money
    
    done = False
    while not done:
      curr_money, has_built = self.try_build_one(curr_money, map, player_info, 250 - turn_num)
      done = not has_built 

    # randomly bid 1 or 2
    self.set_bid(random.randint(1, 2))

    return
