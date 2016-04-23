#!coding: utf-8
from __future__ import division
import sys
import json

class CKY:
	def __init__(self):
		self.binary_emission = {}
		self.unary_emission = {}
		self.unary = {}
		self.binary = {}
		self.nonterminal = {}
		self.vocab = set()
		self.sym_vocab = set()

	def count(self, counts_file):
		f = open(counts_file, "r")
		line = f.readline()
		while line:
			l = line.strip()
			if l:
				l = l.split(" ")
				if l[1] == "NONTERMINAL":
					self.nonterminal.setdefault(l[2], 0)
					self.nonterminal[l[2]] += int(l[0])
					self.sym_vocab.add(l[2])
				elif l[1] == "BINARYRULE":
					key = (l[2], l[3], l[4])
					self.binary.setdefault(key, 0)
					self.binary[key] += int(l[0])
				elif l[1] == "UNARYRULE":
					key = (l[2], l[3])
					self.unary.setdefault(key, 0)
					self.unary[key] += int(l[0])
					self.vocab.add(l[3])
			line = f.readline()
		'''
		for sym in self.sym_vocab:
			for word in self.vocab:
				key = (sym, word)
				if not self.unary.has_key(key):
					print(key)
					self.unary.setdefault(key, 0)
					self.unary_emission.setdefault(key, 0)
		'''
	def parameter_emission(self):
		for (sym, y1, y2), count in self.binary.items():
			key = (sym, y1, y2)
			self.binary_emission.setdefault(key, 0)
			self.binary_emission[key] += (count/self.nonterminal[sym])
		for (sym, word), count in self.unary.items():
			key = (sym, word)
			self.unary_emission.setdefault(key, 0)
			self.unary_emission[key] += (count/self.nonterminal[sym])

	def get_sentence_iterator(self, data_file):
		f = open(data_file, "r")
		line = f.readline()
		while line:
			l = line.strip()
			if l:
				l = l.split(" ")
				yield l
			line = f.readline()

	def dynamic_cky(self, data_file, output_file):
		sentence_iterator = self.get_sentence_iterator(data_file)
		for sentence in sentence_iterator:
			n = len(sentence)
			pi_emission = {}
			bp_emission = {}

			for i in range(1, n+1):
				word = sentence[i - 1]
				if word not in self.vocab:
					word = '_RARE_'
				for sym in self.sym_vocab:
					key = (sym, word)
					if not self.unary_emission.has_key(key):
						pi_emission.setdefault((i, i, sym), 0)
					else:
						pi_emission[(i, i, sym)] = self.unary_emission[key]

					#print(pi_emission[(i, i, sym)])
			for l in range(1, n):
				for i in range(1, n-l+1):
					j = i + l
					for sym in self.sym_vocab:
						max_v = 0
						max_binary = tuple()
						max_s = 0
						for s in range(i, j):
							for (sym1, y1, y2), count in self.binary.items():
								if sym1 == sym:
									temp = self.binary_emission[(sym1, y1, y2)]*pi_emission[(i, s, y1)]*pi_emission[(s+1, j, y2)]
									if temp > max_v:
										max_v = temp
										max_binary = (sym1, y1, y2)
										max_s = s
						pi_emission[(i, j, sym)] = max_v
						bp_emission[(i, j, sym)] = (max_binary, max_s)
						#print(max_binary)
			tree = []
			i, j, sym = 1, n, 'SBARQ'
			self.parse_tree(bp_emission, tree, i, j, sym, sentence)
			#print tree
			out = open(output_file, "a+")
			#out.write(str(tree))
			self.output(tree, out)
			out.write('\n')
			#print("done")

	def parse_tree(self, bp_emission, tree, i, j, sym, sentence):
		if i == j:
			tree.append(sym)
			tree.append(sentence[i - 1])
			return
		tree.append(sym)
		(max_binary, max_s) = bp_emission[(i, j, sym)]
		#print(max_binary)
		#sym1 = max_binary[0] #sym1 = sym
		y1 = max_binary[1]
		tree.append([])
		y2 = max_binary[2]
		tree.append([])
		self.parse_tree(bp_emission, tree[1], i, max_s, y1, sentence)
		self.parse_tree(bp_emission, tree[2], max_s + 1, j, y2, sentence)

	def output(self, tree, output_file):
		out = output_file
		out.write("[\"")
		if len(tree) == 2:
			out.write(tree[0]+"\", "+"\""+tree[1]+"\"]")
		elif len(tree) == 3:
			out.write(tree[0]+"\",")
			self.output(tree[1], output_file)
			out.write(", ")
			self.output(tree[2], output_file)
			out.write("]")

def main(counts_file, data_file, output_file):
	cky = CKY()
	cky.count(counts_file)
	cky.parameter_emission()
	cky.dynamic_cky(data_file, output_file)

if __name__ == '__main__':
	counts_file = sys.argv[1]
	data_file = sys.argv[2]
	output_file = sys.argv[3]
	main(counts_file, data_file, output_file)



			





