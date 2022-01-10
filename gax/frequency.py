#!/usr/bin/env python3
import os, sys, time, string, itertools
import numpy as np

letters = list(string.ascii_letters)
special = list(string.digits + string.punctuation)
counts = dict(zip(letters,list(np.zeros((1,len(letters))).flatten())))

monogramf = {
	'A' :  8.55,        'K' :  0.81,        'U' :  2.68,
	'B' :  1.60,        'L' :  4.21,        'V' :  1.06,
	'C' :  3.16,        'M' :  2.53,        'W' :  1.83,
	'D' :  3.87,        'N' :  7.17,        'X' :  0.19,
	'E' : 12.10,        'O' :  7.47,        'Y' :  1.72,
	'F' :  2.18,        'P' :  2.07,        'Z' :  0.11,        
	'H' :  4.96,        'R' :  6.33,                 
	'I' :  7.33,       'S' :  6.73,                 
	'J' :  0.22,        'T' :  8.94 
}

common_words = {
	      'THE' :  6.42,            'ON' :  0.78,           'ARE' :  0.47,
	       'OF' :  2.76,          'WITH' :  0.75,          'THIS' :  0.42,
	      'AND' :  2.75,            'HE' :  0.75,             'I' :  0.41,
	       'TO' :  2.67,            'IT' :  0.74,           'BUT' :  0.40,
	        'A' :  2.43,           'AS' :  0.71,          'HAVE' :  0.39,
	       'IN' :  2.31,            'AT' :  0.58,            'AN' :  0.37,
	       'IS' :  1.12,           'HIS' :  0.55,           'HAS' :  0.35,
	      'FOR' :  1.01,            'BY' :  0.51,           'NOT' :  0.34,
	     'THAT' :  0.92,            'BE' :  0.48,          'THEY' :  0.33,
	      'WAS' :  0.88,          'FROM' :  0.47,            'OR' :  0.30,
}

bigramf = {
	'TH' :  2.71,        'EN' :  1.13,        'NG' :  0.89,
	'HE' :  2.33,        'AT' :  1.12,        'AL' :  0.88,
	'IN' :  2.03,        'ED' :  1.08,        'IT' :  0.88,
	'ER' :  1.78,        'ND' :  1.07,        'AS' :  0.87,
	'AN' :  1.61,        'TO' :  1.07,        'IS' :  0.86,
	'RE' :  1.41,        'OR' :  1.06,        'HA' :  0.83,
	'ES' :  1.32,        'EA' :  1.00,        'ET' :  0.76,
	'ON' :  1.32,        'TI' :  0.99,        'SE' :  0.73,
	'ST' :  1.25,        'AR' :  0.98,        'OU' :  0.72,
	'NT' :  1.17,        'TE' :  0.98,        'OF' :  0.71
}

trigramf = {
	'THE' :  1.81,        'ERE' :  0.31,        'HES' :  0.24,
	'AND' :  0.73,        'TIO' :  0.31,        'VER' :  0.24,
	'ING' :  0.72,        'TER' :  0.30,        'HIS' :  0.24,
	'ENT ':  0.42,        'EST' :  0.28,        'OFT' :  0.22,
	'ION' :  0.42,        'ERS' :  0.28,        'ITH' :  0.21,
	'HER' :  0.36,        'ATI' :  0.26,        'FTH' :  0.21,
	'FOR' :  0.34,        'HAT' :  0.26,        'STH' :  0.21,
	'THA' :  0.33,        'ATE' :  0.25,        'OTH' :  0.21,
	'NTH' :  0.33,        'ALL' :  0.25,        'RES' :  0.21,
	'INT' :  0.32,        'ETH' :  0.24,        'ONT' :  0.20
}

