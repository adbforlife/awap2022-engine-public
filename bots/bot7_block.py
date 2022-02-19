import sys

import random

import heapq
import math

import numpy as np

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
    self.covered_tiles = set()
    self.per_turn_income = GC.PLAYER_BASE_INCOME
    self.towers_we_tried_to_build = set()
    self.ALPHA = 0.8

  def is_valid(self, i, j):
    return i >= 0 and i < self.WIDTH and j >= 0 and j < self.HEIGHT
  
  def covered(self, m, i, j, team):
    for a in range(-2, 3):
      for b in range(-2, 3):
        if abs(a) + abs(b) <= 2:
          c = i + a
          d = j + b 
          if self.is_valid(c,d):
            if m[c][d].structure is not None:
              if m[c][d].structure.team == team and m[c][d].structure.type == StructureType.TOWER:
                return (c,d)
    return None
  
  def is_buildable(self, m, i, j, team):
    if m[i][j].structure is None:
      for delt in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
        a, b = i + delt[0], j + delt[1]
        if self.is_valid(a,b):
          if m[a][b].structure is not None: 
            if m[a][b].structure.team == team:
              return True
    return False

  def try_block(self, curr_money, m, team):
    # assume updated m and add blockage around yourself
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        if m[i][j].population > 0:
          tow = self.covered(m, i, j, team)
          if tow is not None and tow != (i,j):
            a,b = tow 
            delts = [(-2, 0), (-1, 1), (-1, 0), (-1, -1), (0, 2), (0, 1), (0, 0), (0, -1), (0, -2), (1, 1), (1, 0), (1, -1), (2, 0)]
            for delt in delts:
              a,b = i + delt[0], j + delt[1]
              if self.is_valid(a,b):
                if self.is_buildable(m, a, b, team):
                  cost = m[a][b].passability * 10 
                  if curr_money > cost:
                    curr_money -= cost
                    self.build(StructureType.ROAD, a, b)
                    m[a][b] = Tile(m[a][b].x, m[a][b].y, m[a][b].passability,
                      m[a][b].population, Structure(StructureType.ROAD, a,b, team))
                  else:
                    return curr_money

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
        if population_increase[i, j] > 0 and out[i][j] > 0 and map[i][j].structure is None and not self.covered(map, i, j, player_info.team):
          cost_tower = map[i][j].passability * 250
          cost_roads = (out[i][j] - map[i][j].passability) * 10
          turns_to_build = max(0, (cost_tower + cost_roads - curr_money) / self.per_turn_income)
          total_cost =  cost_tower + cost_roads - population_increase[i, j] * (turns_left - turns_to_build) * self.ALPHA
          # (cost of tower) + (cost of roads) - (increase in population) * (turns left - turns to build) * alpha
          if total_cost < best_cost:
            best_cost = total_cost
            best_pos = (i,j)

    self.towers_we_tried_to_build.clear()
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
            map[tx][ty] = Tile(map[tx][ty].x, map[tx][ty].y, map[tx][ty].passability,
              map[tx][ty].population, Structure(StructureType.ROAD, tx,ty, player_info.team))
            has_built = True
        else:
          cost = map[tx][ty].passability * 250
          if cost < curr_money:
            curr_money -= cost
            self.build(StructureType.TOWER, tx, ty)
            build_targets.append((tx, ty))
            map[tx][ty] = Tile(map[tx][ty].x, map[tx][ty].y, map[tx][ty].passability,
              map[tx][ty].population, Structure(StructureType.ROAD, tx,ty, player_info.team))
            has_built = True
            self.towers_we_tried_to_build.add((tx, ty))
    else:
      # block if we can't build
      self.try_block(curr_money, map, player_info.team)

    out_opp, out_paths_opp = compute_passabilities(map, 1 - player_info.team.value)
    should_bid = False

    # For each build target, figure out if bidding necessary
    for (x, y) in build_targets:
      if out_opp[x][y] >= 0 and out_opp[x][y] < out[x][y]:
        should_bid = True

    return (curr_money, has_built, should_bid)




  def play_turn(self, turn_num, map, player_info):
    self.WIDTH = len(map)
    self.HEIGHT = len(map[0])

    # copy map
    m = [[None for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]
    for i in range(self.WIDTH):
      for j in range(self.HEIGHT):
        m[i][j] = Tile(map[i][j].x, map[i][j].y, map[i][j].passability,
          map[i][j].population, Structure.make_copy(map[i][j].structure))

    for i, j in self.towers_we_tried_to_build:
      if map[i][j].structure.type == StructureType.TOWER and map[i][j].structure.team == player_info.team:
        for _i, _j in [(-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 2), (0, 1), (0, -1), (0, -2), (-1, 1), (-1, -1), (1, 1), (1, -1)]:
          self.covered_tiles.add((i+_i, j+_j))
          if self.is_valid(i+_i, j+_j):
            self.per_turn_income += map[i+_i][j+_j].population

    curr_money = player_info.money

    done = False
    bid_amount = random.randint(1, 2)
    curr_money -= bid_amount
    really_want = False
    
    while not done:
      curr_money, has_built, should_bid = self.try_build_one(curr_money, m, player_info, 250 - turn_num)
      if not really_want and should_bid:
          bid_amount += random.randint(10, 20)
          curr_money -= bid_amount
          really_want = True
      done = not has_built 

    self.set_bid(bid_amount)

    return