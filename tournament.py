import json
import argparse
import os
import sys
# import ipdb

from run_game import run_match
from src.structure import *
from src.game import *
from src.custom_json import *
from src.game_constants import GameConstants as GC

maps = ["flappy", "island", "modified_flappy", "multiple_islands", "ridges"]

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	# parser.add_argument("-m","--map_name", help="Run with custom map (./maps/map-CUSTOM_MAP_NAME.awap22m).", default=None)
	parser.add_argument("-n","--rounds", help="Number of rounds to run for.", default=200)
	parser.add_argument("-p1","--p1_bot_name", help="Player 1 bot name (./bots/P1_BOT_NAME.py).", default=None)
	parser.add_argument("-p2","--p2_bot_name", help="Player 2 bot name (./bots/P2_BOT_NAME.py).", default=None)
	parser.add_argument("-replay","--replay_file_name", help="Replay file name (./replays/{REPLAY_NAME}.awap22r)", default=None)

	args = parser.parse_args()

	rounds = int(args.rounds)
	replay_file_base = args.replay_file_name

	results = []
	bot_1_wins = 0
	bot_2_wins = 0

	for i in range(rounds):
		if i < len(maps):
			selected_map = maps[i % len(maps)]
		else:
			selected_map = "bad_baba_nonexistent_map"
		game_result = run_match(selected_map, args.p1_bot_name, args.p2_bot_name, f"replay_file_base_{i}")
		results.append((i, game_result["winner"]))
		print(f"""Winner: {game_result["winner"]}""")
		
		if game_result["winner"] == 1:
			bot_1_wins += 1
		elif game_result["winner"] == 2:
			bot_2_wins += 1
		else:
			print("Unrecognized winner")

		print("Bot 1 win rate: ", bot_1_wins/(i+1) * 100)
		print("Bot 2 win rate: ", bot_2_wins/(i+1) * 100)


	for (round, res) in results:
		print(f"""Round {round} winner: {res}""")