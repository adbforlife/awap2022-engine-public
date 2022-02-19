import sys

import random
import heapq

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

def compute_distances_from_cell(map, row, col):
    D = [[float('inf') for i in range(len(map[0]))] for j in range(len(map))]

    def set_value(r,c, val):
        if (r >= 0 and r < len(D)):
            if (c >= 0 and c < len(D[0])):
                D[r][c] = val
    def get(r,c):
        if (r >= 0 and r < len(D)):
            if (c >= 0 and c < len(D[0])):
                return D[r][c]
        return float('inf')
    def get_passability(r,c):
        if r == row and c == col: return 0

        if (r >= 0 and r < len(D)):
            if (c >= 0 and c < len(D[0])):
                return map[r][c].passability
        return float('inf')

    def in_bounds(r,c):
        if (r >= 0 and r < len(D)):
            return (c >= 0 and c < len(D[0]))
        return False

    set_value(row, col, 0)

    heap = [(0, (row, col))]
    visited = set()
    while len(heap) > 0:
        (cost, (r,c)) = heapq.heappop(heap)
        if ((r,c) in visited): continue

        visited.add((r,c))
        set_value(r,c, cost)

        for new_r, new_c in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
            if ((new_r, new_c) not in visited and in_bounds(new_r, new_c)):
                new_cost = cost + get_passability(r,c)
                heapq.heappush(heap, (new_cost, (new_r, new_c)))

    return D

class Cell():
    def __init__(self, r, c, dist, passability, utility):
        self.r = r
        self.c = c
        self.dist = dist
        self.passability = passability
        self.utility = utility

    def __hash__(self):
        return hash((r,c))
    def __eq__(self, other):
        return self.r == other.r and self.c == other.c

class MyPlayer(Player):
    def __init__(self):
        self.turn = 0

        self.roads = set()
        self.towers = set()
        self.generators = set()

    def real_init(self, map, player_info):
        self.HEIGHT = len(map)
        self.WIDTH = len(map[0])

        for r in range(self.HEIGHT):
            for c in range(self.WIDTH):
                tile = map[r][c]
                if tile.structure is not None:
                    team = tile.structure.team
                    tile_type = tile.structure.type
                    if (team == player_info.team and tile_type == StructureType.GENERATOR):
                        self.generators.add((r,c))

        gen_r, gen_c = list(self.generators)[0]
        mins = compute_distances_from_cell(map, gen_r, gen_c)
        for gen_r, gen_c in self.generators:
            D = compute_distances_from_cell(map, gen_r, gen_c)
            mins = [[min(mins[r][c], D[r][c]) for c in range(len(D[0]))] for r in range(len(D))]

        for r in range(len(D)):
            for c in range(len(D[0])):
                print(r,c, D[r][c])


    def play_turn(self, turn_num, map, player_info):
        if turn_num == 0:
            self.real_init(map, player_info)

        return
