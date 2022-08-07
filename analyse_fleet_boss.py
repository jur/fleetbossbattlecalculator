#!/usr/bin/python
from __future__ import print_function
import json
import sys
import os
import getopt
import itertools
import collections

difficulty = 4

def print_help(outfd):
	print("analyse_fleet_boss.py [options]", file=outfd)
	print("", file=outfd)
	print("Analyse fleet boss battles.", file=outfd)
	print("", file=outfd)
	print("-c [crew file]                 crew.json file (input from https://datacore.app/structured/crew.json)", file=outfd)
	print("--crewdbfile=[crew file]       crew.json file (input)", file=outfd)
	print("-b [fleet boss file]           refresh.json file (input from https://stt.disruptorbeam.com/fleet_boss_battles/refresh?desc_id=%d&client_api=19)" % (difficulty), file=outfd)
	print("-l [difficulty level]          Difficulty level", file=outfd)
	print("-d                             Print debug messages", file=outfd)
	print("-s [slot:crew name]            Remove crew from possible solutions", file=outfd)
	print("-t [slot:trait]                Remove trait from possible solutions", file=outfd)
	print("-h --help                      Print this help", file=outfd)

debug = False

def main(argv):
	#cwd = os.getcwd()
	scriptdir = os.path.dirname(os.path.realpath(__file__))
	jsondir = scriptdir
	crewdbfilename = jsondir + '/crew.json'
	fleetbossfilename = jsondir + '/refresh.json'
	global difficulty
	testedcrew = [ [], [], [], [], [], [], [] ]
	testedtraits = [ [], [], [], [], [], [], [] ]

	try:
		opts, args = getopt.getopt(argv,"hc:dl:b:s:t:",["help", "crewdbfile=", "fleetbossfile="])
	except getopt.GetoptError:
		print("Parameter wrong", file=sys.stderr)
		print_help(sys.stderr)
		sys.exit(1)

	global debug
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print_help(sys.stdout)
			sys.exit()
		elif opt == '-d':
			debug = True
		elif opt in ("-c", "--crewdbfile"):
			crewdbfilename = arg
		elif opt in ("-b", "--fleetbossfile"):
			fleetbossfilename = arg
		elif opt in ("-l"):
			difficulty = int(arg)
		elif opt in ("-s"):
			notcrewslot = arg.split(':')
			if (len(notcrewslot) > 1):
				testedcrew[int(notcrewslot[0])].append(notcrewslot[1])
			else:
				for slot in testedcrew:
					slot.append(notcrewslot[0])
		elif opt in ("-t"):
			nottraitslot = arg.split(':')
			if (len(nottraitslot) > 1):
				testedtraits[int(nottraitslot[0])].append(nottraitslot[1])
			else:
				for slot in testedtraits:
					slot.append(nottraitslot[0])
	max_rarity = 0

	if difficulty == 1:
		max_rarity = 2;
	if difficulty == 2:
		max_rarity = 3;
	if difficulty == 3:
		max_rarity = 4;
	if difficulty == 4:
		max_rarity = 4;
	if difficulty == 5:
		max_rarity = 5;
	if difficulty == 6:
		max_rarity = 5;

	with open(crewdbfilename) as f:
		crewdb = json.load(f)

	with open(fleetbossfilename) as f:
		fleetboss = json.load(f)

	if 'fleet_boss_battles_root' in fleetboss:
		fleet_boss_battles_root = fleetboss['fleet_boss_battles_root']
		if debug:
			print("Found fleet_boss_battles_root")
		if 'statuses' in fleet_boss_battles_root:
			statuses = fleet_boss_battles_root['statuses']
			if debug:
				print("Found statuses")
			for status in statuses:
				if ('difficulty_id' in status):
					if debug:
						print("difficulty_id %d" % (status['difficulty_id']))
				if ('difficulty_id' in status) and (status['difficulty_id'] == difficulty):
					if debug:
						print("Found difficulty_id %s" % (difficulty))
					if 'combo' in status:
						combo = status['combo']
						if 'traits' in combo:
							traits = combo['traits']
							print("traits %s" % (traits))
							nr = 1
							for node in combo['nodes']:
								unlocked_name = None
								usedtraits = []
								if 'unlocked_character' in node:
									unlocked_character = node['unlocked_character']
									if 'name' in unlocked_character:
										unlocked_name = unlocked_character['name']
								if 'open_traits' in node:
									open_traits = node['open_traits']
									for trait in open_traits:
										usedtraits.append(trait)
								if 'hidden_traits' in node:
									hidden_traits = node['hidden_traits']
									for trait in hidden_traits:
										usedtraits.append(trait)
										if trait in traits:
											traits.remove(trait)

								if unlocked_name:
									print("%d: %s %s" % (nr, unlocked_name, usedtraits))
								else:
									print("%d: %s" % (nr, usedtraits))
								nr = nr + 1
							print("remaining traits %s" % (traits))
							print("")

							slots = [ ]

							nr = 1
							idx = 0
							for node in combo['nodes']:
								slots.append({ "nr": nr})
								unlocked_character = None
								if 'unlocked_character' in node:
									unlocked_character = node['unlocked_character']
								if unlocked_character is None:
									print("slot %d" % (nr))
									open_traits = [ ]
									if 'open_traits' in node:
										open_traits = node['open_traits']
									if 'hidden_traits' in node:
										n = len(node['hidden_traits'])
										searchtraits = traits[:]
										for trait in open_traits:
											while trait in searchtraits:
												searchtraits.remove(trait)
										searchtraits = list(collections.OrderedDict.fromkeys(searchtraits))
										for trait in testedtraits[nr]:
											if trait in searchtraits:
												searchtraits.remove(trait)
										for combi in itertools.combinations(searchtraits, n):
											combi = open_traits + list(combi)
											foundlist = [ ]
											for crew in crewdb:
												if crew['max_rarity'] <= max_rarity:
													found = True
													for trait in combi:
														if trait not in crew['traits']:
															found = False
													if found:
														if crew['name'] in testedcrew[nr]:
															# Crew was tested, so this trait combination is not valid.
															foundlist = [ ]
															break
														else:
															foundlist.append(crew)
											if len(foundlist) > 0:
												if not "combinations" in slots[idx]:
													slots[idx]["combinations"] = [ ]
												entry = { }
												entry["foundlist"] = foundlist
												entry["combi"] = combi
												slots[idx]["combinations"].append(entry)
												print(combi)
												names = []
												for crew in foundlist:
													names.append(crew['name'])
												print(names)
												print("")
								nr = nr + 1
								idx = idx + 1

							step = 1
							reduced = False
							while reduce_slots(step, slots, traits):
								reduced = True
								step = step + 1
							if reduced:
								print_slots(slots)

