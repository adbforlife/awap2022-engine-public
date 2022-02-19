import heapq

import numpy as np



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


# def compute_passabilities_v2(map, team, per_turn_income, turns_left):
#     """
#     Computes grid of "smart costs" for given team.
#     Smart cost := (
#         (cost of cell towers) + (cost of roads) - 0.8 * (income from population)
#     )
#     -1 denotes impossible.
#     """
#     h = len(map)
#     w = len(map[0])
#     out = np.ones((h, w), dtype=np.float) * -1
#     paths = {}
#     frontier = [
#         [0, i, j, []]
#         for i in range(h)
#         for j in range(w)
#         if map[i][j].structure is not None and map[i][j].structure.team == team
#     ]
#     while len(frontier) > 0:
#         cost, i, j, path = heapq.heappop(frontier)
#         if out[i, j] != -1:
#             continue
#         out[i, j] = cost
#         paths[(i, j)] = path
#         for _i, _j in ((-1, 0), (1, 0), (0, 1), (0, -1)):
#             if 0 <= i+_i < h and 0 <= j+_j < w and out[i+_i][j+_j] == -1 and map[i+_i][j+_j].structure is None:
#                 new_item = [
#                     cost + map[i+_i][j+_j].passability,
#                     i+_i,
#                     j+_j,
#                     path + [(i+_i, j+_j)]
#                 ]
#                 heapq.heappush(frontier, new_item)
#     return out, paths

if __name__ == '__main__': 
    import os
    import json
    from src.game_constants import GameConstants as GC
    from src.game import Tile
    from src.player import Team
    from src.structure import Structure, StructureType

    map_path = f'./maps/flappy.awap22m'
    from src.game import MapInfo
    map_info = MapInfo(custom_map_path=map_path)

    map_file = map_info.custom_map_path
    map_data = json.load(open(map_file))

    tile_info = map_data["tile_info"]
    map_gens = map_data["generators"]

    # Parse custom map file name to name??
    width = len(tile_info)
    height = len(tile_info[0])

    assert(GC.MIN_WIDTH <= width <= GC.MAX_WIDTH)
    assert(GC.MIN_HEIGHT <= height <= GC.MAX_HEIGHT)

    map = [[Tile(i, j, tile_info[i][j][0], tile_info[i][j][1], None) for j in range(height)] for i in range(width)]

    for t in [Team.RED, Team.BLUE]:
        for x,y in map_gens[t.value]:
            map[x][y].structure = Structure(StructureType.GENERATOR, x, y, t)
    print(map)

    print(compute_passabilities(map, Team.RED))

    map = [
        [
            Tile(0, 0, 1, 0, None),
            Tile(0, 1, 3, 0, Structure(StructureType.ROAD, 0, 1, Team.BLUE)),
            Tile(0, 2, 33, 0, None),
            Tile(0, 3, 3, 0, None)
        ],
        [
            Tile(1, 0, 352, 0, Structure(StructureType.ROAD, 1, 1, Team.BLUE)),
            Tile(1, 1, 2, 0, Structure(StructureType.ROAD, 1, 1, Team.BLUE)),
            Tile(1, 2, 2, 0, None),
            Tile(1, 3, 3, 0, None)
        ],
        [
            Tile(2, 0, 3, 0, None),
            Tile(2, 1, 1, 0, Structure(StructureType.ROAD, 2, 1, Team.RED)),
            Tile(2, 2, 3, 0, None),
            Tile(2, 3, 2, 0, None)
        ],
        [
            Tile(2, 0, 3, 0, None),
            Tile(2, 1, 34, 0, None),
            Tile(2, 2, 2, 0, None),
            Tile(2, 3, 3, 0, Structure(StructureType.ROAD, 2, 1, Team.RED))
        ],
    ]

    print(np.array([[map[i][j].passability for j in range(4)] for i in range(4)]))
    print(compute_passabilities(map, Team.RED))
