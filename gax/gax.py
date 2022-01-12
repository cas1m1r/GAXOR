import numpy as np, matplotlib.pyplot as plt
import multiprocessing
import itertools
import frequency
import random
import string
import utils
import time
import sys
import os

def int2key(N):
	if type(N)==int: return bytes(chr(N),'utf-8')
	else: return N

def ints2keys(nums):
	keys = []
	for N in nums:
		keys.append(b''.join([int2key(i) for i in N]))
	return keys

def key2int(k):
	return int.from_bytes(k,'big')

def score_ratios(ratios,bgrams,tgrams):
	perfect = []; diff = 0
	# for letter in ratios.keys():
	# 	try:
	# 		if chr(letter) in list(string.ascii_letters):
	# 			ideal = frequency.monogramf[chr(letter).upper()]
	# 			real = ratios[letter]
	# 			perfect.append(ideal)
	# 			diff += real - ideal
	# 	except KeyError:
	# 		# diff -= 1 # Penalize bad chars
	# 		pass

	# Alternate approach, trying to see if ETAION are most common
	top_ratios = np.array(list(ratios.values()))
	top_ratios.sort()
	top_ratios = list(top_ratios[-6:])
	for letter in ratios.keys():
		try:
			L = chr(letter).upper()
			idealf = frequency.monogramf[L]
			real = ratios[letter]
			if real in top_ratios:
				diff += (idealf - real)/real
		except:
			diff /= 2
			pass
	# TODO: Look for bigram and trigram
	for bs in bgrams.keys():
		if bgrams[bs] > 0:
			diff *= 2*bgrams[bs]
	for ts in tgrams.keys():
		if tgrams[ts] > 0:
			diff *= 3*tgrams[ts]
	return diff

def build_samples(keysize):
	population = []
	for sample in itertools.permutations(list(range(256)),keysize):
		population.append(sample)
	return population

def generate_random_samples(N,keysize):
	population = []
	pts = bytes(list(range(256)))
	while len(population) < N:
		population.append(random.sample(pts, keysize))
	return population



class GAXOR:
	# :: FROM WIKIPEDIA ::
	# The following is an example of a generic single-objective genetic algorithm:
	#
	# Step One: Generate the initial population of individuals randomly. (First generation)
	# Step Two: Repeat the following regenerational steps until termination:
	#  [1]  Evaluate the fitness of each individual in the population (time limit, sufficient fitness achieved, etc.)
	#  [2]  Select the fittest individuals for reproduction. (Parents)
	#  [3]  Breed new individuals through crossover and mutation operations to give birth to offspring.
	#  [4]  Replace the least-fit individuals of the population with new individuals.
	
	def __init__(self,cipher,sz):
		self.population_size = 15000
		self.max_generations = 10000
		self.crossover_rate = 0.25
		self.mutation_rate = 0.15
		self.ciphertext = cipher
		self.solved = False
		self.fitness = {}
		self.keysize = sz

	def build_initial_pop(self):
		# Initially try a keysize of 1
		return generate_random_samples(self.population_size, self.keysize)

	def evauate_fitness(self, group):
		fitness = {}
		for key_guess in ints2keys(group):
			attempt = utils.xor(self.ciphertext, key_guess)
			lets, rats, bi, tri = frequency.calculate_letter_frequency(attempt)
			
			score = int(score_ratios(rats, bi, tri))
			fitness[key_guess] = score
			# FOR DEBUGGING 
			if 5 > fitness[key_guess] > 0:
				print(f'\033[1m{attempt[0:10]} \t{score} \t{key_guess}\033[0m')
				# time.sleep(0.07)
			elif 100 >= len(self.ciphertext) > score >= 5:
				print(f'\033[1m\033[33m{attempt[0:18]} \t {score} \t {key_guess}\033[0m')
				# time.sleep(0.05)
			elif 1000 >= len(self.ciphertext) > fitness[key_guess] > 100:
				print(f'\033[1m\033[34m{attempt[0:18]} \t {score} \t {key_guess}\033[0m')
				# time.sleep(0.1)
			elif fitness[key_guess] > 5000:
				print(f'\033[1m\033[31m{attempt[0:18]} \t{ score} \t {key_guess}\033[0m')
				if str(input('Looks cracked? Want to continue?(y):\n')).upper() == 'N':
					print(attempt)
					exit()
			# else:
			# 	print(f'{attempt[0:10]} \t{score} \t{key_guess}')
				# time.sleep(0.01)
		return fitness

	def find_fittest(self, fit_scores):
		mean_fitness = np.array(list(fit_scores.values())).mean()
		most_fit_score = np.array(list(fit_scores.values())).max()
		parents = []
		for k in fit_scores.keys():
			if fit_scores[k]>=most_fit_score:
				parents.append(k)
			elif fit_scores[k]>=mean_fitness:
				parents.append(k)
		return parents, most_fit_score, mean_fitness

	def create_offspring(self, parents, most_fit, mean_fit, scores):
		population = []
		# if N Parents < Population_Size add some random offspring
		n_adopted = self.population_size - len(parents)
		for bits in generate_random_samples(n_adopted, self.keysize): #TODO: keysize based on mostfit instead!
			population.append(bits)
		for elder in parents:
			population.append(elder)
		# Crossover (Reproduction): Choose how to produce children from parents.
		# Mutation: Choose how to randomly mutate some children to introduce additional diversity. 
		n_mutated = 0; inherited = 0
		next_generation = []
		for individual in population:
			if individual not in parents:
				# new children were created randomly, so some should inherit from parents
				if (inherited/self.population_size) <= self.crossover_rate:
					random_parentA = random.sample(parents,1)[0:int(self.keysize/2)]
					# random_parentB = random.sample(population,1)[0:int(self.keysize/2)]
					offspring = individual
					try:
						offspring = b''.join([individual[0:int(self.keysize/2)],random_parentA])[0:self.keysize-1]
						inherited += 1
					except:
						# offspring = random_parentA[0:self.keysize]
						pass
					# 
					# random.shuffle(offspring)
				else:
					offspring = individual
				# and some need mutations
				
			else:
				if (n_mutated/self.population_size) <= self.mutation_rate:
					if  scores[individual]>=mean_fit:
						mutated = []; k = 0
						flips = random.randint(0,len(individual))
						for bit in individual:
							if k != flips:
								mutated.append(bit)
							else:
								mutated.append(os.urandom(1))
							k+=1
					else:
						random.shuffle(individual)
					n_mutated += 1
				# Some parents survive to next generation
				else:
					offspring = individual
			# finally add individual to next generation
			next_generation.append(offspring[0:self.keysize])
		print('\033[1m\033[31m *** Next Generation***\033[0m')
		return next_generation


	def evolution(self):
		generation = 0
		population = self.build_initial_pop()
		while generation < self.max_generations and not self.solved:
			# get fitness of the generation
			fitness = self.evauate_fitness(population)
			# find the most fit
			most_fit, best, mean  = self.find_fittest(fitness)
			# create new population
			population = self.create_offspring(most_fit, best, mean, fitness)
			# if best >=0:
			# 	self.solved = True
			# next generation! 
			generation += 1


# TODO: 
# 
# [1] Need to improve the crossover/mutation
#
# [2] Find set of numbers that works for all key sizes
#
# [3] Clean up the code, it's gettin spaghetti'fied

def main():
	MSG = b'The quieter you become the more you are able to hear'
	KEY = b'secret'
	ex = utils.xor(MSG,KEY)
	gaxor = GAXOR(ex, len(KEY))
	gaxor.evolution()

if __name__ == '__main__':
	main()