def reduce_slots(step, slots, traits):
	reduced = False
	print("Reducing slots step %d:" % (step))
	for slot in slots:
		if "combinations" in slot:
			reducedcombi = None
			combinations = slot["combinations"]
			for entry in combinations:
				if "reducedcombi" in entry:
					combi = entry["reducedcombi"]
				else:
					combi = entry["combi"]
				foundlist = entry["foundlist"]

				if reducedcombi is None:
					# Assume that all traits are used by all combinations.
					reducedcombi = combi[1:]
				else:
					# remove trait which is not used by all combinations.
					removelist = [ ]
					for trait in reducedcombi:
						if not trait in combi[1:]:
							removelist.append(trait)
					for trait in removelist:
						reducedcombi.remove(trait)

			if (reducedcombi is not None) and (len(reducedcombi) > 0):
				print(reducedcombi)
				for entry in combinations:
					if "reducedcombi" in entry:
						combi = entry["reducedcombi"]
					else:
						combi = entry["combi"][:]
						entry["reducedcombi"] = combi

					for trait in reducedcombi:
						if trait in combi:
							combi.remove(trait)
				for trait in reducedcombi:
					if trait in traits:
						print("Removing trait %s" % (trait))
						traits.remove(trait)
						reduced = True
						print("")
	if reduced:
		print("remaining traits %s" % (traits))
		print("")
		remove_traits(slots, traits)
	else:
		print("None")
		print("")
	return reduced

def remove_traits(slots, traits):
	print("Removing slots:")
	for slot in slots:
		if "combinations" in slot:
			nr = slot["nr"]
			combinations = slot["combinations"]
			newcombinations = [ ]
			for entry in combinations:
				if "reducedcombi" in entry:
					combi = entry["reducedcombi"]
				else:
					combi = entry["combi"]
				found = True
				for trait in combi[1:]:
					if trait in traits:
						found = True
					else:
						found = False
				if found:
					newcombinations.append(entry)
				else:
					print("slot %d: Removing %s" % (nr, combi))
			slot["combinations"] = newcombinations
	print("")


def print_slots(slots):
	print("Result:")
	for slot in slots:
		if "combinations" in slot:
			nr = slot["nr"]
			print("slot %d" % (nr))
			combinations = slot["combinations"]
			for entry in combinations:
				combi = entry["combi"]
				foundlist = entry["foundlist"]

				print(combi)
				names = []
				for crew in foundlist:
					names.append(crew['name'])
				print(names)
				print("")

if __name__ == "__main__":
	main(sys.argv[1:])

