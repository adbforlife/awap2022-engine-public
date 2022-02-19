import json
import argparse
import os
import sys

from run_game import run_match
from src.structure import *
from src.game import *
from src.custom_json import *
from src.game_constants import GameConstants as GC

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-m","--map_name", help="Run with custom map (./maps/map-CUSTOM_MAP_NAME.awap22m).", default=None)
	parser.add_argument("-n","--rounds", help="Number of rounds to run for.", default=200)
	parser.add_argument("-p1","--p1_bot_name", help="Player 1 bot name (./bots/P1_BOT_NAME.py).", default=None)
	parser.add_argument("-p2","--p2_bot_name", help="Player 2 bot name (./bots/P2_BOT_NAME.py).", default=None)
	parser.add_argument("-replay","--replay_file_name", help="Replay file name (./replays/{REPLAY_NAME}.awap22r)", default=None)

	args = parser.parse_args()

	rounds = int(args.rounds)
	replay_file_base = args.replay_file_name

	results = []

	for i in range(rounds):
		game_result = run_match(args.map_name, args.p1_bot_name, args.p2_bot_name, f"replay_file_base_{i}")
		results.append((i, game_result["winner"]))
		# print(f"""Winner: {game_result["winner"]}""")


	for (round, res) in results:
		print(f"""Round {round} winner: {res}""")