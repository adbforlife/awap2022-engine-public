import json
import argparse
import os
import sys

from run_game import run_match
from src.structure import *
from src.game import *
from src.custom_json import *
from src.game_constants import GameConstants as GC

maps = ["flappy", "island", "modified_flappy", "multiple_islands", "ridges", "big_blockade", "trench", "two_modes"]
bots_to_use = ["bot4_block", "bot4", "bot2.5", "bot3"] #, "c1", "c2", "c3"]
nbots = len(bots_to_use)
replay_file_base = "tournament_replay"

class Bot():
	def __init__(self, name):
		self.name = name
		self.wins = 0
		self.rounds_played = 0

	def update_result(self, did_win):
		self.rounds_played += 1
		if did_win:
			self.wins += 1

	def win_rate(self):
		if self.rounds_played == 0:
			return 0
		return self.wins / self.rounds_played

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-n","--rounds", help="Number of rounds to run for.", default=5)

	args = parser.parse_args()

	rounds = int(args.rounds)

	bots = []
	for bot in bots_to_use:
		bots.append(Bot(bot))

	for i in range(rounds):
		if i < len(maps):
			selected_map = maps[i % len(maps)]
		else:
			selected_map = "bad_baba_nonexistent_map"

		for i in range(nbots):
			for j in range(nbots):
				if i == j:
					continue
				bot_1 = bots[i]
				bot_2 = bots[j]

				game_result = run_match(selected_map, bot_1.name, bot_2.name, f"{replay_file_base}_{bot_1.name}_{bot_2.name}_{i}")

				if game_result["winner"] == 1:
					bot_1.update_result(did_win=True)
					bot_2.update_result(did_win=False)
					print(f"{bot_1.name} won against {bot_2.name}")
				elif game_result["winner"] == 2:
					bot_1.update_result(did_win=False)
					bot_2.update_result(did_win=True)
					print(f"{bot_2.name} won against {bot_1.name}")
				else:
					print("Unrecognized winner")
				
				for bot in bots:
					print(f"{bot.name} win rate: ", bot.win_rate() * 100)