def calculate_letter_frequency(text):
	printable = list(bytes(text))
	counts = np.zeros((1,len(list(string.printable)))).flatten()
	bigrams = dict(zip(list(bigramf.keys()), list(counts)))
	trigrams = dict(zip(list(trigramf.keys()), list(counts)))
	items = dict(zip(printable,list(counts)))
	badchars = 0
	# print('[+] Analyzing Text \t\t[%d characters]' % len(text))
	for element in list(text):
		try:
			items[element] += 1
		except:
			badchars += 1
			pass
	# print('[+] Bad Characters in text \t[%d]' % badchars)
	# recalculate these as percentages instead of counts? 
	N = len(list(text))
	fracs = np.zeros((1,len(list(string.printable)))).flatten()
	ratios = dict(zip(printable,fracs))
	for diagram in printable:
		ratios[diagram] = 100. * (items[diagram]/N)
	
	# Now Look for bigrams 
	i = 0
	for i in list(range(0,len(text))):
		if i>0 and i%2==0:
			try:
				bi = text[i-2:i].decode().upper()
				if bi in list(bigramf.keys()):
					bigrams[bi] += 1
			except:
				pass
		i += 1
	# Now Look for trigrams
	j = 0
	for j in list(range(0,len(text))):
		if j>0 and j%3==0:
			try:
				tri = text[j-3:j].decode().upper()
				if tri in list(trigramf.keys()):
					trigrams[tri] += 1
			except:
				pass

	return items, ratios, bigrams, trigrams

def display_counts(d):
	print('')
	print('\033[3m\t\tLetter Frequencies:\033[0m')
	printout = ''; ii = 1
	for k in d.keys():
		if k in letters:
			if d[k] > 5:
				printout += '\033[1m'
			printout += '%s: %f\t' % (k, d[k])
			if d[k] > 5:
				printout += '\033[0m'
			ii += 1
		if ii % 5 == 0:
			printout += '\n'
			ii = 1
	print(printout)	

def analyze_text(text):
	counts, ratios = calculate_letter_frequency(text.decode('utf-8'))
	top_letters = ['E','T','A','O','I','N']
	opmap = {
		'E' : ratios['e'] + ratios['E'],
		'T' : ratios['t'] + ratios['T'],
		'A' : ratios['a'] + ratios['A'],
		'I' : ratios['i'] + ratios['O'],
		'O' : ratios['o'] + ratios['I'],
		'N' : ratios['n'] + ratios['N']	
	}
	text_rats = dict(zip( list(opmap.values()),top_letters))
	for char in top_letters:
		text_rats[opmap[char]] = char
	# Now compare relative ratios of expected distribution and action
	most_freq = list(text_rats.values())
	most_freq.sort(reverse=True)
	top_seen = []
	frequencies = dict(zip(most_freq, list(text_rats.keys())))
	for element in most_freq:
		top_seen.append(text_rats[frequencies[element]])
	# meanf = np.array(list(ratios.values())).mean()
	seemsEnglish = False
	try:
		seemsEnglish = seemsEnglish or frequencies['I'] >= monogramf['I']
		seemsEnglish = seemsEnglish or frequencies['O'] >= monogramf['O']
		seemsEnglish = seemsEnglish or frequencies['N'] >= monogramf['N']
		seemsEnglish =  seemsEnglish or frequencies['E'] >= monogramf['E']
		seemsEnglish = seemsEnglish or frequencies['A'] >= monogramf['A']
		seemsEnglish = seemsEnglish or frequencies['T'] >= monogramf['T']
	except KeyError:
		pass
	return top_seen, frequencies, seemsEnglish




def main():
	if len(sys.argv) < 2:
		print('[+] Analyzing test file example.txt')
		text = open('example.txt','r').read()
		
	if(len(sys.argv) > 1):
		print('[+] Attempting to Analyze %s' % sys.argv[1])
		text = open(sys.argv[1],'r').read()

	counts, frequencies = calculate_letter_frequency(text)
	display_counts(frequencies)

	most_used, frequencies, appearsEnglish = analyze_text(text)
	if appearsEnglish:
		print('[+] Input Text Seems English')

if __name__ == '__main__':
	main()
